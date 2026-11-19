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


def consulta() -> np.ndarray:  # airplane cabin chime ("ding-dong") before a featured question
    return timeline(2.3, [(0.0, cut(load("general-consulta.mp3"), 0.02, 2.38, fin=0.005), 0)], fade_out=0.6)


def campanilla() -> np.ndarray:  # hotel desk bell: a pick locked in, a "dato curioso"
    return timeline(1.6, [(0.0, cut(load("general-campanilla.mp3"), 0.03, 1.80, fin=0.003), 0)], fade_out=0.5)


def escribiendo() -> np.ndarray:  # pen on paper: "anotado"
    return timeline(2.0, [(0.0, cut(load("general-escribiendo.mp3"), 0.65, 2.75, fin=0.1), 0)], fade_out=0.5)


# ---------------------------------------------------------------- Sábados Científicos
def sabado_burbujas() -> np.ndarray:  # lab bubbling: El Tema de Ashley
    return timeline(2.8, [(0.0, cut(load("sabado-burbujas.mp3"), 0.8, 3.8, fin=0.25), 0)], fade_out=0.8)


def sabado_eureka() -> np.ndarray:  # the lightbulb "ding!"
    return timeline(1.8, [(0.0, cut(load("sabado-eureka.mp3"), 0.68, 2.60, fin=0.003), 0)], fade_out=0.4)


def sabado_eureka_2() -> np.ndarray:  # second take, rotates weekly
    return timeline(1.1, [(0.0, cut(load("sabado-eureka2.mp3"), 0.0, 1.10, fin=0.003), 0)], fade_out=0.3)


def sabado_espacio() -> np.ndarray:  # space ambience swelling in (space topics)
    return timeline(3.6, [(0.0, cut(load("sabado-espacio.mp3"), 1.2, 4.8, fin=0.05), 0)], fade_out=1.0)


def sabado_espacio_2() -> np.ndarray:  # second take, rotates weekly
    return timeline(3.6, [(0.0, cut(load("sabado-espacio2.mp3"), 0.4, 4.4, fin=0.6), 0)], fade_out=1.2)


def sabado_mito() -> np.ndarray:  # ¿Mito o Ciencia? verdict: Mito
    return timeline(1.4, [(0.0, cut(load("sabado-mito.mp3"), 0.0, 1.40, fin=0.003), 0)], fade_out=0.4)


# ---------------------------------------------------------------- Viernes de Variedad
def viernes_telenovela() -> np.ndarray:  # the dramatic "¡tan tan tán!"
    return timeline(4.0, [(0.0, cut(load("viernes-telenovela.mp3"), 0.45, 4.45, fin=0.005), 0)], fade_out=1.2)


def viernes_sospecha() -> np.ndarray:  # someone is hiding something…
    return timeline(1.6, [(0.0, cut(load("viernes-sospecha.mp3"), 0.0, 1.62, fin=0.01), 0)], fade_out=0.4)


def viernes_suspenso() -> np.ndarray:
    return timeline(3.2, [(0.0, cut(load("viernes-suspenso.mp3"), 0.28, 3.48, fin=0.005), 0)], fade_out=1.0)


def viernes_trueno() -> np.ndarray:
    return timeline(3.4, [(0.0, cut(load("viernes-trueno.mp3"), 0.15, 3.55, fin=0.05), 0)], fade_out=1.2)


def viernes_fin() -> np.ndarray:  # sad trombone "wah wah wah"
    return timeline(4.8, [(0.0, cut(load("viernes-fin.mp3"), 0.18, 5.00, fin=0.01), 0)], fade_out=0.6)


def viernes_risas() -> np.ndarray:  # a small, natural laugh (use sparingly)
    return timeline(3.2, [(0.0, cut(load("viernes-risas.mp3"), 0.30, 3.50, fin=0.15), 0)], fade_out=1.2)


def viernes_maquina() -> np.ndarray:  # typing, the margin bell, carriage return: Historia con sabor
    src = load("viernes-maquina.mp3")
    typing = cut(src, 1.80, 3.60, fin=0.05, fout=0.05)
    bell = cut(src, 23.15, 23.80, fin=0.003, fout=0.2)
    ret = cut(src, 18.10, 18.95, fin=0.01, fout=0.1)
    x = timeline(3.4, [(0.0, typing, 0), (1.85, bell, 2), (2.35, ret, 0)], fade_out=0.3)
    x = x / (np.max(np.abs(x)) + 1e-9)
    return (np.tanh(6 * x) / np.tanh(6)).astype(np.float32)  # tame the key clicks so it isn't too quiet


