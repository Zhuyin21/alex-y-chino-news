#!/usr/bin/env python3
"""Sports transition sound effects ("Miércoles en La Cancha").

Builds short, reusable clips (assets/sfx/<sport>.mp3): a synthesized referee whistle / ball kick,
a stadium crowd bed, and a crowd of fans shouting, made by layering several Gemini TTS voices,
each copied a few times with small pitch/timing changes and stadium reverb.

  python pipeline/sfx.py futbol            # calls Gemini TTS for the shouts (needs GEMINI_API_KEY)
  python pipeline/sfx.py futbol --no-tts   # synthesized parts only (no API, for local tests)

Output: build/sfx/<sport>.mp3 (crowd voices + synth) and build/sfx/<sport>_sin-voces.mp3 (synth only).
Cost: a few seconds of TTS audio per voice pair, well under one cent per clip.
"""
from __future__ import annotations

import argparse
import base64
import io
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 24000
RNG = np.random.default_rng(7)
OUT = Path("build/sfx")

# Each sport: what the fans shout, and how they shout it.
SPORTS = {
    "futbol": {
        "lines": ["¡Gooooooool!", "¡Gooool, goool, gooool!", "¡Golazooo!", "¡Eso, eso, gooool!"],
        "style": ("a fan in a packed soccer stadium screaming a goal at the top of their lungs, ecstatic, "
                  "very loud, stretched vowels, Mexican Spanish"),
    },
}

# Varied voices so the crowd has men and women, high and low (two per request).
VOICE_PAIRS = [
    ("Fenrir", "Puck"), ("Charon", "Orus"), ("Enceladus", "Algenib"), ("Alnilam", "Umbriel"),
    ("Kore", "Leda"), ("Aoede", "Zephyr"), ("Despina", "Laomedeia"),
]


# ---------------------------------------------------------------- audio helpers
def read_wav(data: bytes) -> np.ndarray:
    with wave.open(io.BytesIO(data)) as w:
        raw = w.readframes(w.getnframes())
        sr, ch = w.getframerate(), w.getnchannels()
    x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if ch > 1:
        x = x.reshape(-1, ch).mean(axis=1)
    if sr != SR:
        x = resample(x, SR / sr)
    return x


def resample(x: np.ndarray, factor: float) -> np.ndarray:
    """factor > 1 makes it longer (lower pitch); < 1 shorter (higher pitch)."""
    n = max(1, int(len(x) * factor))
    return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x).astype(np.float32)


def trim(x: np.ndarray, thresh: float = 0.02) -> np.ndarray:
    idx = np.where(np.abs(x) > thresh)[0]
    return x[idx[0]:idx[-1] + 1] if len(idx) else x


def split_on_silence(x: np.ndarray, gap_s: float = 0.25, thresh: float = 0.02) -> list[np.ndarray]:
    """Cut a multi-shout recording into single shouts."""
    loud = np.abs(x) > thresh
    win = int(gap_s * SR)
    pieces, start, quiet = [], None, 0
    for i, v in enumerate(loud):
        if v:
            if start is None:
                start = i
            quiet = 0
        elif start is not None:
            quiet += 1
            if quiet > win:
                pieces.append(x[start:i - quiet])
                start, quiet = None, 0
    if start is not None:
        pieces.append(x[start:])
    return [p for p in pieces if len(p) > 0.3 * SR]


def fft_convolve(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = len(a) + len(b) - 1
    size = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(a, size) * np.fft.rfft(b, size), size)[:n].astype(np.float32)


def stadium_reverb(x: np.ndarray, seconds: float = 1.4, wet: float = 0.45) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    ir = RNG.standard_normal(len(t)).astype(np.float32) * np.exp(-t * 4.0)
    ir[0] = 1.0
    y = fft_convolve(x, ir)
    y /= np.max(np.abs(y)) + 1e-9
    dry = np.pad(x, (0, len(y) - len(x)))
    return (1 - wet) * dry / (np.max(np.abs(dry)) + 1e-9) + wet * y


def bandpass_noise(seconds: float, lo: float, hi: float) -> np.ndarray:
    n = int(seconds * SR)
    spec = np.fft.rfft(RNG.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec[(f < lo) | (f > hi)] = 0
    spec[f > 0] /= np.sqrt(f[f > 0] / lo)  # pinker
    y = np.fft.irfft(spec, n).astype(np.float32)
    return y / (np.max(np.abs(y)) + 1e-9)


def place(track: np.ndarray, clip: np.ndarray, at_s: float, gain: float) -> None:
    i = int(at_s * SR)
    if i >= len(track):
        return
    end = min(len(track), i + len(clip))
    track[i:end] += gain * clip[: end - i]


def fade(x: np.ndarray, fin: float, fout: float) -> np.ndarray:
    y = x.copy()
    a, b = int(fin * SR), int(fout * SR)
    if a:
        y[:a] *= np.linspace(0, 1, a)
    if b:
        y[-b:] *= np.linspace(1, 0, b)
    return y


# ---------------------------------------------------------------- synthesized parts
def referee_whistle(seconds: float = 0.45) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    f = 3150 + 40 * np.sin(2 * np.pi * 6 * t)                 # slight wobble
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR)
    rattle = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * 34 * t))  # the pea inside the whistle
    breath = 0.08 * bandpass_noise(seconds, 2500, 6000)[: len(t)]
    env = np.minimum(1, t / 0.015) * np.minimum(1, (seconds - t) / 0.05)
    return ((tone * rattle + breath) * env).astype(np.float32)


