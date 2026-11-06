#!/usr/bin/env python3
"""Generate candidate theme-music styles with Lyria (30-second instrumental clips, ~$0.04 each).

Output: build/music/NN_<style>.mp3 for each style, plus build/music/all_styles.mp3
(every clip back to back, with a short gap) so they're easy to compare on a phone.
Prompts describe genres and instruments only. No artist names: Lyria blocks them,
and we want original music anyway.
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

MODELS = [m for m in [os.environ.get("MUSIC_MODEL"), "lyria-3-clip-preview", "lyria-3.5-clip-preview"] if m]

STYLES = {
    "cumbia-nortena-upbeat": (
        "Upbeat modern cumbia norteña instrumental with a Mexican-American border sound, made as a morning radio "
        "show theme. Lead button accordion playing a catchy, bright melody; bajo sexto strumming the cumbia rhythm; "
        "electric bass; güiro and light drums. 95 BPM, G major, celebratory and feel-good. Clear opening hook in the "
        "first 5 seconds and a clean ending. Instrumental only, no vocals."
    ),
    "cumbia-nortena-romantica": (
        "Smooth, romantic modern cumbia norteña instrumental. Expressive button accordion melody with vibrato, "
        "bajo sexto and requinto guitar, warm electric bass, soft güiro, relaxed groove. 88 BPM, D major, "
        "nostalgic, like driving at sunrise. Instrumental only, no vocals."
    ),
    "norteno-sax-chihuahua": (
        "Energetic norteño-sax instrumental in the northern Chihuahua, Mexico style: alto saxophone lead melody, "
        "bajo sexto, upright tololoche-style bass, snare drum, bouncy cumbia-polka rhythm. 105 BPM, A major, "
        "festive, a party in Juárez. Instrumental only, no vocals."
    ),
    "cumbia-electronica": (
        "Modern electronic cumbia instrumental for a podcast intro: accordion riff over a deep sub bass, crisp hand "
        "percussion, güiro, subtle synth pads, punchy and urban but warm. 92 BPM, E minor. Instrumental only, no vocals."
    ),
    "serious-news-bed": (
        "Calm, respectful news transition music: solo nylon-string requinto guitar with soft ambient pads and a very "
        "subtle low drum. 70 BPM, D minor, reflective and serious, for introducing hard news. Instrumental only, no vocals."
    ),
}


def generate(client, prompt: str, out: Path) -> str:
    last = None
    for model in MODELS:
        for attempt in range(3):
            try:
                interaction = client.interactions.create(model=model, input=prompt)
                audio = interaction.output_audio
                if not audio or not audio.data:
                    raise RuntimeError("no audio returned")
                out.write_bytes(base64.b64decode(audio.data))
                return model
            except Exception as e:  # noqa: BLE001
                last = e
                msg = str(e)
                print(f"  {model} attempt {attempt + 1}: {msg[:200]}", file=sys.stderr)
                if "404" in msg:
                    break  # model id not available, so try the next one
                time.sleep(5 * (attempt + 1))
    raise RuntimeError(f"all models failed: {last}")


def main() -> int:
    from google import genai

    client = genai.Client()
    outdir = Path("build/music")
    outdir.mkdir(parents=True, exist_ok=True)
    files, legend = [], []
    for i, (name, prompt) in enumerate(STYLES.items(), 1):
        out = outdir / f"{i:02d}_{name}.mp3"
        print(f"{i}. {name}")
        model = generate(client, prompt, out)
        files.append(out)
        legend.append(f"{i}. {name} ({model})")

    with tempfile.TemporaryDirectory() as tmp:
        gap = Path(tmp) / "gap.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                        "anullsrc=r=44100:cl=stereo", "-t", "2", "-c:a", "libmp3lame", "-b:a", "128k", str(gap)],
                       check=True)
        listing = Path(tmp) / "list.txt"
        listing.write_text("".join(f"file '{p.resolve().as_posix()}'\nfile '{gap.as_posix()}'\n" for p in files))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(listing),
                        "-ar", "44100", "-ac", "2", "-c:a", "libmp3lame", "-b:a", "128k",
                        str(outdir / "all_styles.mp3")], check=True)
    (outdir / "legend.txt").write_text("Theme music options (each 30 s, in this order):\n" + "\n".join(legend) + "\n")
    print("\n".join(legend))
    return 0


if __name__ == "__main__":
    sys.exit(main())
