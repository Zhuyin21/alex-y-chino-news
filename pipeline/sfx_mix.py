#!/usr/bin/env python3
"""Build the sports transition clips for "Miércoles en La Cancha" from real sound effects.

Sources (Pixabay, free for commercial use, no attribution required) live in assets/sfx/src/;
each recipe below cuts pieces from them, layers them on a short timeline and levels the result
to sit with the music stings (~-19 LUFS). Output: assets/sfx/<name>.mp3, used in scripts as
[SFX: <name>] (e.g. [SFX: futbol]).

  python pipeline/sfx_mix.py            # rebuild every clip
  python pipeline/sfx_mix.py futbol nba # just these
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np

SR = 24000
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "sfx" / "src"
OUT = ROOT / "assets" / "sfx"
TARGET_LUFS = -19.0  # same level as the music stings (speech is -16)


def load(name: str) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(SRC / name), "-f", "s16le",
                          "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


def cut(x: np.ndarray, start: float, end: float, fin: float = 0.01, fout: float = 0.05) -> np.ndarray:
    y = x[int(start * SR):int(end * SR)].copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        y[:a] *= np.linspace(0, 1, a)
    if b:
        y[-b:] *= np.linspace(1, 0, b)
    return y


def db(gain_db: float) -> float:
    return 10 ** (gain_db / 20)


def timeline(seconds: float, layers: list[tuple[float, np.ndarray, float]], fade_out: float) -> np.ndarray:
    """layers: (start time, clip, gain in dB)."""
    out = np.zeros(int(seconds * SR), dtype=np.float32)
    for at, clip, g in layers:
        i = int(at * SR)
        n = min(len(clip), len(out) - i)
        if n > 0:
            out[i:i + n] += db(g) * clip[:n]
    b = int(fade_out * SR)
    out[-b:] *= np.linspace(1, 0, b) ** 1.5
    return out


# ---------------------------------------------------------------- recipes
def futbol() -> np.ndarray:
    whistle = cut(load("futbol-silbato.mp3"), 0.10, 0.62, fout=0.12)
    kick = cut(load("futbol-patada.mp3"), 0.03, 0.40, fout=0.15)
    crowd = cut(load("futbol-gol.mp3"), 22.70, 27.70, fin=0.25)  # the goal erupts ~0.5 s in
    return timeline(5.2, [(0.0, whistle, -4), (0.68, kick, 7), (0.80, crowd, 0)], fade_out=1.4)


def nfl() -> np.ndarray:
    whistle = cut(load("nfl-silbato.mp3"), 1.36, 2.32, fout=0.12)  # one set of three blasts
    crowd = cut(load("nfl-multitud.mp3"), 0.75, 5.0, fin=0.05)
    return timeline(4.6, [(0.0, whistle, -6), (0.55, crowd, -4)], fade_out=1.3)


def nba() -> np.ndarray:
    arena = cut(load("nba-arena.mp3"), 5.0, 9.0, fin=0.2)
    swish = cut(load("nba-swish.mp3"), 1.58, 2.10, fout=0.12)  # the loudest of the first three
    buzzer = cut(load("nba-buzzer.mp3"), 1.00, 2.60, fout=0.4)
    return timeline(3.8, [(0.0, arena, 2), (0.15, swish, 2), (0.75, buzzer, -3)], fade_out=1.0)


def box() -> np.ndarray:
    bell = cut(load("box-campana.mp3"), 0.05, 1.18, fout=0.2)
    arena = cut(load("nba-arena.mp3"), 12.0, 15.5, fin=0.3)
    return timeline(3.2, [(0.0, arena, -2), (0.1, bell, 0), (1.05, bell, -2)], fade_out=1.0)


def lobos() -> np.ndarray:
    crowd = cut(load("lobos-aficion.mp3"), 22.0, 26.5, fin=0.3)
    return timeline(4.2, [(0.0, crowd, 0)], fade_out=1.2)


# ---------------------------------------------------------------- Tech Thursday
def tone(freqs: list[tuple[float, float]], seconds: float, decay: float) -> np.ndarray:
    """A small synthesized bell/beep: (frequency, level) partials with an exponential decay."""
    t = np.arange(int(seconds * SR)) / SR
    y = sum(lvl * np.sin(2 * np.pi * f * t) for f, lvl in freqs)
    env = np.minimum(1, t / 0.004) * np.exp(-t * decay)
    return (y * env).astype(np.float32)


def ping() -> np.ndarray:
    """Two-note notification ping (generic, not any brand's sound)."""
    bell = [(1.0, 1.0), (2.76, 0.25), (5.4, 0.08)]
    a = tone([(1318.5 * k, l) for k, l in bell], 0.5, 9)
    b = tone([(1760.0 * k, l) for k, l in bell], 0.8, 7)
    return timeline(1.0, [(0.0, a, -3), (0.11, b, 0)], fade_out=0.2)


def stutter(x: np.ndarray, seed: int = 3) -> np.ndarray:
    """Chop a sound into random on/off slices: a digital glitch."""
    rng = np.random.default_rng(seed)
    y, i = x.copy(), 0
    while i < len(y):
        n = int(rng.uniform(0.015, 0.06) * SR)
        if rng.random() < 0.45:
            y[i:i + n] = 0
        elif i >= n and rng.random() < 0.3:  # repeat the previous slice (the "stuck" glitch)
            m = len(y[i:i + n])
            y[i:i + m] = y[i - n:i - n + m]
        i += n
    return y


def sweep(f0: float, f1: float, seconds: float) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    f = f0 * (f1 / f0) ** (t / seconds)
    y = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3  # square wave = digital
    y = np.round(y * 6) / 6                                   # bit-crush
    return (y * np.minimum(1, t / 0.05)).astype(np.float32)


def space_beeps() -> np.ndarray:
    pattern = [(0.0, 1200), (0.18, 1200), (0.36, 1500), (0.9, 1200), (1.08, 1800)]
    return timeline(1.8, [(at, tone([(f, 1.0), (f * 2, 0.15)], 0.12, 25), -2) for at, f in pattern], fade_out=0.2)


def tech_noticias() -> np.ndarray:
    keys = cut(load("tech-teclado.mp3"), 1.30, 2.90, fin=0.05, fout=0.2)
    return timeline(2.7, [(0.0, keys, 0), (1.55, ping(), -1)], fade_out=0.4)


def tech_ia() -> np.ndarray:
    static = stutter(cut(load("tech-estatica.mp3"), 0.5, 1.4, fin=0.02, fout=0.1))
    rise = stutter(sweep(220, 1760, 0.9), seed=11)
    return timeline(2.0, [(0.0, static, 2), (0.05, rise, -8), (0.95, ping(), 0)], fade_out=0.4)


def tech_vale() -> np.ndarray:
    return timeline(1.6, [(0.0, cut(load("tech-kaching.mp3"), 0.40, 1.80, fin=0.01, fout=0.3), 0)], fade_out=0.3)


def tech_si_vale() -> np.ndarray:
    return timeline(1.2, [(0.0, cut(load("tech-correcto.mp3"), 0.0, 1.10, fout=0.3), 0)], fade_out=0.3)


def tech_esperate() -> np.ndarray:
    return timeline(2.1, [(0.0, cut(load("tech-tictac.mp3"), 0.62, 2.70, fout=0.2), 0)], fade_out=0.3)


def tech_ni_lo_pienses() -> np.ndarray:
    return timeline(1.0, [(0.0, cut(load("tech-buzzer.mp3"), 0.58, 1.55, fout=0.15), 0)], fade_out=0.2)


def tech_avance() -> np.ndarray:
    return timeline(2.8, [(0.0, cut(load("tech-cohete.mp3"), 0.10, 3.00, fin=0.15, fout=0.6), 0)], fade_out=0.8)


def drumroll_into(verdict: np.ndarray) -> np.ndarray:
    roll = cut(load("tech-redoble.mp3"), 2.60, 4.05, fin=0.3, fout=0.03)  # stops right before the cymbal
    return timeline(2.6, [(0.0, roll, 0), (1.45, verdict, 3)], fade_out=0.3)


def tech_realidad() -> np.ndarray:
    return drumroll_into(cut(load("tech-correcto.mp3"), 0.0, 1.10, fout=0.3))


def tech_hype() -> np.ndarray:
    return drumroll_into(cut(load("tech-buzzer.mp3"), 0.58, 1.55, fout=0.15))


def tech_nm() -> np.ndarray:
    static = cut(load("tech-estatica.mp3"), 2.0, 5.0, fin=0.3, fout=0.5)
    return timeline(2.8, [(0.0, static, -4), (0.4, space_beeps(), 0)], fade_out=0.6)


# ---------------------------------------------------------------- every day
def alerta() -> np.ndarray:  # serious newsroom intro, for real breaking news only
    return timeline(4.0, [(0.0, cut(load("general-alerta.mp3"), 0.60, 4.60, fin=0.05), 0)], fade_out=1.3)


def bueno() -> np.ndarray:  # bright chime before Lo Bueno del Día
    return timeline(1.1, [(0.0, cut(load("general-bueno.mp3"), 0.0, 1.08, fin=0.005, fout=0.2), 0)], fade_out=0.2)


def rimshot() -> np.ndarray:  # ba-dum-tss after one of Doc's dad jokes
    return timeline(2.2, [(0.0, cut(load("general-rimshot.mp3"), 0.36, 2.60, fin=0.005), 0)], fade_out=0.8)


def grillos() -> np.ndarray:  # a joke that didn't land
    return timeline(2.6, [(0.0, cut(load("general-grillos.mp3"), 1.0, 3.6, fin=0.3), 0)], fade_out=0.6)


def scratch() -> np.ndarray:  # record scratch (third take of the source)
    return timeline(0.8, [(0.0, cut(load("general-scratch.mp3"), 5.20, 5.95, fin=0.005, fout=0.08), 0)], fade_out=0.1)


def scratch_2() -> np.ndarray:  # second take; the build rotates the two weekly
    return timeline(0.9, [(0.0, cut(load("general-scratch.mp3"), 2.65, 3.40, fin=0.005, fout=0.08), 0)], fade_out=0.1)


def aplausos() -> np.ndarray:  # big applause
    return timeline(3.4, [(0.0, cut(load("general-aplausos.mp3"), 0.5, 3.9, fin=0.2), 0)], fade_out=1.2)


def aplausos_chico() -> np.ndarray:  # small applause
    return timeline(3.0, [(0.0, cut(load("general-aplausos-chico.mp3"), 0.5, 3.5, fin=0.2), 0)], fade_out=1.0)


# Quieter targets for sounds that should sit under the voices.
LEVEL = {"grillos": -24.0, "bueno": -20.0, "alerta": -20.0}

RECIPES = {
    # Every day
    "alerta": alerta, "bueno": bueno, "rimshot": rimshot, "grillos": grillos,
    "scratch": scratch, "scratch-2": scratch_2, "aplausos": aplausos, "aplausos-chico": aplausos_chico,
    # Miércoles en La Cancha
    "futbol": futbol, "nfl": nfl, "nba": nba, "box": box, "lobos": lobos,
    # Tech Thursday
    "tech-noticias": tech_noticias, "tech-ia": tech_ia, "tech-vale": tech_vale,
    "tech-si-vale": tech_si_vale, "tech-esperate": tech_esperate, "tech-ni-lo-pienses": tech_ni_lo_pienses,
    "tech-avance": tech_avance, "tech-realidad": tech_realidad, "tech-hype": tech_hype, "tech-nm": tech_nm,
}


# ---------------------------------------------------------------- leveling + export
def write_wav(path: Path, x: np.ndarray) -> None:
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def integrated_lufs(wav: Path) -> float:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(wav), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    lines = [ln for ln in err.splitlines() if ln.strip().startswith("I:")]
    return float(lines[-1].split()[1])


def export(name: str, x: np.ndarray) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.5
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / f"{name}.wav"
        write_wav(wav, x)
        gain = LEVEL.get(name, TARGET_LUFS) - integrated_lufs(wav)
        peak_db = 20 * np.log10(np.max(np.abs(x)) + 1e-9)
        gain = min(gain, -2.0 - peak_db)  # never past -2 dBFS
        mp3 = OUT / f"{name}.mp3"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), "-af", f"volume={gain:.2f}dB",
                        "-ar", str(SR), "-ac", "1", "-c:a", "libmp3lame", "-b:a", "128k", str(mp3)], check=True)
    return mp3


def main(argv: list[str]) -> int:
    names = argv or list(RECIPES)
    for n in names:
        mp3 = export(n, RECIPES[n]())
        print(f"{mp3.relative_to(ROOT)}  {len(RECIPES[n]()) / SR:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
