#!/usr/bin/env python3
"""Collect recent items from the feeds listed in watch/sources.json (standard library only, Python 3.8+).

First stage of the monthly trend watch (.github/workflows/trend-watch.yml). It does the deterministic part:
fetch, parse, filter by date, deduplicate, flag primary sources. The result (collected.json) is the only thing
the trend-scout agent reads: the agent itself has no network access.

Usage: python scripts/watch_collect.py --since 2026-10-01 --out collected.json
Exit code: 0 even if some feeds failed (they are listed under "errors"); 1 if every source failed.
"""
import argparse
import datetime
import html
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from urllib.parse import urlparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, read_text, utf8_console, write_text  # noqa: E402

DEFAULT_SOURCES = os.path.join(ROOT, "watch", "sources.json")
USER_AGENT = "keemboll-bi-trend-watch (+https://github.com/Keemboll/keemboll-bi)"
MAX_BYTES = 5_000_000
SUMMARY_CHARS = 500
TITLE_CHARS = 200

_LOCALE_BLOG = re.compile(r"^(https?://[^/]+)/[a-z]{2}(?:-[a-z]{2,4})?/blog/", re.I)
_TAGS = re.compile(r"<[^>]+>")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def clean_text(value, limit):
    """Plain text from feed markup: no tags, no control characters, collapsed spaces, truncated."""
    text = html.unescape(_TAGS.sub(" ", html.unescape(value or "")))
    text = _CONTROL.sub("", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def normalize_link(url):
    """Same post, different locale feed (/en-US/blog/ vs /en-NZ/blog/) -> same key."""
    url = (url or "").strip().split("#")[0]
    url = _LOCALE_BLOG.sub(r"\1/blog/", url)
    return url.rstrip("/").lower()


def is_primary(url, prefixes):
    """True if the URL is on one of the listed hosts, optionally limited to a path prefix ("host/path/")."""
    parsed = urlparse(url)
    target = ((parsed.hostname or "") + parsed.path).lower()
    for prefix in prefixes:
        host, _, path = prefix.lower().partition("/")
        if (parsed.hostname or "").lower() == host and target.startswith(host + "/" + path):
            return True
    return False


def parse_date(value):
    """RFC 822 (RSS) or ISO 8601 (Atom) -> aware UTC datetime, or None."""
    value = (value or "").strip()
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        dt = None
    if dt is None:
        iso = re.sub(r"\.\d+", "", value.replace("Z", "+00:00"))
        try:
            dt = datetime.datetime.fromisoformat(iso)
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt.astimezone(datetime.timezone.utc)


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _child_text(node, *names):
    for child in node:
        if _local(child.tag) in names and (child.text or "").strip():
            return child.text
    return ""


def parse_feed(xml_bytes):
    """RSS 2.0 or Atom -> list of dicts {title, link, published, summary} (raw, not yet cleaned)."""
    root = ET.fromstring(xml_bytes)
    items = []
    for node in root.iter():
        kind = _local(node.tag)
        if kind not in ("item", "entry"):
            continue
        link = ""
        if kind == "item":
            link = _child_text(node, "link")
        else:
            for child in node:
                if _local(child.tag) == "link" and child.get("rel", "alternate") == "alternate":
                    link = child.get("href", "")
                    break
        items.append({
            "title": _child_text(node, "title"),
            "link": link.strip(),
            "published": _child_text(node, "pubDate", "published", "updated", "date"),
            "summary": _child_text(node, "description", "summary", "encoded", "content"),
        })
    return items


def fetch(url):
    if not url.lower().startswith("https://"):
        raise ValueError("only https URLs are fetched: " + url)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(MAX_BYTES)


def collect(config, since, fetcher=fetch, now=None):
    """Fetch every source, keep items published on/after `since` (a date), deduplicate, flag primary sources."""
    domains = config.get("primary_domains", [])
    since_dt = datetime.datetime.combine(since, datetime.time.min, tzinfo=datetime.timezone.utc)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    seen, items, sources, errors = set(), [], [], []
    for source in config["sources"]:
        last_error = "no url configured"
        for url in source["urls"]:
            try:
                parsed = parse_feed(fetcher(url))
            except Exception as exc:  # network, TLS, XML: record and try the next url
                last_error = "%s: %s" % (url, exc)
                continue
            kept = 0
            for raw in parsed:
                published = parse_date(raw["published"])
                key = normalize_link(raw["link"])
                if not key or published is None or published < since_dt or key in seen:
                    continue
                seen.add(key)
                kept += 1
                items.append({
                    "source": source["name"],
                    "title": clean_text(raw["title"], TITLE_CHARS),
                    "link": raw["link"],
                    "published": published.strftime("%Y-%m-%d"),
                    "summary": clean_text(raw["summary"], SUMMARY_CHARS),
                    "primary": is_primary(raw["link"], domains),
                })
            sources.append({"name": source["name"], "url": url, "items": kept})
            break
        else:
            errors.append("%s — %s" % (source["name"], last_error))
    items.sort(key=lambda i: i["published"], reverse=True)
    return {
        "since": since.isoformat(),
        "generated": now.strftime("%Y-%m-%d"),
        "primary_domains": domains,
        "sources": sources,
        "errors": errors,
        "items": items[: config.get("max_items", 60)],
    }


def main():
    utf8_console()
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--since", required=True, help="YYYY-MM-DD: keep items published on or after this date")
    parser.add_argument("--out", required=True, help="where to write collected.json")
    parser.add_argument("--sources", default=DEFAULT_SOURCES)
    args = parser.parse_args()
    config = json.loads(read_text(args.sources))
    result = collect(config, datetime.date.fromisoformat(args.since))
    write_text(args.out, json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("%d item(s) since %s from %d source(s); %d error(s)" % (
        len(result["items"]), args.since, len(result["sources"]), len(result["errors"])))
    for error in result["errors"]:
        print("  warning:", error, file=sys.stderr)
    return 1 if not result["sources"] else 0


if __name__ == "__main__":
    sys.exit(main())
