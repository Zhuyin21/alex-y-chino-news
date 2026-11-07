# Instructions for Claude

This repo produces a daily news podcast. Before writing or editing any episode, read `SHOW_BIBLE.md` and follow it exactly.
**On Saturdays** the show is the special **Sábado de Tech con Alex y Chino**: also read `SABADO_TECH.md`, which overrides the bible's format, sourcing and AI-labeling rules for that episode.

- New episodes go to `episodes/YYYY-MM-DD_episode-NNN.md`, numbered one higher than the latest episode.
- Use the front matter and line format from the previous episode (`SPEAKER [style]: text`). The TTS pipeline parses this format.
- Check yesterday's episode so you don't repeat stories without a real update.
- Verify every fact against sources you fetched in this session. Don't fill gaps from memory.
- **Before committing an episode, self-check the voice against SHOW_BIBLE.md "How they talk":**
  - Chino is about 70% Spanish / 30% English overall (real Juárez Spanish, whole sentences, not sprinkled words), and laughs on a good number of his lighter lines (style tags).
  - Doc is about 60% English / 40% Spanish, with New Mexican touches and 2–3 natural dry jokes per episode (none in serious segments).
  - The respect rule holds: never "no mames" or "wey" aimed at Doc.
  - No transition is repeated, and the serious segments have no jokes.
  - Rewrite any line that reads like an English news script with Spanish sprinkled on top.
