#!/usr/bin/env python3
"""Build docs/feed.xml (podcast RSS) from docs/episodes.json.

docs/episodes.json is a list of episode records appended by the workflow, each with:
  episode, air_date, title, url, bytes, duration_s, description, notes_url
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

OWNER, REPO = "Zhuyin21", "alex-y-chino-news"
SITE = f"https://{OWNER.lower()}.github.io/{REPO}"
SHOW_TITLE = "Alex y Chino"
# When AUDIO_BASE is set (the Pages deploy job), enclosures point at audio served by GitHub Pages
# (real audio/mpeg with byte-range support, which Apple Podcasts requires) instead of GitHub Releases.
AUDIO_BASE = os.environ.get("AUDIO_BASE", "").rstrip("/")
MAX_ITEMS = int(os.environ.get("FEED_MAX_ITEMS") or "30")
SHOW_DESC = ("Show hecho con IA: los guiones los escribe IA a partir de fuentes reales y las voces "
             "son sintéticas (Doc, Chino, Ashley y Sophie son personajes de IA). "
             "Podcast diario en Spanglish, de lunes a sábado: las noticias de Nuevo México, "
             "Estados Unidos y el mundo, más el segmento del día. Referencias en cada episodio. "
             "Made with AI: AI-written scripts based on real sources, and synthetic voices.")
# First line of every episode's notes (Apple Podcasts guideline 1.11: AI-generated audio
# must be disclosed in each episode's content and metadata).
AI_NOTICE = ("🤖 Episodio hecho con IA: guion escrito por IA a partir de fuentes reales y voces "
             "sintéticas. Las referencias están abajo. / Made with AI: AI-written script, synthetic voices.")


APPLE_DESC_LIMIT = 4000  # Apple Podcasts: <description> max 4,000 characters
URL_RE = re.compile(r"(?<!\]\()(?<![<\"'=])\b(https?://[^\s<>]+?)([.,;:)]*)(?=\s|$)")


def show_notes_md(stem: str) -> str:
    """The '# SHOW NOTES' section of episodes/<stem>.md (everything below that heading)."""
    path = Path("episodes") / f"{stem}.md"
    if not stem or not path.exists():
        return ""
    md = path.read_text(encoding="utf-8")
    m = re.search(r"^#\s+SHOW NOTES.*$", md, flags=re.M | re.I)
    return md[m.end():].strip() if m else ""


SKIP_SECTIONS = re.compile(r"editor|log|bit[aá]cora", re.I)


def inline_html(text: str) -> str:
    """Escape, then *italic* -> <em>, drop ** bold markers, and link bare URLs."""
    text = escape(text).replace("**", "")
    text = re.sub(r"(?<![\w*])\*([^*]+?)\*(?![\w*])", r"<em>\1</em>", text)
    return URL_RE.sub(lambda m: f'<a href="{m.group(1)}">{m.group(1)}</a>{m.group(2)}', text)


def references(md: str) -> list[tuple[str, list[str]]]:
    """[(section, ["[1] Author, \"Title,\" Outlet, date. URL", ...]), ...] from the show notes.

    Only the numbered references are kept: no sourcing rules, flags, discrepancy notes or
    editor's log. Each reference appears once, under the first section that defines it.
    """
    out: list[tuple[str, list[str]]] = []
    seen: set[str] = set()
    for block in re.split(r"^##\s+", md, flags=re.M)[1:]:
        heading, _, body = block.partition("\n")
        heading = heading.replace("**", "").strip()
        if SKIP_SECTIONS.search(heading):
            continue
        # Drop italic note lines (*Discrepancy:*, *Note:*, *Single-source items...*).
        lines = [ln.strip() for ln in body.splitlines() if not ln.strip().startswith("*") or ln.strip().startswith("**")]
        refs = []
        pieces = [pc for ln in lines for pc in re.split(r"(?=\[\d+\]\s)", ln)]  # line by line
        for piece in pieces:
            m = re.match(r"\[(\d+)\]\s+(.*)", piece.strip())
            if not m or m.group(1) in seen:
                continue
            ref = m.group(2).strip(" ·,;")
            # Drop what follows the last link on the line (" · [2]", " · Next label:", notes).
            segs = ref.split(" · ")
            last = max((i for i, sg in enumerate(segs) if re.search(r"https?://|doi:", sg)), default=len(segs) - 1)
            ref = " · ".join(segs[: last + 1]).strip(" ·,;")
            if not re.search(r"https?://|doi:", ref) or len(ref) < 20:
                continue  # a re-cite like "[2]" or "[5], [6]", not a definition
            # Trim trailing annotations in parentheses that carry no link.
            while True:
                t = re.sub(r"\s*\((?:(?!https?://)[^()])*\)\s*$", "", ref)
                if t == ref:
                    break
                ref = t.strip(" ·,;")
            seen.add(m.group(1))
            refs.append(f"[{m.group(1)}] {ref}")
        if refs:
            out.append((heading, refs))
    return out


def episode_notes(e: dict) -> tuple[str, str]:
    """(description, content_html) for one episode."""
    summary = e.get("description", "")
    notes_url = e.get("notes_url", SITE)
    notes_md = show_notes_md(e.get("stem", ""))
    parts = [f"<p>{escape(AI_NOTICE)}</p>"]
    if summary:
        parts.append(f"<p>{escape(summary)}</p>")
    refs = references(notes_md) if notes_md else []
    if refs:
        parts.append("<p><strong>Referencias</strong></p>")
        for heading, items in refs:
            parts.append(f"<p><strong>{inline_html(heading)}</strong><br>" + "<br>".join(inline_html(r) for r in items) + "</p>")
    parts.append(f'<p>Notas completas y guion: <a href="{escape(notes_url)}">{escape(notes_url)}</a></p>')
    content = "\n".join(parts)
    # <description>: the full notes when they fit Apple's limit, otherwise summary + link.
    if len(content) <= APPLE_DESC_LIMIT:
        desc = content
    else:
        desc = "\n".join(p for p in (
            f"<p>{escape(AI_NOTICE)}</p>",
            f"<p>{escape(summary)}</p>" if summary else "",
            f'<p>Show notes with all references (IEEE): <a href="{escape(notes_url)}">{escape(notes_url)}</a></p>',
        ) if p)
    return desc, content


def rfc822(air_date: str) -> str:
    # Publish at 6:00 am Mountain (13:00 UTC, standard time) on the air date.
    d = datetime.strptime(air_date, "%Y-%m-%d").replace(hour=13, tzinfo=timezone.utc)
    return format_datetime(d)


def enclosure_url(e: dict) -> str:
    if AUDIO_BASE:
        return f"{AUDIO_BASE}/{e['url'].rsplit('/', 1)[-1]}"
    return e["url"]


def main() -> int:
    docs = Path(os.environ.get("FEED_DIR") or "docs")
    episodes = json.loads((docs / "episodes.json").read_text()) if (docs / "episodes.json").exists() else []
    episodes.sort(key=lambda e: (e["air_date"], e.get("stem", "")), reverse=True)
    episodes = episodes[:MAX_ITEMS]

    items = []
    for e in episodes:
        mins, secs = divmod(int(e["duration_s"]), 60)
        desc, content = episode_notes(e)
        items.append(f"""    <item>
      <title>{escape(e['title'])}</title>
      <description><![CDATA[{desc}]]></description>
      <content:encoded><![CDATA[{content}]]></content:encoded>
      <link>{escape(e.get('notes_url', SITE))}</link>
      <guid isPermaLink="false">alex-y-chino-{e['episode']}-{e['air_date']}</guid>
      <pubDate>{rfc822(e['air_date'])}</pubDate>
      <enclosure url="{escape(enclosure_url(e))}" length="{e['bytes']}" type="audio/mpeg"/>
      <itunes:duration>{mins}:{secs:02d}</itunes:duration>
      <itunes:explicit>true</itunes:explicit>
    </item>""")

    now = format_datetime(datetime.now(timezone.utc))
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/">
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
    <itunes:image href="{SITE}/cover.jpg"/>
    <image><url>{SITE}/cover.jpg</url><title>{SHOW_TITLE}</title><link>https://github.com/{OWNER}/{REPO}</link></image>
    <itunes:owner><itunes:name>Alex y Chino</itunes:name></itunes:owner>
    <itunes:type>episodic</itunes:type>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (docs / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"feed.xml: {len(items)} episodes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
