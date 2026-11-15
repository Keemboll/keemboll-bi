#!/usr/bin/env python3
"""Turn the trend-scout report (report.json) into a GitHub issue body (standard library only, Python 3.8+).

Second stage of the monthly trend watch. The agent proposes; this script enforces the rules in code:
- a row is only "confirmed" (preview, GA, retired, announced) if its source is a collected item on a primary domain,
  otherwise it is downgraded to "unconfirmed";
- a row whose source already appears in an existing watch issue is dropped (no repeated proposals);
- at most three skill proposals; every text field is flattened so it cannot break the table.

Usage: python scripts/watch_issue.py --report report.json --collected collected.json --known known.txt --out body.md
Writes `rows=<n>` and `title=<...>` to $GITHUB_OUTPUT when set. Exit code 2 if the report is malformed.
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import read_text, utf8_console, write_text  # noqa: E402
from watch_collect import is_primary, normalize_link  # noqa: E402

CONFIRMED = ("retired", "ga", "preview", "announced")
STATUSES = CONFIRMED + ("unconfirmed",)
PRIORITIES = ("high", "medium", "low")
MAX_PROPOSALS = 3
_URL = re.compile(r"https?://[^\s)>\]|]+")


class ReportError(ValueError):
    pass


def flat(value, limit=300):
    """One line, no table-breaking characters."""
    text = re.sub(r"\s+", " ", str(value or "")).strip().replace("|", "/")
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def known_links(text):
    return {normalize_link(u) for u in _URL.findall(text or "")}


def validate_report(report):
    if not isinstance(report, dict) or not isinstance(report.get("rows"), list):
        raise ReportError('report must be an object with a "rows" list')
    rows = []
    for n, row in enumerate(report["rows"], 1):
        if not isinstance(row, dict):
            raise ReportError("row %d is not an object" % n)
        status = str(row.get("status", "")).strip().lower()
        priority = str(row.get("priority", "")).strip().lower()
        if status not in STATUSES:
            raise ReportError("row %d: status %r not in %s" % (n, status, ", ".join(STATUSES)))
        if priority not in PRIORITIES:
            raise ReportError("row %d: priority %r not in %s" % (n, priority, ", ".join(PRIORITIES)))
        for key in ("change", "source", "action"):
            if not str(row.get(key, "")).strip():
                raise ReportError("row %d: %r is empty" % (n, key))
        rows.append({
            "change": flat(row["change"]),
            "status": status,
            "source": str(row["source"]).strip(),
            "skill": flat(row.get("skill") or "gap"),
            "action": flat(row["action"]),
            "priority": priority,
        })
    proposals = []
    for p in (report.get("proposals") or [])[:MAX_PROPOSALS]:
        if isinstance(p, dict) and str(p.get("title", "")).strip():
            proposals.append({"title": flat(p["title"], 120), "brief": str(p.get("brief", "")).strip()[:1200]})
    return rows, proposals


def enforce_sources(rows, collected):
    """Downgrade to unconfirmed any row not backed by a collected item on a primary domain."""
    domains = collected.get("primary_domains", [])
    by_link = {normalize_link(i["link"]): i for i in collected.get("items", [])}
    for row in rows:
        item = by_link.get(normalize_link(row["source"]))
        reason = None
        if item is None:
            reason = "source not in the collected set"
        elif not (item.get("primary") and is_primary(row["source"], domains)):
            reason = "source is not a primary Microsoft page"
        if reason and row["status"] != "unconfirmed":
            row["status"] = "unconfirmed"
            row["action"] = "%s (%s)" % (row["action"], reason)
    return rows


def render(rows, proposals, collected, report):
    order = {p: i for i, p in enumerate(PRIORITIES)}
    confirmed = sorted((r for r in rows if r["status"] != "unconfirmed"), key=lambda r: order[r["priority"]])
    unconfirmed = [r for r in rows if r["status"] == "unconfirmed"]
    out = ["Period: %s → %s. Sources read: %s." % (
        collected.get("since", "?"), collected.get("generated", "?"),
        ", ".join(s["name"] for s in collected.get("sources", [])) or "none")]
    if collected.get("errors"):
        out += ["", "> Feeds that failed this run: " + "; ".join(collected["errors"])]

    def table(items):
        lines = ["| Change | Status | Source | Skill / gap | Proposed action | Priority |", "|---|---|---|---|---|---|"]
        for r in items:
            lines.append("| %s | %s | <%s> | %s | %s | %s |" % (
                r["change"], r["status"], r["source"], r["skill"], r["action"], r["priority"]))
        return lines

    out += ["", "## Confirmed on a primary source", ""]
    out += table(confirmed) if confirmed else ["Nothing new."]
    if unconfirmed:
        out += ["", "## Not confirmed — do not assert in a skill", ""] + table(unconfirmed)
    if proposals:
        out += ["", "## Proposals ready for `skill-author`"]
        for p in proposals:
            out += ["", "### " + p["title"], "", p["brief"]]
    missing = [flat(x, 200) for x in (report.get("not_confirmed") or []) if str(x).strip()]
    if missing:
        out += ["", "## What the agent could not confirm", ""] + ["- " + m for m in missing]
    out += ["", "---", "Generated by the monthly trend watch (`scripts/watch_collect.py`, `trend-scout`, "
            "`scripts/watch_issue.py`). Nothing was changed in the repository: review each row, then implement what you keep."]
    return "\n".join(out) + "\n"


def main():
    utf8_console()
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--report", required=True)
    parser.add_argument("--collected", required=True)
    parser.add_argument("--known", help="text file: bodies of existing watch issues (to drop repeated rows)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    collected = json.loads(read_text(args.collected))
    try:
        report = json.loads(read_text(args.report))
        rows, proposals = validate_report(report)
    except (ValueError, OSError) as exc:  # json.JSONDecodeError is a ValueError
        print("error: malformed report: %s" % exc, file=sys.stderr)
        return 2
    rows = enforce_sources(rows, collected)
    known = known_links(read_text(args.known)) if args.known and os.path.isfile(args.known) else set()
    rows = [r for r in rows if normalize_link(r["source"]) not in known]
    write_text(args.out, render(rows, proposals, collected, report))
    title = "Trend watch — %s" % collected.get("generated", "")[:7]
    count = len(rows) + len(proposals)
    print("%d row(s), %d proposal(s) -> %s" % (len(rows), len(proposals), args.out))
    if os.environ.get("GITHUB_OUTPUT"):
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf-8") as f:
            f.write("rows=%d\ntitle=%s\n" % (count, title))
    return 0


if __name__ == "__main__":
    sys.exit(main())
