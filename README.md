# alex-y-chino-news

Daily Spanglish news podcast. Dr. Alex y Chino break down local (Albuquerque/Bernalillo), US, and world news. Auto-generated scripts, AI voices, RSS feed for AntennaPod.

## How it works

1. **5:15 am MT, the script:** a Claude scheduled task researches the day's news, writes the episode script plus show notes with sources, and commits it to `episodes/`.
2. **~5:50 am, the audio:** a GitHub Action picks up the new script, sends it to Gemini's multi-speaker text-to-speech API, stitches the segments into one MP3, and updates the RSS feed. The MP3 is attached to a GitHub Release, and `docs/feed.xml` is served by GitHub Pages.
3. **~6:15 am, the phone:** AntennaPod downloads the new episode over Wi-Fi.
4. **7:00 am:** Bluetooth connects in the car and you press Play.

## Repo layout

| Path | What's in it |
|---|---|
| `SHOW_BIBLE.md` | Hosts, show format, editorial and sourcing rules. The source of truth for every episode. |
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
2. **Pages:** Settings → Pages → Deploy from a branch → `main` / `/docs`
3. **Test:** Actions → *Build episode audio + feed* → Run workflow

**Voices:** Alex = Algenib, Chino = Fenrir by default. To change them without editing code, add repository variables `VOICE_ALEX` / `VOICE_CHINO` (Settings → Secrets and variables → Actions → Variables). To compare voices, run *Voice audition* with pairs like `Algenib:Fenrir,Algenib:Achird`.

## Sábado de Tech
Every Saturday there's a tech, science and engineering special in the same feed. See `SABADO_TECH.md` for its rules.
**Ask Doc a question:** open an issue whose title starts with `Pregunta:` (for example, *"Pregunta: ¿cómo funcionan los paneles solares cuando está nublado?"*). Questions opened during the week can be answered in that Saturday's "Pregúntale a Doc" segment.