def viernes_pagina() -> np.ndarray:  # turning the page
    return timeline(1.2, [(0.0, cut(load("viernes-pagina.mp3"), 1.15, 2.30, fin=0.01), 0)], fade_out=0.2)


# ---------------------------------------------------------------- Agenda Cultural (Tuesday)
def martes_diva() -> np.ndarray:  # heels walking in: Sophie's entrance
    return timeline(2.8, [(0.0, cut(load("martes-tacones.mp3"), 0.0, 2.85, fin=0.003), 0)], fade_out=0.5)


def martes_cine() -> np.ndarray:  # clapperboard, then the old projector rolling
    clap = cut(load("martes-claqueta.mp3"), 0.03, 0.58, fin=0.002)
    proj = cut(load("martes-proyector.mp3"), 1.0, 3.6, fin=0.4)
    return timeline(2.8, [(0.0, clap, 0), (0.35, proj, 14)], fade_out=0.9)


def martes_vinil() -> np.ndarray:  # needle drop (the second one in the source) + a little crackle
    src = load("martes-vinil.mp3")
    drop = cut(src, 1.25, 1.90, fin=0.003, fout=0.15)
    crackle = cut(src, 6.0, 8.0, fin=0.2)
    return timeline(2.3, [(0.0, drop, 0), (0.45, crackle, 8)], fade_out=0.7)


def martes_chisme() -> np.ndarray:  # the "¡uuuy!" before the chisme
    return timeline(1.5, [(0.0, cut(load("martes-chisme.mp3"), 0.05, 1.50, fin=0.05), 0)], fade_out=0.3)


def martes_evento() -> np.ndarray:  # crowd before a concert: el evento local
    return timeline(2.9, [(0.0, cut(load("martes-boletos.mp3"), 0.10, 3.00, fin=0.15), 0)], fade_out=1.0)


# ---------------------------------------------------------------- Monday
def lunes_reloj() -> np.ndarray:  # serious ticking to open El Tema de la Semana
    return timeline(3.2, [(0.0, cut(load("lunes-reloj.mp3"), 0.0, 3.30, fin=0.002), 0)], fade_out=0.8)


def _papeles(start: float, end: float) -> np.ndarray:  # papers shuffling: "a ver qué trae la semana"
    return timeline(end - start, [(0.0, cut(load("lunes-papeles.mp3"), start, end, fin=0.08), 0)], fade_out=0.4)


# ---------------------------------------------------------------- weather (cold open), by forecast
def _clip(name: str, start: float, end: float, fin: float = 0.2, fade_out: float = 0.8) -> np.ndarray:
    return timeline(end - start, [(0.0, cut(load(name), start, end, fin=fin), 0)], fade_out=fade_out)


def clima() -> np.ndarray:  # wind chimes: a normal day
    return _clip("general-clima.mp3", 0.2, 3.4, fin=0.05, fade_out=1.0)


def clima_lluvia() -> np.ndarray:  # soft rain: some chance of rain or snow
    return _clip("general-lluviasuave.mp3", 2.0, 5.5, fin=0.6, fade_out=1.2)


def clima_tormenta() -> np.ndarray:  # heavy rain
    return _clip("general-lluviafuerte.mp3", 2.0, 5.5, fin=0.5, fade_out=1.2)


def clima_truenos() -> np.ndarray:  # rain with a thunder crack: thunderstorms in the forecast
    return _clip("general-lluviatruenos.mp3", 1.0, 5.2, fin=0.5, fade_out=1.4)


# ---------------------------------------------------------------- more Monday / Friday
def lunes_mazo() -> np.ndarray:  # gavel: council and legislature meetings in Lo que viene
    return _clip("lunes-mazo.mp3", 0.85, 1.85, fin=0.003, fade_out=0.3)


def viernes_aullido() -> np.ndarray:
    return _clip("viernes-aullido.mp3", 0.15, 3.95, fin=0.05, fade_out=1.0)


