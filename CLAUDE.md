# Instructions for Claude

This repo produces a daily news podcast. Before writing or editing any episode, read `SHOW_BIBLE.md` and follow it exactly.

- New episodes go to `episodes/YYYY-MM-DD_episode-NNN.md`, numbered one higher than the latest episode.
- Use the front matter and line format from the previous episode (`SPEAKER [style]: text`). The TTS pipeline parses this format.
- Check yesterday's episode so you don't repeat stories without a real update.
- Verify every fact against sources you fetched in this session. Don't fill gaps from memory.
- **Before committing an episode, self-check the voice against SHOW_BIBLE.md "How they talk":**
  - Most of Chino's lines include real Juárez Spanish, with whole reactions and asides in Spanish (not just a one-word opener).
  - About a quarter or more of Doc's lines have Spanish or New Mexican touches.
  - The respect rule holds: never "no mames" or "wey" aimed at Doc.
  - No transition is repeated, and the serious segments have no jokes.
  - Rewrite any line that reads like an English news script with Spanish sprinkled on top.
