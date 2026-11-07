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

MODEL = os.environ.get("TTS_MODEL") or "gemini-3.8-flash-tts"
# "flex" = 50% cheaper, slower (can queue 1-15 min per request). Falls back to standard if Flex fails.
SERVICE_TIER = (os.environ.get("TTS_SERVICE_TIER") or "flex").lower()
PARALLEL = int(os.environ.get("TTS_PARALLEL") or "4")
# Free tier: if GEMINI_API_KEY_FREE is set (a key from a project WITHOUT billing), use it first.
# Free TTS is rate-limited (~3 requests/min), so requests go one at a time with spacing.
# If the free quota runs out, the remaining chunks fall back to the paid key (GEMINI_API_KEY).
FREE_KEY = os.environ.get("GEMINI_API_KEY_FREE") or ""
FREE_MIN_INTERVAL_S = float(os.environ.get("FREE_MIN_INTERVAL_S") or "21")
VOICES = {
    "ALEX": os.environ.get("VOICE_ALEX") or "Algenib",     # "Gravelly"
    "CHINO": os.environ.get("VOICE_CHINO") or "Fenrir",   # "Excitable"
}
# Persona hints prepended to every line's style so the accent/register stays consistent.
PERSONA = {
    "ALEX": ("a mechanical engineer with a PhD, podcast co-host from Albuquerque, New Mexico; calm, clear and "
             "professional but relaxed and warm; American English with New Mexican flavor and natural Spanish words "
             "pronounced with a native Mexican accent"),
    "CHINO": ("a podcast co-host from Ciudad Juárez, Chihuahua, living in Albuquerque; warm, energetic and funny; "
              "speaks lots of fluent northern Mexican (Chihuahua border) Spanish mixed with English; native Juárez accent"),
}
MAX_CHARS_PER_CHUNK = int(os.environ.get("MAX_CHARS_PER_CHUNK", "1800"))
PAUSE_BETWEEN_CHUNKS_S = 0.5
PAUSE_BETWEEN_SECTIONS_S = 1.2

TTS_USAGE: dict = {}
LINE_RE = re.compile(r"^(ALEX|CHINO)\s*\[([^\]]*)\]\s*:\s*(.+)$")
MUSIC_RE = re.compile(r"^\[MUSIC:\s*([\w-]+)\s*\]$", re.I)
MUSIC_DIR = Path(__file__).resolve().parent.parent / "assets" / "music"
SPEECH_LUFS = -16  # music clips in assets/music are pre-leveled ~3-5 dB under this


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
    music: str | None = None  # set for [MUSIC: cue] chunks (no speech)

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
        mm = MUSIC_RE.match(line)
        if mm:
            flush()
            cue = mm.group(1).lower()
            if not (MUSIC_DIR / f"{cue}.mp3").exists():
                raise SystemExit(f"Unknown music cue '{cue}' (no assets/music/{cue}.mp3)")
            chunks.append(Chunk(section=section, music=cue, starts_section=new_section))
            new_section = False
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


def tts_chunk(client, chunk: Chunk, out_wav: Path, attempts: int = 4, voices: dict | None = None,
              model: str | None = None, tier: str | None = None) -> str:
    """Synthesize one chunk. Returns the service tier that actually produced the audio."""
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
    speakers = [{"speaker": s, "voice": v} for s, v in (voices or VOICES).items()]
    model = model or MODEL
    tier = (tier or SERVICE_TIER).lower()
    delay = 5.0
    for i in range(1, attempts + 1):
        # Last attempt always uses the standard tier so a Flex outage never blocks the episode.
        use_tier = "standard" if (i == attempts and tier != "standard") else tier
        kwargs = {"service_tier": use_tier, "timeout": 1200} if use_tier != "standard" else {"timeout": 300}
        try:
            interaction = client.interactions.create(
                model=model,
                input=[{"type": "user_input", "content": parts}],
                response_format={"type": "audio"},  # complete WAV, 24 kHz mono 16-bit
                generation_config={"speech_config": {"speakers": speakers}},
                **kwargs,
            )
            data = interaction.output_audio.data
            if not data:
                raise RuntimeError("empty audio in response")
            out_wav.write_bytes(base64.b64decode(data))
            return use_tier
        except Exception as e:  # noqa: BLE001 - retry any API/network error
            msg = str(e)
            permanent = any(c in msg for c in ("Error code: 400", "Error code: 401", "Error code: 403", "Error code: 404"))
            if permanent and use_tier != "standard":
                # Flex may not be offered for this model/project: drop straight to standard.
                print(f"  {use_tier} rejected ({msg[:160]}); switching to standard", file=sys.stderr)
                tier = "standard"
                continue
            if permanent:
                print(f"  non-retryable API error: {msg[:300]}", file=sys.stderr)
                raise
            if i == attempts:
                raise
            print(f"  attempt {i} ({use_tier}) failed ({msg[:160]}); retrying in {delay:.0f}s", file=sys.stderr)
            time.sleep(delay)
            delay *= 2
    raise RuntimeError("TTS failed after all attempts")


