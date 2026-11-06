#!/usr/bin/env python3
"""Build docs/feed.xml (podcast RSS) from docs/episodes.json.

docs/episodes.json is a list of episode records appended by the workflow, each with:
  episode, air_date, title, url, bytes, duration_s, description, notes_url
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

OWNER, REPO = "Zhuyin21", "alex-y-chino-news"
SITE = f"https://{OWNER.lower()}.github.io/{REPO}"
SHOW_TITLE = "Alex y Chino"
SHOW_DESC = ("Daily Spanglish news podcast. Dr. Alex y Chino break down local "
             "(Albuquerque/Bernalillo), US, and world news. AI-generated from sourced scripts.")


def rfc822(air_date: str) -> str:
    # Publish at 6:00 am Mountain (13:00 UTC, standard time) on the air date.
    d = datetime.strptime(air_date, "%Y-%m-%d").replace(hour=13, tzinfo=timezone.utc)
    return format_datetime(d)


def main() -> int:
    docs = Path("docs")
    episodes = json.loads((docs / "episodes.json").read_text()) if (docs / "episodes.json").exists() else []
    episodes.sort(key=lambda e: e["air_date"], reverse=True)

    items = []
    for e in episodes:
        mins, secs = divmod(int(e["duration_s"]), 60)
        items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <description>{escape(e.get('description', ''))}</description>
      <link>{escape(e.get('notes_url', SITE))}</link>
      <guid isPermaLink="false">alex-y-chino-{e['episode']}-{e['air_date']}</guid>
      <pubDate>{rfc822(e['air_date'])}</pubDate>
      <enclosure url="{escape(e['url'])}" length="{e['bytes']}" type="audio/mpeg"/>
      <itunes:duration>{mins}:{secs:02d}</itunes:duration>
      <itunes:explicit>true</itunes:explicit>
    </item>""")

    now = format_datetime(datetime.now(timezone.utc))
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{SHOW_TITLE}</title>
    <link>https://github.com/{OWNER}/{REPO}</link>
    <atom:link href="{SITE}/feed.xml" rel="self" type="application/rss+xml"/>
    <description>{escape(SHOW_DESC)}</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
    <itunes:author>Alex y Chino</itunes:author>
    <itunes:explicit>true</itunes:explicit>
    <itunes:category text="News"/>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (docs / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"feed.xml: {len(items)} episodes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
