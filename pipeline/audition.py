#!/usr/bin/env python3
"""Voice audition: render the same short Alex y Chino exchange with several voice pairs.

Output: build/audition.mp3, one clip per pair, each announced by number, with a pause between.
Costs a few cents per run.
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_episode as b  # noqa: E402

import os

DEFAULT_PAIRS = [  # (Alex voice, Chino voice)
    ("Sadaltager", "Puck"),
    ("Charon", "Achird"),
    ("Algenib", "Zubenelgenubi"),
    ("Iapetus", "Sadachbia"),
    ("Rasalgethi", "Fenrir"),
]
# Override with AUDITION_PAIRS="Algenib:Fenrir,Algenib:Achird"
_env = os.environ.get("AUDITION_PAIRS", "").strip()
PAIRS = [tuple(p.split(":", 1)) for p in _env.split(",") if ":" in p] if _env else DEFAULT_PAIRS

SAMPLE = [
    ("CHINO", "excited, laughing", "¡Qué onda, Burque! It's Monday, and Doc, la neta, I'm still not over the weekend."),
    ("ALEX", "playful, teasing", "Chino, it was two days. Scientifically, your recovery time should be like four hours, carnal."),
    ("CHINO", "outraged, joking", "¿Cuatro horas? ¡No mames, wey! You've never been to a carne asada with my tíos."),
    ("ALEX", "laughing, then warm", "Okay, fair. Ándale pues, let's get into the news before your abuela calls."),
    ("CHINO", "dramatic, storytelling", "Oye, la neta, mi abuela ya me habló tres veces hoy. Dice que si no le llevo tamales el domingo, me deshereda. ¡Está cañón, carnal!"),
    ("ALEX", "dry, amused", "Pues, statistically speaking, compa, I'd bring the tamales."),
]


def main() -> int:
    from google import genai

    client = genai.Client()
    out = Path("build")
    out.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        pause = work / "pause.wav"
        b.make_silence(pause, 1.5)
        wavs: list[Path] = []
        for i, (alex, chino) in enumerate(PAIRS, 1):
            turns = [b.Turn("ALEX", "neutral, announcer", f"Pair number {i}.")]
            turns += [b.Turn(s, st, t) for s, st, t in SAMPLE]
            chunk = b.Chunk(section="audition", turns=turns)
            voices = {"ALEX": alex, "CHINO": chino}
            print(f"Pair {i}: Alex={alex}, Chino={chino}")
            cw = work / f"pair_{i}.wav"
            b.tts_chunk(client, chunk, cw, voices=voices)
            wavs += [cw, pause]
        b.concat_to_mp3(wavs, out / "audition.mp3", work)
    legend = "\n".join(f"{i}. Alex = {a}, Chino = {c}" for i, (a, c) in enumerate(PAIRS, 1))
    (out / "audition.txt").write_text(legend + "\n")
    print(legend)
    return 0


if __name__ == "__main__":
    sys.exit(main())