def make_silence(path: Path, seconds: float) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
         "anullsrc=r=24000:cl=mono", "-t", str(seconds), "-c:a", "pcm_s16le", str(path)],
        check=True,
    )


def normalize_speech(src: Path, dst: Path) -> None:
    """Level one TTS chunk to the podcast standard so every chunk (and the music) sits consistently."""
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
         "-af", f"loudnorm=I={SPEECH_LUFS}:TP=-1.5:LRA=11", "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(dst)],
        check=True,
    )


def music_pack() -> str | None:
    """Active weekly music pack: repo variable MUSIC_PACK pins one, else assets/music/current.json."""
    pinned = (os.environ.get("MUSIC_PACK") or "").strip()
    if pinned:
        return pinned
    cur = MUSIC_DIR / "current.json"
    if cur.exists():
        try:
            return json.loads(cur.read_text()).get("pack")
        except ValueError:
            return None
    return None


def music_file(cue: str) -> Path:
    """Use this week's pack for intro/sting/outro when it has the cue; otherwise the original clips."""
    pack = music_pack()
    if pack:
        candidate = MUSIC_DIR / "library" / pack / f"{cue}.mp3"
        if candidate.exists():
            return candidate
    return MUSIC_DIR / f"{cue}.mp3"


def music_wav(cue: str, work: Path) -> Path:
    out = work / f"music_{cue}.wav"
    if not out.exists():
        src = music_file(cue)
        print(f"  music {cue}: {src.relative_to(MUSIC_DIR.parent.parent)}")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(src),
             "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(out)],
            check=True,
        )
    return out


