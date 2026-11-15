"""Tests for the trend watch scripts (watch_collect.py, watch_issue.py) — no network."""
import datetime
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import watch_collect as wc  # noqa: E402
import watch_issue as wi  # noqa: E402

RSS = b"""<?xml version="1.0"?><rss version="2.0"><channel>
<item><title>Power BI May 2026 Feature Summary</title>
<link>https://powerbi.microsoft.com/en-US/blog/power-bi-may-2026-feature-summary/</link>
<pubDate>Tue, 12 May 2026 08:00:00 +0000</pubDate>
<description>&lt;p&gt;Welcome &amp;amp; enjoy.&lt;/p&gt;</description></item>
<item><title>Old post</title><link>https://powerbi.microsoft.com/en-US/blog/old/</link>
<pubDate>Mon, 05 Jan 2026 08:00:00 +0000</pubDate></item>
<item><title>No date</title><link>https://powerbi.microsoft.com/en-US/blog/nodate/</link></item>
</channel></rss>"""

ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>Community take</title><link rel="alternate" href="https://example.com/post"/>
<updated>2026-05-20T10:00:00.123Z</updated><summary>Opinion</summary></entry></feed>"""

CONFIG = {
    "primary_domains": ["powerbi.microsoft.com", "learn.microsoft.com", "community.fabric.microsoft.com/t5/Fabric-Updates-Blog/"],
    "sources": [
        {"name": "Power BI blog", "urls": ["https://bad.invalid/feed", "https://powerbi.microsoft.com/en-us/blog/feed/"]},
        {"name": "Community", "urls": ["https://example.com/atom"]},
    ],
}


def fake_fetch(url):
    return {"https://powerbi.microsoft.com/en-us/blog/feed/": RSS, "https://example.com/atom": ATOM}[url]


class Collect(unittest.TestCase):
    def test_parse_rss_and_atom(self):
        rss = wc.parse_feed(RSS)
        self.assertEqual(len(rss), 3)
        self.assertEqual(rss[0]["title"], "Power BI May 2026 Feature Summary")
        atom = wc.parse_feed(ATOM)
        self.assertEqual(atom[0]["link"], "https://example.com/post")

    def test_dates(self):
        self.assertEqual(wc.parse_date("Tue, 12 May 2026 08:00:00 +0000").strftime("%Y-%m-%d"), "2026-05-12")
        self.assertEqual(wc.parse_date("2026-05-20T10:00:00.123Z").strftime("%Y-%m-%d"), "2026-05-20")
        self.assertIsNone(wc.parse_date("not a date"))

    def test_clean_text_strips_markup_and_control_characters(self):
        self.assertEqual(wc.clean_text("<p>Welcome &amp; enjoy.\x07</p>", 100), "Welcome & enjoy.")
        self.assertLessEqual(len(wc.clean_text("x" * 1000, 50)), 50)

    def test_locale_variants_are_the_same_post(self):
        a = wc.normalize_link("https://blog.fabric.microsoft.com/en-US/blog/post-x/")
        b = wc.normalize_link("https://blog.fabric.microsoft.com/en-NZ/blog/post-x")
        self.assertEqual(a, b)

    def test_primary_domain_check(self):
        self.assertTrue(wc.is_primary("https://powerbi.microsoft.com/x", ["powerbi.microsoft.com"]))
        self.assertFalse(wc.is_primary("https://evilmicrosoft.com/x", ["microsoft.com"]))
        self.assertFalse(wc.is_primary("https://example.com/microsoft.com", ["microsoft.com"]))
        forum = ["community.fabric.microsoft.com/t5/Fabric-Updates-Blog/"]
        self.assertTrue(wc.is_primary("https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/a/ba-p/1", forum))
        self.assertFalse(wc.is_primary("https://community.fabric.microsoft.com/t5/Desktop/a/m-p/1", forum))

    def test_collect_filters_falls_back_and_flags(self):
        result = wc.collect(CONFIG, datetime.date(2026, 5, 1), fetcher=fake_fetch,
                            now=datetime.datetime(2026, 6, 1, tzinfo=datetime.timezone.utc))
        self.assertEqual([i["title"] for i in result["items"]], ["Community take", "Power BI May 2026 Feature Summary"])
        self.assertTrue(result["items"][1]["primary"])
        self.assertFalse(result["items"][0]["primary"])
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["sources"][0]["url"], "https://powerbi.microsoft.com/en-us/blog/feed/")

    def test_collect_reports_a_dead_source(self):
        def broken(url):
            raise OSError("down")
        result = wc.collect(CONFIG, datetime.date(2026, 5, 1), fetcher=broken)
        self.assertEqual(len(result["errors"]), 2)
        self.assertEqual(result["items"], [])


class Issue(unittest.TestCase):
    def collected(self):
        return wc.collect(CONFIG, datetime.date(2026, 5, 1), fetcher=fake_fetch,
                          now=datetime.datetime(2026, 6, 1, tzinfo=datetime.timezone.utc))

    def row(self, **kw):
        base = {"change": "Thing | with pipe", "status": "ga",
                "source": "https://powerbi.microsoft.com/en-US/blog/power-bi-may-2026-feature-summary/",
                "skill": "powerbi-conventions", "action": "Update rule", "priority": "high"}
        base.update(kw)
        return base

    def test_malformed_reports_are_rejected(self):
        for bad in ({}, {"rows": [{"status": "ga"}]}, {"rows": [self.row(status="shipped")]},
                    {"rows": [self.row(priority="urgent")]}):
            with self.assertRaises(wi.ReportError):
                wi.validate_report(bad)

    def test_pipes_cannot_break_the_table(self):
        rows, _ = wi.validate_report({"rows": [self.row()]})
        self.assertNotIn("|", rows[0]["change"])

    def test_source_outside_the_collected_set_is_downgraded(self):
        rows, _ = wi.validate_report({"rows": [self.row(source="https://learn.microsoft.com/made-up")]})
        rows = wi.enforce_sources(rows, self.collected())
        self.assertEqual(rows[0]["status"], "unconfirmed")

    def test_non_primary_source_is_downgraded(self):
        rows, _ = wi.validate_report({"rows": [self.row(source="https://example.com/post")]})
        rows = wi.enforce_sources(rows, self.collected())
        self.assertEqual(rows[0]["status"], "unconfirmed")

    def test_primary_collected_source_stays_confirmed(self):
        rows, _ = wi.validate_report({"rows": [self.row(source="https://powerbi.microsoft.com/en-NZ/blog/power-bi-may-2026-feature-summary")]})
        rows = wi.enforce_sources(rows, self.collected())
        self.assertEqual(rows[0]["status"], "ga")

    def test_known_links_ignore_locale(self):
        known = wi.known_links("see <https://powerbi.microsoft.com/en-US/blog/x/> in a past issue")
        self.assertIn(wc.normalize_link("https://powerbi.microsoft.com/en-NZ/blog/x"), known)

    def test_render_orders_by_priority_and_separates_unconfirmed(self):
        rows, props = wi.validate_report({
            "rows": [self.row(priority="low", change="Low one"), self.row(priority="high", change="High one"),
                     self.row(status="unconfirmed", change="Rumour")],
            "proposals": [{"title": "T", "brief": "B"}] * 5, "not_confirmed": ["GA date of X"]})
        text = wi.render(rows, props, self.collected(), {"not_confirmed": ["GA date of X"]})
        self.assertLess(text.index("High one"), text.index("Low one"))
        self.assertLess(text.index("Low one"), text.index("Not confirmed"))
        self.assertEqual(text.count("### T"), wi.MAX_PROPOSALS)
        self.assertIn("GA date of X", text)


if __name__ == "__main__":
    unittest.main()
