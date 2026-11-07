#!/usr/bin/env python3
"""Weekly theme-music pack: generate one 30-second Lyria clip in this week's genre,
cut it into intro / sting / outro, and save it to the music library.

    python pipeline/music_pack.py                 # genre picked by the weekly rotation
    python pipeline/music_pack.py --genre salsa   # force a genre
    python pipeline/music_pack.py --list          # show the rotation

Library layout:
    assets/music/library/<YYYY-MM-DD>_<genre>/{intro,sting,outro}.mp3 + pack.json
    assets/music/current.json  -> {"pack": "<YYYY-MM-DD>_<genre>"}
The serious sting (assets/music/sting-serious.mp3) never rotates, so hard news always sounds the same.
Costs ~$0.04 per pack (one Lyria clip) on the paid key.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from music_options import generate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LIB = ROOT / "assets" / "music" / "library"
CURRENT = ROOT / "assets" / "music" / "current.json"
TARGET_LUFS = -19  # ~3 dB under the voices (speech is leveled to -16)

_TAIL = ("Strong, catchy opening hook in the first 5 seconds, energetic and bright, built as a morning "
         "radio-show theme, with a clean, definite ending. Instrumental only, no vocals, no singing, no spoken words.")

# Rotation order (no country, per the host's request). Prompts name genres and instruments only, never artists.
GENRES: dict[str, str] = {
    "norteno-upbeat": "Upbeat modern norteño instrumental: lead button accordion, bajo sexto, electric bass, "
                      "snare-driven polka rhythm, 120 BPM, D major, festive.",
    "corrido-tumbado": "Modern Mexican regional corrido tumbado instrumental: bright requinto guitar riffs, "
                       "acoustic twelve-string guitar, tuba bass line, light trap hi-hats and 808 under a "
                       "regional Mexican groove, 95 BPM, A minor, confident and cool.",
    "mariachi": "Joyful mariachi instrumental: bright trumpets, violin section, vihuela and guitarrón, "
                "lively son jalisciense rhythm, 130 BPM, G major, celebratory.",
    "cumbia": "Upbeat cumbia instrumental with a Mexican sonidero feel: accordion melody, güiro, congas, "
              "electric bass, steady cumbia rhythm, 98 BPM, C major, danceable and warm.",
    "cumbia-rebajada": "Cumbia rebajada instrumental from northern Mexico: slowed-down cumbia groove, deep "
                       "heavy bass, accordion melody, güiro, laid-back and hypnotic but upbeat, 80 BPM, E minor.",
    "salsa": "Energetic salsa instrumental: piano montuno, congas, timbales, bongos, punchy brass section, "
             "clave rhythm, 180 BPM, F major, joyful and driving.",
    "bachata": "Upbeat modern bachata instrumental: bright requinto guitar lead, rhythm guitar, bongos, "
               "güira, electric bass, 128 BPM, B minor, romantic but energetic.",
    "merengue": "Fast, joyful merengue instrumental: tambora, güira, accordion and saxophone lead, "
                "electric bass, 150 BPM, G major, party energy.",
}


def week_genre(today: dt.date) -> str:
    """Genre for the episode week that starts on the next Monday (the Sunday run sets up Mon–Sat)."""
    names = list(GENRES)
    return names[(today + dt.timedelta(days=1)).isocalendar().week % len(names)]


def loudness(path: Path) -> float:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    vals = [ln.split()[1] for ln in out.splitlines() if ln.strip().startswith("I:")]
    return float(vals[-1])


def duration(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True, check=True).stdout.strip())


def cut(src: Path, dst: Path, start: float, length: float, fade_in: float, fade_out: float, work: Path) -> None:
    tmp = work / f"tmp_{dst.stem}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", str(src),
                    "-af", f"afade=t=in:d={fade_in},afade=t=out:st={length - fade_out:.2f}:d={fade_out}",
                    "-ar", "44100", "-ac", "2", str(tmp)], check=True)
    gain = round(TARGET_LUFS - loudness(tmp), 2)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
                    "-af", f"volume={gain}dB,alimiter=limit=0.95", "-c:a", "libmp3lame", "-b:a", "160k", str(dst)],
                   check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--genre", choices=list(GENRES))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--no-activate", action="store_true", help="add to library without making it current")
    args = ap.parse_args()

    today = dt.date.today()
    if args.list:
        for i, g in enumerate(GENRES):
            print(f"{i}: {g}" + ("   <- this week" if g == week_genre(today) else ""))
        return 0

    genre = args.genre or week_genre(today)
    prompt = f"{GENRES[genre]} {_TAIL}"
    name = f"{today.isoformat()}_{genre}"
    out = LIB / name
    out.mkdir(parents=True, exist_ok=True)

    from google import genai

    client = genai.Client()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        raw = work / "raw.mp3"
        model = generate(client, prompt, raw)
        total = duration(raw)
        outro_len = min(9.3, total - 1)
        cut(raw, out / "intro.mp3", 0, 8.0, 0.05, 1.8, work)
        cut(raw, out / "sting.mp3", 0, 3.2, 0.05, 1.2, work)
        cut(raw, out / "outro.mp3", max(0.0, total - outro_len), outro_len, 0.6, 0.4, work)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-c:a", "libmp3lame", "-b:a", "128k",
                        str(out / "full.mp3")], check=True)

    (out / "pack.json").write_text(json.dumps(
        {"pack": name, "genre": genre, "created": today.isoformat(), "model": model, "prompt": prompt}, indent=2,
        ensure_ascii=False) + "\n")
    if not args.no_activate:
        CURRENT.write_text(json.dumps({"pack": name}, indent=2) + "\n")
    print(f"Created music pack {name} ({model})" + ("" if args.no_activate else " and made it current"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
