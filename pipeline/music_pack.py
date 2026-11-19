#!/usr/bin/env python3
"""Theme-music packs: generate a 30-second Lyria clip in a genre, cut it into intro / sting / outro,
and save it to the music library. Since Nov 2026 every episode picks a pack AT RANDOM from the whole
library (build_episode.py, with a record in docs/episodes.json so genres and packs don't repeat too soon).

    python pipeline/music_pack.py --batch 30      # create packs for genres that don't have one yet
    python pipeline/music_pack.py --grow          # one new pack for the genre with the fewest (weekly job)
    python pipeline/music_pack.py --genre salsa   # force a genre
    python pipeline/music_pack.py --list          # genres and how many packs each has

Library layout:
    assets/music/library/<YYYY-MM-DD>_<genre>/{intro,sting,outro}.mp3 + pack.json
    assets/music/current.json  -> {"pack": "<YYYY-MM-DD>_<genre>"}
Each pack also has sting-serious.mp3: a softer, quieter cut of the same theme used before hard news.
Costs ~$0.04 per pack (one Lyria clip) on the paid key.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
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

# Genres (no country, per the host's request). Prompts name genres and instruments only, never artists.
# Mexico and the border first, then the rest of Latin America, the Caribbean, Brazil, Africa and Cape Verde.
GENRES: dict[str, str] = {
    "norteno-upbeat": "Upbeat modern norteño instrumental: lead button accordion, bajo sexto, electric bass, "
                      "snare-driven polka rhythm, 120 BPM, D major, festive.",
    "norteno-old-school": "Classic 1970s norteño instrumental with a cantina feel: two-row button accordion melody in "
                          "thirds, bajo sexto, upright-style bass, simple snare and brushes, polka-redova rhythm, "
                          "118 BPM, G major, warm and nostalgic but upbeat.",
    "corrido-tumbado": "Modern Mexican regional corrido tumbado instrumental: bright requinto guitar riffs, "
                       "acoustic twelve-string guitar, tuba bass line, light trap hi-hats and 808 under a "
                       "regional Mexican groove, 95 BPM, A minor, confident and cool.",
    "banda-sinaloense": "Festive banda sinaloense instrumental: brass band with trumpets, trombones, clarinets, "
                        "sousaphone bass line, tambora and snare, fast quebradita feel, 140 BPM, F major, loud and joyful.",
    "mariachi": "Joyful mariachi instrumental: bright trumpets, violin section, vihuela and guitarrón, "
                "lively son jalisciense rhythm, 130 BPM, G major, celebratory.",
    "huapango": "Lively huapango huasteco instrumental: virtuosic violin melody, jarana huasteca and quinta huapanguera "
                "strumming, syncopated sesquiáltera rhythm, 120 BPM, D major, playful and bright.",
    "nuevo-mexicano": "Classic New Mexico Spanish dance-hall instrumental from the 1970s and 80s: electric organ and "
                      "button accordion trading the melody, electric guitar, bass, drums, a cheerful ranchera-polka "
                      "and cumbia blend from Northern New Mexico weddings, 122 BPM, C major, homey and festive.",
    "tejano": "Upbeat Tejano instrumental: synth keyboard lead, button accordion, electric bass, drums with a "
              "cumbia-polka groove, 1990s border dance-hall energy, 110 BPM, A major, bright and danceable.",
    "cumbia": "Upbeat cumbia instrumental with a Mexican sonidero feel: accordion melody, güiro, congas, "
              "electric bass, steady cumbia rhythm, 98 BPM, C major, danceable and warm.",
    "cumbia-rebajada": "Cumbia rebajada instrumental from northern Mexico: slowed-down cumbia groove, deep "
                       "heavy bass, accordion melody, güiro, laid-back and hypnotic but upbeat, 80 BPM, E minor.",
    "cumbia-sonidera": "Psychedelic cumbia sonidera instrumental: wah-wah electric guitar and vintage synth lead, "
                       "timbales, güiro, congas, punchy bass, echo effects, 96 BPM, D minor, party energy.",
    "reggaeton": "Modern reggaeton instrumental: dembow drum pattern, deep 808 bass, bright plucked synth hook, "
                 "Latin percussion accents, 94 BPM, F minor, catchy and confident.",
    "rock-en-espanol": "1990s rock en español instrumental: jangly electric guitars, driving bass, live drums, "
                       "a melodic lead guitar hook with a touch of Latin percussion, 128 BPM, E major, anthemic and upbeat.",
    "salsa": "Energetic salsa instrumental: piano montuno, congas, timbales, bongos, punchy brass section, "
             "clave rhythm, 180 BPM, F major, joyful and driving.",
    "son-cubano": "Classic son cubano instrumental: tres guitar lead, upright bass, bongos, maracas, claves, "
                  "muted trumpet answering the tres, 104 BPM, C major, sunny and elegant.",
    "cha-cha-cha": "Playful cha-cha-chá instrumental: flute and violin melody, piano guajeo, güiro, congas, "
                   "timbales, 116 BPM, G major, light and smiling.",
    "bachata": "Upbeat modern bachata instrumental: bright requinto guitar lead, rhythm guitar, bongos, "
               "güira, electric bass, 128 BPM, B minor, romantic but energetic.",
    "merengue": "Fast, joyful merengue instrumental: tambora, güira, accordion and saxophone lead, "
                "electric bass, 150 BPM, G major, party energy.",
    "vallenato": "Upbeat Colombian vallenato instrumental: diatonic accordion lead, caja vallenata drum, guacharaca "
                 "scraper, electric bass, 112 BPM, A major, cheerful.",
    "samba": "Brazilian samba instrumental: surdo, tamborim, pandeiro, agogô and cuíca, cavaquinho strumming, "
             "a bright brass hook, 100 BPM, D major, carnival joy.",
    "forro": "Brazilian forró instrumental: accordion melody, zabumba drum, triangle, bouncy baião rhythm, "
             "118 BPM, G major, rustic and joyful.",
    "kompa": "Haitian kompa instrumental: smooth electric guitar riffs, warm synth pads, steady kompa drum groove "
             "with cowbell, rolling bass, 112 BPM, C major, sunny and danceable.",
    "funana": "Cape Verdean funaná instrumental: fast diatonic accordion (gaita) melody, ferrinho scraper, electric "
              "bass, driving drums, 140 BPM, A major, high energy and joyful.",
    "reggae": "Upbeat roots reggae instrumental: offbeat guitar skank, organ bubble, deep round bass line, "
              "one-drop drums, a melodica hook, 80 BPM, G major, sunny and relaxed.",
    "dancehall": "Modern dancehall instrumental: syncopated dancehall drum riddim, deep bass, bright synth stabs, "
                 "steel-drum-like melody, 100 BPM, E minor, party energy.",
    "soca": "Trinidad soca instrumental: fast four-on-the-floor groove, steel pan melody, brass hits, rolling bass, "
            "160 BPM, F major, carnival energy.",
    "afrobeats": "Modern afrobeats instrumental: log drums and shakers, syncopated percussion, warm bass, bright "
                 "guitar licks and a catchy synth hook, 108 BPM, A minor, feel-good.",
    "highlife": "West African highlife instrumental: interlocking bright electric guitars, horn section, congas and "
                "bell pattern, 118 BPM, D major, joyful and open.",
    "west-african-drums": "West African drum ensemble instrumental: djembe lead, dunun drums, bells and shakers in "
                          "interlocking rhythms, a kora melody on top, 120 BPM, D major, powerful and celebratory.",
    "soukous": "Congolese soukous instrumental: fast sparkling high electric guitar lines, rolling bass, crisp "
               "snare and hi-hat, 135 BPM, E major, dance-floor energy.",
    # December only: family-party sounds that feel like the holidays at home, not Christmas carols.
    "sonora-tropical": "Classic tropical cumbia orchestra instrumental (sonora style): bright trumpets and saxophones, "
                       "piano, güiro, congas and timbales, festive family-party cumbia, 104 BPM, G major, nostalgic and joyful.",
    "grupera-fiesta": "1990s Mexican grupera party instrumental: synth keyboard lead with a warm organ tone, electric "
                      "bass, cumbia drums, festive family-gathering feel, 100 BPM, D major, sweet and danceable.",
    "banda-navidena": "Warm Mexican brass-band instrumental for a family December party: trumpets, clarinets, tuba and "
                      "tambora with sleigh-bell-like shakers, cheerful polka feel, no carols, 126 BPM, B-flat major.",
}
# Genres used only in December (build_episode.py gives them more weight then and skips them the rest of the year).
SEASONAL = {"sonora-tropical": "december", "grupera-fiesta": "december", "banda-navidena": "december"}


def packs_by_genre() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {g: [] for g in GENRES}
    for d in sorted(LIB.glob("*_*")):
        g = re.sub(r"-\d+$", "", d.name.split("_", 1)[1])
        if g in out and (d / "intro.mp3").exists():
            out[g].append(d.name)
    return out


ROTATION_OFFSET = 7  # aligns ISO week 46 (Nov 9-14, 2026) with salsa, the first pack we made


def week_genre(today: dt.date) -> str:
    """Genre for the episode week that starts on the next Monday (the Sunday run sets up Mon–Sat)."""
    names = list(GENRES)
    return names[((today + dt.timedelta(days=1)).isocalendar().week + ROTATION_OFFSET) % len(names)]


def recent_pack(genre: str, today: dt.date, days: int = 7) -> str | None:
    """A pack of this genre created in the last `days` days (reuse it instead of paying again)."""
    for d in sorted(LIB.glob(f"*_{genre}"), reverse=True):
        try:
            created = dt.date.fromisoformat(d.name.split("_", 1)[0])
        except ValueError:
            continue
        if (today - created).days <= days and (d / "intro.mp3").exists():
            return d.name
    return None


# Stings come from different parts of the track so transitions don't all sound identical.
STING_STARTS = [0.0, 8.5, 16.0, 22.5]


def cut_pack(raw: Path, out: Path, work: Path) -> None:
    total = duration(raw)
    outro_len = min(9.3, total - 1)
    cut(raw, out / "intro.mp3", 0, 8.0, 0.05, 1.8, work)
    for n, start in enumerate(s for s in STING_STARTS if s + 3.2 < total):
        name = "sting.mp3" if n == 0 else f"sting-{n + 1}.mp3"
        cut(raw, out / name, start, 3.2, 0.05 if n == 0 else 0.15, 1.2, work)
    cut(raw, out / "outro.mp3", max(0.0, total - outro_len), outro_len, 0.6, 0.4, work)
    # "Serious" transition: a short, softer cut of the same theme (slow fade in, long fade out, a bit quieter).
    cut(raw, out / "sting-serious.mp3", 12.0, 4.0, 0.6, 2.4, work, level=TARGET_LUFS - 4)


def loudness(path: Path) -> float:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    vals = [ln.split()[1] for ln in out.splitlines() if ln.strip().startswith("I:")]
    return float(vals[-1])


def duration(path: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(path)], capture_output=True, text=True, check=True).stdout.strip())


def cut(src: Path, dst: Path, start: float, length: float, fade_in: float, fade_out: float, work: Path,
        level: float = TARGET_LUFS) -> None:
    tmp = work / f"tmp_{dst.stem}.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{length:.2f}", "-i", str(src),
                    "-af", f"afade=t=in:d={fade_in},afade=t=out:st={length - fade_out:.2f}:d={fade_out}",
                    "-ar", "44100", "-ac", "2", str(tmp)], check=True)
    gain = round(level - loudness(tmp), 2)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp),
                    "-af", f"volume={gain}dB,alimiter=limit=0.95", "-c:a", "libmp3lame", "-b:a", "160k", str(dst)],
                   check=True)


def create(genre: str, today: dt.date, activate: bool) -> str:
    from google import genai

    prompt = f"{GENRES[genre]} {_TAIL}"
    name = f"{today.isoformat()}_{genre}"
    n = 2
    while (LIB / name).exists():  # a second pack of the same genre on the same day
        name, n = f"{today.isoformat()}_{genre}-{n}", n + 1
    out = LIB / name
    out.mkdir(parents=True, exist_ok=True)
    client = genai.Client()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        raw = work / "raw.mp3"
        model = generate(client, prompt, raw)
        cut_pack(raw, out, work)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-c:a", "libmp3lame", "-b:a", "128k",
                        str(out / "full.mp3")], check=True)
    info = {"pack": name, "genre": genre, "created": today.isoformat(), "model": model, "prompt": prompt}
    if genre in SEASONAL:
        info["seasonal"] = SEASONAL[genre]
    (out / "pack.json").write_text(json.dumps(info, indent=2, ensure_ascii=False) + "\n")
    if activate:
        CURRENT.write_text(json.dumps({"pack": name}, indent=2) + "\n")
    print(f"Created music pack {name} ({model})", flush=True)
    return name


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, metavar="N", help="create packs for up to N genres that have none yet")
    ap.add_argument("--grow", action="store_true", help="one new pack for the genre with the fewest packs")
    ap.add_argument("--genre", choices=list(GENRES))
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--no-activate", action="store_true", help="add to library without making it current")
    ap.add_argument("--recut", metavar="PACK", help="re-cut an existing pack from its full.mp3 (no API call)")
    args = ap.parse_args()

    today = dt.date.today()
    if args.list:
        for g, packs in packs_by_genre().items():
            print(f"{g:22s} {len(packs)} pack(s)" + (f"  [{SEASONAL[g]}]" if g in SEASONAL else ""))
        return 0

    if args.batch:
        missing = [g for g, packs in packs_by_genre().items() if not packs][: args.batch]
        print(f"Creating {len(missing)} packs: {', '.join(missing)}", flush=True)
        failed = []
        for g in missing:
            try:
                create(g, today, activate=False)
            except Exception as e:  # noqa: BLE001 - keep going; the rest of the batch still counts
                print(f"  {g}: failed ({str(e)[:160]})", flush=True)
                failed.append(g)
        print(f"Done: {len(missing) - len(failed)} created" + (f", failed: {', '.join(failed)}" if failed else ""))
        return 0

    if args.grow:
        counts = packs_by_genre()
        g = min((g for g in GENRES if g not in SEASONAL or today.month in (11, 12)), key=lambda g: len(counts[g]))
        create(g, today, activate=False)
        return 0

    if args.recut:
        out = LIB / args.recut
        with tempfile.TemporaryDirectory() as tmp:
            cut_pack(out / "full.mp3", out, Path(tmp))
        print(f"Re-cut {args.recut}: " + ", ".join(sorted(p.name for p in out.glob("*.mp3"))))
        return 0

    genre = args.genre or week_genre(today)
    if not args.genre:
        existing = recent_pack(genre, today)
        if existing:
            if not args.no_activate:
                CURRENT.write_text(json.dumps({"pack": existing}, indent=2) + "\n")
            print(f"Reusing this week's {genre} pack {existing} (no new generation needed)")
            return 0
    create(genre, today, activate=not args.no_activate)
    return 0


if __name__ == "__main__":
    sys.exit(main())