def concat_to_mp3(wavs: list[Path], out_mp3: Path, work: Path, normalize: bool = True) -> None:
    listing = work / "concat.txt"
    listing.write_text("".join(f"file '{w.as_posix()}'\n" for w in wavs))
    af = "loudnorm=I=-16:TP=-1.5:LRA=11" if normalize else "alimiter=limit=0.9"
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
         "-af", af, "-ac", "1", "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "64k", str(out_mp3)],
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
    n_music = sum(1 for c in chunks if c.music)
    n_words = sum(len(t.text.split()) for c in chunks for t in c.turns)
    print(f"{args.script.name}: {len(chunks) - n_music} speech chunks, {n_music} music cues, {n_turns} turns, "
          f"~{n_words} words (~{n_words / 150:.0f} min speech)")
    if args.dry_run:
        for i, c in enumerate(chunks):
            if c.music:
                print(f"  [{i:02d}] {c.section[:40]:40s} ♪ {c.music}")
            else:
                print(f"  [{i:02d}] {c.section[:40]:40s} turns={len(c.turns):2d} chars={c.chars}")
        return 0

    from google import genai  # imported here so --dry-run works without the SDK

    paid_key = os.environ.get("GEMINI_API_KEY") or ""
    client = genai.Client(api_key=paid_key) if paid_key else None
    free_client = genai.Client(api_key=FREE_KEY) if FREE_KEY else None
    if not client and not free_client:
        raise SystemExit("No Gemini API key: set GEMINI_API_KEY and/or GEMINI_API_KEY_FREE")
    args.out.mkdir(parents=True, exist_ok=True)
    stem = args.script.stem
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        short, long_ = work / "pause_s.wav", work / "pause_l.wav"
        make_silence(short, PAUSE_BETWEEN_CHUNKS_S)
        make_silence(long_, PAUSE_BETWEEN_SECTIONS_S)
        from concurrent.futures import ThreadPoolExecutor

        speech = [(i, c) for i, c in enumerate(chunks) if not c.music]
        print(f"  TTS: {len(speech)} chunks, model={MODEL}, tier={SERVICE_TIER}, parallel={PARALLEL}")
        t0 = time.time()

        def synth(item):
            i, c = item
            raw = work / f"chunk_{i:03d}_raw.wav"
            used = tts_chunk(client, c, raw)
            normalize_speech(raw, work / f"chunk_{i:03d}.wav")
            print(f"    chunk {i:02d} done (paid {used}, {time.time() - t0:.0f}s)")
            return f"paid-{used}"

        tiers_used: list[str] = []
        remaining = list(speech)
        if free_client:
            print(f"  Free tier first: one request every {FREE_MIN_INTERVAL_S:.0f}s")
            last = 0.0
            while remaining:
                i, c = remaining[0]
                raw = work / f"chunk_{i:03d}_raw.wav"
                ok = False
                for attempt in range(3):
                    wait = FREE_MIN_INTERVAL_S - (time.time() - last)
                    if wait > 0:
                        time.sleep(wait)
                    last = time.time()
                    try:
                        tts_chunk(free_client, c, raw, attempts=1, tier="standard")
                        ok = True
                        break
                    except Exception as e:  # noqa: BLE001
                        msg = str(e)
                        print(f"    free chunk {i:02d} attempt {attempt + 1} failed: {msg[:160]}", file=sys.stderr)
                        if "429" in msg or "RESOURCE_EXHAUSTED" in msg.upper():
                            time.sleep(65)  # per-minute limit: wait it out once or twice
                            continue
                        break  # other errors: hand this chunk to the paid key
                if not ok:
                    print("    free tier unavailable or exhausted; switching the rest to the paid key")
                    break
                normalize_speech(raw, work / f"chunk_{i:03d}.wav")
                print(f"    chunk {i:02d} done (free, {time.time() - t0:.0f}s)")
                tiers_used.append("free")
                remaining.pop(0)
        if remaining:
            if not client:
                raise SystemExit("Free tier exhausted and no paid GEMINI_API_KEY set")
            with ThreadPoolExecutor(max_workers=PARALLEL) as pool:
                tiers_used += list(pool.map(synth, remaining))
        TTS_USAGE.update({t: tiers_used.count(t) for t in set(tiers_used)})
        print(f"  TTS finished in {time.time() - t0:.0f}s; chunks by source: {TTS_USAGE}")

        wavs: list[Path] = []
        prev_music = False
        for i, c in enumerate(chunks):
            if c.music:
                if wavs and not prev_music:
                    wavs.append(short)
                wavs.append(music_wav(c.music, work))
                prev_music = True
                continue
            wav = work / f"chunk_{i:03d}.wav"
            if wavs and not prev_music:
                wavs.append(long_ if c.starts_section else short)
            wavs.append(wav)
            prev_music = False
        mp3 = args.out / f"{stem}.mp3"
        concat_to_mp3(wavs, mp3, work, normalize=False)

    info = {
        "file": mp3.name,
        "episode": meta.get("episode", "").split()[0],
        "air_date": meta.get("air_date", "").split()[0],
        "bytes": mp3.stat().st_size,
        "duration_s": duration_seconds(mp3),
        "title": meta.get("title", ""),
        "tts_model": MODEL,
        "tts_tier": SERVICE_TIER,
        "tts_usage": TTS_USAGE,
        "music_pack": music_pack(),
        "stories": story_titles(md),
    }
    (args.out / f"{stem}.json").write_text(json.dumps(info, indent=2))
    print(f"Wrote {mp3} ({info['bytes'] / 1e6:.1f} MB, {info['duration_s'] // 60} min)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
