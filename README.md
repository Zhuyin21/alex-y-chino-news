# alex-y-chino-news

Spanglish news podcast for the Albuquerque commute, **~30 min, Monday to Saturday**: ~7 min of New Mexico, US and world news with Doc and Chino, then a **~18-minute segment of the day**: El Tema de la Semana (Mon), Agenda Cultural with Sophie (Tue), Miércoles en La Cancha (Wed), Tech Thursday (Thu), Viernes de Variedad (Fri) and Sábados Científicos with Ashley (Sat). Auto-generated scripts, AI voices, RSS feed. Lineup and cast: `PROGRAMACION.md`.

## How it works

1. **4:22 am MT, the script:** a Claude scheduled task researches the day's news, writes the episode script plus show notes with sources, and commits it to `episodes/`.
2. **~5:50 am, the audio:** a GitHub Action picks up the new script, sends it to Gemini's multi-speaker text-to-speech API, stitches the segments into one MP3, and updates the RSS feed. The MP3 is attached to a GitHub Release, and `docs/feed.xml` is served by GitHub Pages.
3. **~6:15 am, the phone:** AntennaPod downloads the new episode over Wi-Fi.
4. **7:00 am:** Bluetooth connects in the car and you press Play.

## Repo layout

| Path | What's in it |
|---|---|
| `SHOW_BIBLE.md` | Hosts, show format, editorial and sourcing rules. The source of truth for every episode. |
| `PROGRAMACION.md` | The weekly lineup: segment of each day, the cast (Ashley, Sophie, producción), running bits. |
| `SABADO_TECH.md` | Rules for Sábados Científicos (old file name). |
| `episodes/` | One Markdown script per day: `YYYY-MM-DD_episode-NNN.md` |
| `pipeline/` | `build_episode.py` (script → MP3 via Gemini TTS), `build_feed.py` (RSS) |
| `.github/workflows/audio.yml` | Runs on every new episode, and can also be triggered manually |
| `docs/` | `feed.xml` + `episodes.json`, served by GitHub Pages |

## Script format

Each spoken line looks like this:

```
SPEAKER [delivery style]: text
```

The delivery style goes to the TTS as styling and is never read aloud.

## Podcast feed

Subscribe in AntennaPod: `https://zhuyin21.github.io/alex-y-chino-news/feed.xml`

## One-time setup
1. **Secret:** Settings → Secrets and variables → Actions → `GEMINI_API_KEY`
2. **Optional free key:** add a key from a Google project *without billing* as secret `GEMINI_API_KEY_FREE`. The build tries it first and falls back to the paid `GEMINI_API_KEY` if the free quota runs out.
3. **Pages:** Settings → Pages → Deploy from a branch → `main` / `/docs`
4. **Test:** Actions → *Build episode audio + feed* → Run workflow

**Voices:** Alex = Algenib, Chino = Fenrir by default. To change them without editing code, add repository variables `VOICE_ALEX` / `VOICE_CHINO` (Settings → Secrets and variables → Actions → Variables). To compare voices, run *Voice audition* with pairs like `Algenib:Fenrir,Algenib:Achird`.

## Listener input (GitHub issues)
- `Pregunta: …` → answered in **Pregúntale a Doc** on Saturday (e.g., *"Pregunta: ¿cómo funcionan los paneles solares cuando está nublado?"*).
- `Tema: …` → the main topic Ashley presents on **Sábados Científicos**.
- `Tech: …` → a product for **¿Vale la pena?** or a breakthrough for **El Avance de la Semana** on Tech Thursday.

## Theme music library
Every episode picks its theme music **at random** from `assets/music/library/` (about 30 genres; no genre repeats within 4 episodes and no pack within 30 days; December-only family-party packs in December), recorded in `docs/episodes.json`. Each pack is a 30-second Lyria theme (about $0.04) cut into an intro, stings and an outro. *Theme music library* adds one pack every Sunday for the genre with the fewest; run it with `batch` to fill every genre at once, or with a genre to add one. To pin a favorite, set the repo variable `MUSIC_PACK` to a folder name (e.g. `2026-11-07_salsa`). Each pack's `sting-serious.mp3` is a softer cut of the same theme, used before hard news.
