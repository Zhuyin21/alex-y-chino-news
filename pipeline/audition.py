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
def _parse(spec: str):
    voices, _, model = spec.strip().partition("@")
    a, c = voices.split(":", 1)
    return a.strip(), c.strip(), (model.strip() or None)


PAIRS = [_parse(p) for p in _env.split(",") if ":" in p] if _env else [(a, c, None) for a, c in DEFAULT_PAIRS]

SAMPLE = [
    ("CHINO", "excited, friendly", "¡Quiúbole, Burque! ¿Qué onda? It's Monday, y la neta, Doc, todavía ando bien desvelado del fin de semana."),
    ("ALEX", "amused, relaxed", "Eee, Chino. It was two days, bro. You should've recovered by Sunday night."),
    ("CHINO", "laughing", "¡No manches, Doc! You've never been to a carne asada with my tíos en Juárez. La troca parqueada en la banqueta, la música a todo lo que da, y burritos hasta las dos de la mañana."),
    ("ALEX", "laughing, warm", "Uy, okay, that's fair. Suave. Ahí te watcho next time, pero first, the news."),
    ("CHINO", "storytelling", "Simón. Nombre, y mi abuela ya me marcó tres veces hoy. Dice que si no le llevo tamales el domingo, me deshereda. ¡Qué caray!"),
    ("ALEX", "dry, amused", "Ay, ay, ay. As an engineer, compa, the solution is simple: bring the tamales."),
    ("CHINO", "shifting tone, calmer", "Órale pues. Ya, hablando en serio..."),
    ("ALEX", "calm, serious", "In other news, and this one is more serious: let's talk about our water. Here in New Mexico, every drop counts."),
    ("CHINO", "lighter, moving on", "Y cambiando de tema, Doc, vámonos pal' otro lado del charco."),
    ("ALEX", "neutral, clear", "Switching gears to the world."),
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
        for i, (alex, chino, model) in enumerate(PAIRS, 1):
            turns = [b.Turn("ALEX", "neutral, announcer", f"Pair number {i}.")]
            turns += [b.Turn(s, st, t) for s, st, t in SAMPLE]
            chunk = b.Chunk(section="audition", turns=turns)
            voices = {"ALEX": alex, "CHINO": chino}
            print(f"Pair {i}: Alex={alex}, Chino={chino}, model={model or b.MODEL}")
            cw = work / f"pair_{i}.wav"
            used = b.tts_chunk(client, chunk, cw, voices=voices, model=model)
            print(f"  served by tier: {used}")
            wavs += [cw, pause]
        b.concat_to_mp3(wavs, out / "audition.mp3", work)
    legend = "\n".join(f"{i}. Alex = {a}, Chino = {c}, model = {m or b.MODEL}" for i, (a, c, m) in enumerate(PAIRS, 1))
    (out / "audition.txt").write_text(legend + "\n")
    print(legend)
    return 0


if __name__ == "__main__":
    sys.exit(main())
