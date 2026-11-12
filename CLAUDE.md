# Instructions for Claude

This repo produces a daily news podcast. Before writing or editing any episode, read `SHOW_BIBLE.md` **and `PROGRAMACION.md`** and follow them exactly.
- **Monday to Saturday (from Thu Nov 12, 2026): ~30 min every day** = ~10 min of news (Tue–Sat with the spoken transitions "la noticia local del día" / "el rapid fire…"; Monday longer, separated by music) + a **~15-minute segment of the day** (Mon El Tema de la Semana, Tue Agenda Cultural with Sophie, Wed Miércoles en La Cancha + Chino's quiniela, Thu Tech Thursday, Fri La Radionovela, Sat Sábados Científicos) + **Lo Bueno del Día**. Format, transitions and weather in SHOW_BIBLE.md "Format, Monday to Saturday"; segments, cast and running bits in PROGRAMACION.md.
- **Saturdays:** also read `SABADO_TECH.md` (old file name) for the science segment rules.
- **If a scheduled-task prompt quotes an older format** (10–15 or 15–20 min, "5 stories per section", "Sábado de Tech", El Taller), **the repo files win**: follow SHOW_BIBLE.md, PROGRAMACION.md and SABADO_TECH.md as they are now.

- **File names and numbering.** The daily show and Sábado de Tech are numbered separately:
  - **Daily (Mon–Fri):** `episodes/YYYY-MM-DD_episode-NNN.md`. NNN is one higher than the highest daily episode number. **Ignore `2026-11-07_episode-002.md`**: that's Sábado de Tech #1, filed under an old name. The daily show starts at **episode 001 on Monday, Nov 9, 2026** (the earlier test episodes live in `pilots/` and don't count). Front matter `episode: 1`, title `Ep 1: …`.
  - **Saturdays (Sábados Científicos):** `episodes/YYYY-MM-DD_sabado-NNN.md`. NNN is one higher than the highest `sabado-NNN`. With none yet, use **002** (#1 was Sábado de Tech, `2026-11-07_episode-002.md`). Front matter `episode: sabado-N`; the heading says `Sábados Científicos #N`.
  - "Already produced" check: any `episodes/<air_date>_*.md`.
- `pilots/` holds test episodes. Don't build, number or reference them.
- Use the front matter and line format from the previous episode (`SPEAKER [style]: text`). The TTS pipeline parses this format.
- Check yesterday's episode so you don't repeat stories without a real update.
- Verify every fact against sources you fetched in this session. Don't fill gaps from memory.
- **Before committing an episode, self-check the voice against SHOW_BIBLE.md "How they talk":**
  - Chino is about 70% Spanish / 30% English overall (real Juárez Spanish, whole sentences, not sprinkled words), and laughs on a good number of his lighter lines (style tags).
  - Doc is about 60% English / 40% Spanish, with New Mexican touches and 2–3 natural dry jokes per episode (none in serious segments).
  - The respect rule holds: never "no mames" or "wey" aimed at Doc.
  - No transition is repeated, and the serious segments have no jokes.
  - It sounds like a conversation (SHOW_BIBLE "Sound like a real conversation"): ~4–6 backchannels (mm-hmm, ajá, órale), 2–3 friendly interruptions, at most 1 harmless self-correction that ends on the right fact, and none of that in serious segments except quiet backchannels.
  - **Cast (PROGRAMACION.md):** Ashley ~70% English with a gringa accent in Spanish, at most one Spanish stumble, never repeating a line in both languages. Sophie (Tuesdays only) almost all Spanish, playful with Chino but never flirty, and every unconfirmed item is called "puro rumor" on air. Cameos are 1–3 lines and set up by the line before. Producción never speaks. Follow SHOW_BIBLE "Guests and cameos" so voices don't mix.
  - Rivalries (Cowboys/Broncos, Jordan/Curry, Samsung/weird phones/iPhone) are seasoning: 1–2 moments per segment, and the hosts agree on plenty.
  - **Structure:** the news uses the spoken transitions (Tue–Sat) or music separators (Mon); the segment of the day ends with something local; Lo Bueno del Día fits the day's theme; the weather gives °F and °C, humidity and rain chance (AQI/pollen when they matter).
  - Rewrite any line that reads like an English news script with Spanish sprinkled on top.
