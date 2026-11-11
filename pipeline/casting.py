#!/usr/bin/env python3
"""Casting: render the same short scene for each candidate voice of a new character.

Ashley auditions opposite Doc (Sábados Científicos); Sophie opposite Chino (Tuesday's Agenda Cultural).
Output: build/casting/<character>_<n>_<voice>.mp3, one file per candidate, plus build/casting.txt.
Override the candidates with CASTING="ASHLEY:Leda,ASHLEY:Autonoe,SOPHIE:Gacrux,…". A few cents per run.
"""
from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_episode as b  # noqa: E402

DEFAULT = [
    ("ASHLEY", "Leda"), ("ASHLEY", "Autonoe"), ("ASHLEY", "Erinome"), ("ASHLEY", "Laomedeia"),
    ("SOPHIE", "Gacrux"), ("SOPHIE", "Sulafat"), ("SOPHIE", "Pulcherrima"), ("SOPHIE", "Despina"),
]

SCENES = {
    # Ashley: ~70% English, home Spanish, science nerd, the occasional "no sabo" moment.
    "ASHLEY": [
        ("ALEX", "warm, welcoming", "Y ahora sí, the Saturday science corner. With us, la experta del show. Ashley, welcome back."),
        ("ASHLEY", "a little shy, then excited", "Okay, okay, hi everyone! So, I've been reading about this all week and I'm kind of obsessed."),
        ("ALEX", "dry, amused", "Of course you are."),
        ("ASHLEY", "enthusiastic, nerdy, fast", "So, eclipses, right? The Earth's shadow on the Moon is always round, from every angle. A flat disc can't do that. Only a sphere can. That's, like, geometry doing a mic drop."),
        ("ALEX", "laughing", "Geometry doing a mic drop. Eee, I'm stealing that."),
        ("ASHLEY", "trying her Spanish, a bit hesitant", "Y mi abuela siempre decía que la luna es como el... the... ¿cómo se dice? The mirror of the Earth."),
        ("ALEX", "gently", "El espejo, Ashley."),
        ("ASHLEY", "laughing at herself", "¡El espejo! Ay, remember que soy no sabo, Doc."),
    ],
    # Sophie: almost all Spanish, ex-telenovela star, fresa, English words with a strong Mexican accent.
    "SOPHIE": [
        ("CHINO", "excited", "¡Ya llegó, ya llegó! Sophie, ¿qué nos trajiste hoy? ¡Suelta la sopa!"),
        ("SOPHIE", "theatrical, fresa, warm", "Ay, Chino, ¡por favor! Primero se saluda, ¿no? Hola a todos, hola a mis amigas de producción. Ashley, mi amor, te ves divina."),
        ("CHINO", "laughing", "Ya, ya, ¡el chisme, Sophie!"),
        ("SOPHIE", "lowering her voice, conspiratorial", "Okay. Me llegó de muy, muy buena fuente que... ay, no. Espérate. Oh my God, no sé si debo decirlo."),
        ("CHINO", "impatient, half-laughing", "¡Nombre, Sophie, ya lo empezaste!"),
        ("SOPHIE", "dramatic, then serious", "Bueno, pero escúchenme bien: por ahorita es puro rumor, ¿eh? Si lo tuviera confirmado te lo daba exclusivo, my darling. Tú sabes que yo no invento nada."),
        ("CHINO", "teasing", "Nada más tantito."),
        ("SOPHIE", "offended, then laughing", "¡Chino! Ay, my honey, ¿cómo crees?"),
    ],
}


def candidates() -> list[tuple[str, str]]:
    spec = os.environ.get("CASTING", "").strip()
    if not spec:
        return DEFAULT
    out = []
    for item in spec.split(","):
        who, _, voice = item.strip().partition(":")
        if who.upper() in SCENES and voice.strip():
            out.append((who.upper(), voice.strip()))
    return out


def main() -> int:
    from google import genai

    client = genai.Client()
    out = Path("build/casting")
    out.mkdir(parents=True, exist_ok=True)
    legend = []
    counter: dict[str, int] = {}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for who, voice in candidates():
            counter[who] = counter.get(who, 0) + 1
            n = counter[who]
            chunk = b.Chunk(section="casting", turns=[b.Turn(s, st, t) for s, st, t in SCENES[who]])
            wav = work / f"{who}_{n}.wav"
            print(f"{who} #{n}: {voice}")
            used = b.tts_chunk(client, chunk, wav, voices={who: voice})
            print(f"  served by tier: {used}")
            name = f"{who.lower()}_{n}_{voice}.mp3"
            b.concat_to_mp3([wav], out / name, work)
            legend.append(f"{name}: {who} = {voice}")
    Path("build/casting.txt").write_text("\n".join(legend) + "\n")
    print("\n".join(legend))
    return 0


if __name__ == "__main__":
    sys.exit(main())
