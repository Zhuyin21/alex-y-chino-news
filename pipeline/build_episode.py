#!/usr/bin/env python3
"""Turn an Alex y Chino episode script (Markdown) into an MP3 using Gemini multi-speaker TTS.

Usage:
    python pipeline/build_episode.py episodes/2026-11-06_episode-000.md --out build/
    python pipeline/build_episode.py episodes/... --dry-run   # parse + chunk only, no API calls

Script format (one spoken line per row):
    SPEAKER [delivery style]: text
Everything from the "# SHOW NOTES" heading down is ignored.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path

MODEL = os.environ.get("TTS_MODEL", "gemini-3.8-flash-tts")
VOICES = {
    "ALEX": os.environ.get("VOICE_ALEX", "Sadaltager"),   # "Knowledgeable"
    "CHINO": os.environ.get("VOICE_CHINO", "Puck"),       # "Upbeat"
}
# Persona hints prepended to every line's style so the accent/register stays consistent.
PERSONA = {
    "ALEX": "a scientist podcast host with dry humor, clear and measured, American English with natural Spanish words",
    "CHINO": "a Mexican-American podcast host from Albuquerque, warm and funny, natural Spanglish, Mexican Spanish pronunciation for Spanish words",
}
MAX_CHARS_PER_CHUNK = int(os.environ.get("MAX_CHARS_PER_CHUNK", "1800"))
PAUSE_BETWEEN_CHUNKS_S = 0.5
PAUSE_BETWEEN_SECTIONS_S = 1.2

LINE_RE = re.compile(r"^(ALEX|CHINO)\s*\[([^\]]*)\]\s*:\s*(.+)$")


@dataclass
class Turn:
    speaker: str
    style: str
    text: str


@dataclass
class Chunk:
    section: str
    turns: list[Turn] = field(default_factory=list)
    starts_section: bool = False

    @property
    def chars(self) -> int:
        return sum(len(t.text) for t in self.turns)


def parse_front_matter(md: str) -> dict:
    meta: dict = {}
    m = re.match(r"^---\n(.*?)\n---\n", md, re.S)
    if not m:
        return meta
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip().strip('"')
    return meta


def clean(text: str) -> str:
    text = re.sub(r"[*_`]", "", text)          # markdown emphasis
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_script(md: str) -> list[Chunk]:
    body = re.split(r"^# SHOW NOTES", md, maxsplit=1, flags=re.M)[0]
    chunks: list[Chunk] = []
    section = "intro"
    current: Chunk | None = None
    new_section = True

    def flush():
        nonlocal current
        if current and current.turns:
            chunks.append(current)
        current = None

    for raw in body.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            flush()
            section = line[3:].strip()
            new_section = True
            continue
        if line.startswith("### "):
            flush()  # each story starts a new chunk
            continue
        m = LINE_RE.match(line)
        if not m:
            continue
        turn = Turn(m.group(1), m.group(2).strip(), clean(m.group(3)))
        if current is None or current.chars + len(turn.text) > MAX_CHARS_PER_CHUNK:
            flush()
            current = Chunk(section=section, starts_section=new_section)
            new_section = False
        current.turns.append(turn)
    flush()
    return chunks


def story_titles(md: str) -> list[str]:
    body = re.split(r"^# SHOW NOTES", md, maxsplit=1, flags=re.M)[0]
    return [re.sub(r"^\d+\.\s*", "", h).strip() for h in re.findall(r"^### (.+)$", body, re.M)]


def tts_chunk(client, chunk: Chunk, out_wav: Path, attempts: int = 4) -> None:
    parts = [
        {
            "type": "text",
            "text": t.text,
            "annotations": [{
                "type": "speech_metadata",
                "speaker": t.speaker,
                "style": f"{PERSONA[t.speaker]}; {t.style}" if t.style else PERSONA[t.speaker],
            }],
        }
        for t in chunk.turns
    ]
    speakers = [{"speaker": s, "voice": v} for s, v in VOICES.items()]
    delay = 5.0
    for i in range(1, attempts + 1):
        try:
            interaction = client.interactions.create(
                model=MODEL,
                input=[{"type": "user_input", "content": parts}],
                response_format={"type": "audio"},  # complete WAV, 24 kHz mono 16-bit
                generation_config={"speech_config": {"speakers": speakers}},
            )
            data = interaction.output_audio.data
            if not data:
                raise RuntimeError("empty audio in response")
            out_wav.write_bytes(base64.b64decode(data))
            return
        except Exception as e:  # noqa: BLE001 - retry any API/network error
            if i == attempts:
                raise
            print(f"  attempt {i} failed ({e!r}); retrying in {delay:.0f}s", file=sys.stderr)
            time.sleep(delay)
            delay *= 2


def make_silence(path: Path, seconds: float) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
         "anullsrc=r=24000:cl=mono", "-t", str(seconds), "-c:a", "pcm_s16le", str(path)],
        check=True,
    )


def concat_to_mp3(wavs: list[Path], out_mp3: Path, work: Path) -> None:
    listing = work / "concat.txt"
    listing.write_text("".join(f"file '{w.as_posix()}'\n" for w in wavs))
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",   # podcast loudness standard
         "-ac", "1", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "64k", str(out_mp3)],
        check=True,
    )


def duration_seconds(path: Path) -> int:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return int(float(out))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--out", type=Path, default=Path("build"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    md = args.script.read_text(encoding="utf-8")
    meta = parse_front_matter(md)
    chunks = parse_script(md)
    n_turns = sum(len(c.turns) for c in chunks)
    n_words = sum(len(t.text.split()) for c in chunks for t in c.turns)
    print(f"{args.script.name}: {len(chunks)} chunks, {n_turns} turns, ~{n_words} words "
          f"(~{n_words / 150:.0f} min)")
    if args.dry_run:
        for i, c in enumerate(chunks):
            print(f"  [{i:02d}] {c.section[:40]:40s} turns={len(c.turns):2d} chars={c.chars}")
        return 0

    from google import genai  # imported here so --dry-run works without the SDK

    client = genai.Client()  # reads GEMINI_API_KEY
    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.script.stem
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        short, long_ = work / "pause_s.wav", work / "pause_l.wav"
        make_silence(short, PAUSE_BETWEEN_CHUNKS_S)
        make_silence(long_, PAUSE_BETWEEN_SECTIONS_S)
        wavs: list[Path] = []
        for i, c in enumerate(chunks):
            wav = work / f"chunk_{i:03d}.wav"
            print(f"  TTS chunk {i + 1}/{len(chunks)} ({c.section[:30]})")
            tts_chunk(client, c, wav)
            if wavs:
                wavs.append(long_ if c.starts_section else short)
            wavs.append(wav)
        mp3 = args.out / f"{stem}.mp3"
        concat_to_mp3(wavs, mp3, work)

    info = {
        "file": mp3.name,
        "episode": meta.get("episode", "").split()[0],
        "air_date": meta.get("air_date", "").split()[0],
        "bytes": mp3.stat().st_size,
        "duration_s": duration_seconds(mp3),
        "title": meta.get("title", ""),
        "stories": story_titles(md),
    }
    (args.out / f"{stem}.json").write_text(json.dumps(info, indent=2))
    print(f"Wrote {mp3} ({info['bytes'] / 1e6:.1f} MB, {info['duration_s'] // 60} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