def ball_kick() -> np.ndarray:
    t = np.arange(int(0.18 * SR)) / SR
    thump = np.sin(2 * np.pi * (140 * np.exp(-t * 18) + 55) * t) * np.exp(-t * 28)
    slap = bandpass_noise(0.18, 800, 4000)[: len(t)] * np.exp(-t * 90) * 0.5
    return (thump + slap).astype(np.float32)


def crowd_bed(seconds: float) -> np.ndarray:
    """Roar that swells after the kick: band-limited noise with a slow 'breathing' envelope."""
    roar = bandpass_noise(seconds, 250, 3500)
    t = np.arange(len(roar)) / SR
    swell = np.clip((t - 0.7) / 0.6, 0, 1) * np.clip((seconds - t) / 1.6, 0, 1)
    flutter = 0.85 + 0.15 * np.sin(2 * np.pi * 3.1 * t + RNG.uniform(0, 6))
    return (roar * (0.25 + 0.75 * swell) * flutter).astype(np.float32)


# ---------------------------------------------------------------- TTS shouts
def tts_shouts(sport: str) -> list[np.ndarray]:
    from google import genai  # noqa: PLC0415 - only needed with TTS

    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY_FREE")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set (use --no-tts for a synth-only test)")
    client = genai.Client(api_key=key)
    model = os.environ.get("TTS_MODEL") or "gemini-3.8-flash-tts"
    cfg = SPORTS[sport]
    shouts: list[np.ndarray] = []
    for n, (v1, v2) in enumerate(VOICE_PAIRS):
        l1, l2 = cfg["lines"][n % len(cfg["lines"])], cfg["lines"][(n + 1) % len(cfg["lines"])]
        parts = [
            {"type": "text", "text": l1, "annotations": [{"type": "speech_metadata", "speaker": "Speaker1", "style": cfg["style"]}]},
            {"type": "text", "text": l2, "annotations": [{"type": "speech_metadata", "speaker": "Speaker2", "style": cfg["style"]}]},
        ]
        try:
            r = client.interactions.create(
                model=model,
                input=[{"type": "user_input", "content": parts}],
                response_format={"type": "audio"},
                generation_config={"speech_config": {"speakers": [
                    {"speaker": "Speaker1", "voice": v1}, {"speaker": "Speaker2", "voice": v2}]}},
                timeout=90,
            )
            audio = read_wav(base64.b64decode(r.output_audio.data))
        except Exception as e:  # noqa: BLE001 - one bad voice shouldn't sink the clip
            print(f"  {v1}+{v2}: failed ({str(e)[:120]})", file=sys.stderr)
            continue
        pieces = split_on_silence(audio) or [trim(audio)]
        print(f"  {v1}+{v2}: {len(pieces)} shouts")
        shouts += [trim(p) for p in pieces]
    if not shouts:
        raise SystemExit("no shouts came back from TTS")
    raw = OUT / f"{sport}_voces_crudas.wav"
    write_wav(raw, np.concatenate([np.pad(s, (0, SR // 4)) for s in shouts]))
    return shouts


# ---------------------------------------------------------------- mix
def mix(sport: str, shouts: list[np.ndarray], seconds: float = 6.0) -> np.ndarray:
    track = np.zeros(int(seconds * SR), dtype=np.float32)
    place(track, referee_whistle(), 0.05, 0.55)
    place(track, ball_kick(), 0.65, 0.9)
    place(track, crowd_bed(seconds), 0.0, 0.35)
    if shouts:
        crowd = np.zeros_like(track)
        # Each real shout is reused 3-4 times with a different pitch, timing and level: ~25-30 "fans".
        for s in shouts:
            for _ in range(int(RNG.integers(3, 5))):
                v = resample(s, float(RNG.uniform(0.86, 1.14)))
                place(crowd, v, float(RNG.uniform(0.8, 1.9)), float(RNG.uniform(0.25, 0.7)))
        crowd = stadium_reverb(crowd / (np.max(np.abs(crowd)) + 1e-9))[: len(track)]
        track += 0.75 * crowd
    track = fade(track, 0.0, 1.2)
    return track / (np.max(np.abs(track)) + 1e-9) * 0.9


def write_wav(path: Path, x: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def to_mp3(wav: Path, mp3: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav),
                    "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "24000", "-ac", "1",
                    "-c:a", "libmp3lame", "-b:a", "96k", str(mp3)], check=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("sport", choices=sorted(SPORTS))
    ap.add_argument("--no-tts", action="store_true", help="synthesized parts only (no API)")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    shouts = [] if args.no_tts else tts_shouts(args.sport)
    for name, voices in ((args.sport, shouts), (f"{args.sport}_sin-voces", [])):
        if name == args.sport and not shouts:
            continue
        wav = OUT / f"{name}.wav"
        write_wav(wav, mix(args.sport, voices))
        to_mp3(wav, OUT / f"{name}.mp3")
        print(f"wrote {OUT / name}.mp3")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