def viernes_caballo() -> np.ndarray:
    return _clip("viernes-caballo.mp3", 1.40, 4.30, fin=0.05, fade_out=1.0)


def viernes_puerta_abrir() -> np.ndarray:
    return _clip("viernes-puertaabrir.mp3", 0.0, 2.30, fin=0.01, fade_out=0.4)


def viernes_puerta_cerrar() -> np.ndarray:
    return _clip("viernes-puertacerrar.mp3", 0.45, 1.00, fin=0.005, fade_out=0.15)


def viernes_puerta_rechinido() -> np.ndarray:
    return _clip("viernes-puertarechinido.mp3", 0.0, 0.90, fin=0.01, fade_out=0.2)


def viernes_puerta_tocar() -> np.ndarray:
    return _clip("viernes-puertatocar.mp3", 0.0, 0.85, fin=0.003, fade_out=0.1)


def viernes_telefono() -> np.ndarray:  # old phone ringing once
    return _clip("viernes-telefonoviejo.mp3", 0.0, 3.60, fin=0.003, fade_out=0.6)


def llamada() -> np.ndarray:  # ringback tones: a cast member calling into the studio
    return _clip("viernes-telefonollamada.mp3", 0.05, 3.70, fin=0.003, fade_out=0.3)


# ---------------------------------------------------------------- accidents, cars, Chino's late arrival
def caida_papel() -> np.ndarray:  # papers slipping off the desk (second take of the source)
    return _clip("general-caidapapel.mp3", 3.05, 4.40, fin=0.01, fade_out=0.4)


def caida_papel_2() -> np.ndarray:  # third take; the build rotates them weekly
    return _clip("general-caidapapel.mp3", 4.75, 6.30, fin=0.01, fade_out=0.4)


def caida_micro() -> np.ndarray:  # a mic hitting the floor
    return _clip("general-caidamicro.mp3", 0.12, 1.15, fin=0.003, fade_out=0.3)


def caida_chino() -> np.ndarray:  # someone tripping
    return _clip("general-caidachino.mp3", 0.0, 1.25, fin=0.003, fade_out=0.3)


def carro_arranca() -> np.ndarray:
    return _clip("general-carroarrancaymaneja.mp3", 1.10, 6.00, fin=0.02, fade_out=1.4)


def carro_acelera() -> np.ndarray:  # from inside the car
    return _clip("general-carroaceleradentro.mp3", 1.10, 5.00, fin=0.05, fade_out=1.2)


def carro_freno() -> np.ndarray:
    return _clip("general-carrofreno.mp3", 0.40, 3.60, fin=0.01, fade_out=0.8)


def carro_claxon() -> np.ndarray:
    return _clip("general-carroclaxon.mp3", 0.0, 0.65, fin=0.003, fade_out=0.1)


def carro_puerta() -> np.ndarray:
    return _clip("general-carropuerta.mp3", 0.0, 0.45, fin=0.002, fade_out=0.1)


def chino_llega_tarde() -> np.ndarray:  # screech, car door, a stumble at the studio door
    freno = cut(load("general-carrofreno.mp3"), 0.40, 2.60, fin=0.01, fout=0.5)
    puerta = cut(load("general-carropuerta.mp3"), 0.0, 0.45, fin=0.002, fout=0.08)
    caida = cut(load("general-caidachino.mp3"), 0.0, 1.25, fin=0.003, fout=0.25)
    return timeline(4.6, [(0.0, freno, 0), (2.35, puerta, 2), (3.25, caida, 3)], fade_out=0.3)


# Quieter targets for sounds that should sit under the voices.
LEVEL = {"caida-papel": -22.0, "caida-papel-2": -22.0, "carro-claxon": -22.0, "clima": -23.0, "clima-lluvia": -24.0, "clima-tormenta": -23.0, "clima-truenos": -21.0, "lunes-mazo": -22.0, "viernes-puerta-rechinido": -22.0, "llamada": -22.0, "viernes-telefono": -21.0, "lunes-reloj": -21.0, "lunes-papeles": -22.0, "lunes-papeles-2": -22.0, "lunes-papeles-3": -22.0, "lunes-papeles-4": -22.0, "martes-diva": -21.0, "martes-chisme": -21.0, "viernes-risas": -22.0, "viernes-pagina": -21.0, "sabado-espacio": -21.0, "sabado-espacio-2": -21.0, "sabado-burbujas": -21.0, "grillos": -24.0, "bueno": -20.0, "alerta": -20.0, "consulta": -21.0, "campanilla": -21.0, "escribiendo": -22.0}

RECIPES = {
    # Every day
    "alerta": alerta, "bueno": bueno, "rimshot": rimshot, "grillos": grillos,
    "scratch": scratch, "scratch-2": scratch_2, "aplausos": aplausos, "aplausos-chico": aplausos_chico,
    "consulta": consulta, "campanilla": campanilla, "escribiendo": escribiendo,
    # Accidents, cars, Chino's late arrival
    "caida-papel": caida_papel, "caida-papel-2": caida_papel_2, "caida-micro": caida_micro, "caida-chino": caida_chino,
    "carro-arranca": carro_arranca, "carro-acelera": carro_acelera, "carro-freno": carro_freno,
    "carro-claxon": carro_claxon, "carro-puerta": carro_puerta, "chino-llega-tarde": chino_llega_tarde,
    # Weather intro in the cold open (pick by the forecast)
    "clima": clima, "clima-lluvia": clima_lluvia, "clima-tormenta": clima_tormenta, "clima-truenos": clima_truenos,
    "llamada": llamada,
    "lunes-mazo": lunes_mazo,
    "viernes-aullido": viernes_aullido, "viernes-caballo": viernes_caballo,
    "viernes-puerta-abrir": viernes_puerta_abrir, "viernes-puerta-cerrar": viernes_puerta_cerrar,
    "viernes-puerta-rechinido": viernes_puerta_rechinido, "viernes-puerta-tocar": viernes_puerta_tocar,
    "viernes-telefono": viernes_telefono,
    # Monday (papeles has 4 takes that rotate weekly)
    "lunes-reloj": lunes_reloj,
    "lunes-papeles": lambda: _papeles(0.90, 2.40), "lunes-papeles-2": lambda: _papeles(15.45, 17.00),
    "lunes-papeles-3": lambda: _papeles(19.70, 21.20), "lunes-papeles-4": lambda: _papeles(23.20, 25.00),
    # Agenda Cultural (Tuesday)
    "martes-diva": martes_diva, "martes-cine": martes_cine, "martes-vinil": martes_vinil,
    "martes-chisme": martes_chisme, "martes-evento": martes_evento,
    # Viernes de Variedad
    "viernes-telenovela": viernes_telenovela, "viernes-sospecha": viernes_sospecha, "viernes-suspenso": viernes_suspenso,
    "viernes-trueno": viernes_trueno, "viernes-fin": viernes_fin, "viernes-risas": viernes_risas,
    "viernes-maquina": viernes_maquina, "viernes-pagina": viernes_pagina,
    # Sábados Científicos (Ciencia verdict = tech-si-vale; Ciencia en NM close = tech-nm)
    "sabado-burbujas": sabado_burbujas, "sabado-eureka": sabado_eureka, "sabado-eureka-2": sabado_eureka_2,
    "sabado-espacio": sabado_espacio, "sabado-espacio-2": sabado_espacio_2, "sabado-mito": sabado_mito,
    "sabado-ciencia": tech_si_vale, "sabado-nm": tech_nm,
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
    target = LEVEL.get(name, TARGET_LUFS)
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.5
    with tempfile.TemporaryDirectory() as tmp:
        wav = Path(tmp) / f"{name}.wav"
        write_wav(wav, x)
        # Very peaky clips (heels, a clapperboard, a needle drop) can't reach the target under the
        # -2 dBFS ceiling: soften the transients a little at a time until they get within 3 dB.
        for drive in (2, 3, 4, 6, 8):
            reachable = -2.0 - 20 * np.log10(np.max(np.abs(x)) + 1e-9) + integrated_lufs(wav)
            if reachable >= target - 3:
                break
            y = x / (np.max(np.abs(x)) + 1e-9)
            x = (np.tanh(drive * y) / np.tanh(drive) * 0.5).astype(np.float32)
            write_wav(wav, x)
        gain = target - integrated_lufs(wav)
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
