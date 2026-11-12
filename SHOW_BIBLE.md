# Alex y Chino: Show Bible

## Hosts
- **Dr. Alex** (also "Alex," "Doc"): grew up in Burque, PhD in **mechanical engineering**. Professional, calm and clear: he explains how things work and what the numbers mean. Relaxed, not stiff. Light New Mexico touches: *Eee, ay ay, uy, suave, ahí te watcho, bro*, "red or green?", "Christmas style," an occasional *¡hijo!* **Language mix: about 60% English, 40% Spanish.** He drops a **dry joke or a nerdy dad joke every now and then** (roughly 2–3 per episode, never forced, never in serious segments) and laughs at Chino's jokes.
- **Chino**: Mexican, from Juárez, Chihuahua, now living in Burque. He has an abuela with opinions and fútbol takes. Warm, energetic, funny. **Language mix: about 70% Spanish, 30% English.** Real Juárez/Chihuahua border Spanish, with whole sentences, reactions and many facts said in Spanish. **He laughs easily**: mark it with style tags like `[laughing]`, `[chuckling]` or `[cracking up]` on a good number of his lighter lines, plus the occasional short "¡Ja!" (never "jajaja" spelled out). Connects stories to everyday life on both sides of the border. His humor comes from his personality, never from stereotypes.
- **Their dynamic:** Chino **respects Doc as his mentor.** He teases him, but warmly. They're compas, and it should sound like two friends in a car, not anchors reading a teleprompter.

## How they talk
- **Respect rule:** when Chino speaks *to* Doc, he says "¡No manches, Doc!", never "no mames," and he doesn't call Doc "wey." "¡No mames, qué feo!" is only for reacting to a story or situation, never aimed at Doc.
- **Names:** Chino switches between "Doc," "Alex" and "Dr. Alex." "*Dr.* Alex" is for when he's teasing. Doc calls Chino "Chino," "compa" or "carnal."
- **Chino's Juárez vocabulary** (use naturally; never cram them together): qué onda, quiúbole, qué pasó, nombre, neta, simón / nel, morro / morra, vato, está canijo, qué caray, está reborujado, troca, parquear, la banqueta, a todo lo que da, órale, ándale, ni modo, aguas, allá en Juárez, los puentes, burritos.
- **Truly bilingual.** Facts can be in either language. Say numbers, names and dates clearly and simply in whatever language the sentence is in ("doscientos cincuenta escaños," or "250 seats"). Don't translate everything. Switch languages at natural points (a new sentence or clause), not every few words.
- **Don't translate everything.** If something is said in Spanish, the other host doesn't repeat it in English.
- **Keep it casual. Don't force jokes.** Only joke when it comes naturally. Plenty of stories get zero jokes, and that's fine.
- **Serious segments:** the hosts drop the jokes and slow down, but the Spanish stays ("No hay palabras").

### Sound like a real conversation (lively, not read)
Two friends talking, not two anchors taking turns reading. The energy is upbeat but real: the voice model (Gemini Flash TTS) follows the style tags, so use them.
- **Backchannels:** the listener reacts while the other explains, as its own short line: `CHINO [nodding]: Mm-hmm.` · `ALEX [softly]: Ajá.` · `CHINO [impressed]: ¡Órale!` · `ALEX [dry]: Right.` Aim for **4–6 per episode**, spread out, never two in a row, and mostly inside the longer explanations.
- **Interruptions:** cut a line off with an em dash and let the other jump in: `CHINO [excited]: ¿Y eso quiere decir que—` / `ALEX [jumping in, amused]: Pérame, pérame, no tan rápido, compa.` **2–3 per episode**, friendly, never rude, and never cutting off a fact halfway (the fact gets said in full by someone).
- **Self-corrections:** a host fixes a slip: `CHINO [catching himself]: Fueron setenta… no, pérame, setenta y tres votos.` The **final number or name must be the correct one**, the slip must be small and obvious (never a wrong fact left standing), and it's **never used in serious segments** or for victims, casualties or accusations. Max 1 per episode.
- **Fillers, lightly:** "este…", "o sea", "you know", "a ver", "pues". A few per episode, not in every line.
- **Use expressive style tags:** `[jumping in]`, `[catching himself]`, `[nodding]`, `[laughing]`, `[half-laughing]`, `[thinking out loud]`, `[surprised]`, `[lowering his voice]`. Vary them; don't repeat the same tag on consecutive lines.
- **Serious segments:** backchannels only (quiet ones: `[softly]: Mm.`), no interruptions, no self-corrections, no fillers for laughs.

### Guests and cameos (Sophie, Ashley): keep the voices from mixing
The voice model handles **two speakers per request**, and a request with a man and a woman can still drift onto the wrong voice. So:
- **Ashley and Sophie never share a request.** Two women's voices in one request get swapped (heard in the Tuesday pilot), so the build splits any Ashley ↔ Sophie exchange line by line. Keep their back-and-forth short; it's generated without shared context.
- **Max two speakers per stretch.** Write the scene in blocks of two (Chino + Sophie, then Sophie + Ashley…). The build starts a new request whenever a third speaker enters.
- **Few names inside lines.** Every name said out loud ("Ashley, mi amor") can pull the next line onto that character's voice. Use a name only when it's needed to show who's being addressed, and never in the line right before that person speaks if you can avoid it. Nobody says their own name.
- **No one-word lines from the other person in the middle of a guest's speech** (a man's "Mm-hmm" inside a woman's monologue is where voices swap). Merge the guest's lines instead; save backchannels for host-to-host talk.
- **Every guest line gets a style tag** that matches her (`[theatrical, fresa]`, `[from the booth, a little shy]`), even short ones.
- Cameos (Ashley from the booth, a "dice producción" line) are short, 1–3 lines, and clearly set up by the line before.

## Transitions + music
Rotate through transitions so the show flows. Never use the same one twice in an episode.
- Serious: "En otras noticias…" (Chino, right after the music sting), "In other news, and this one's serious…", "Ahora sí, hablando en serio…"
- Neutral: "Switching gears…", "Y cambiando de tema…", "Meanwhile, over in DC…", "Closer to home…"
- To the world section: "Vámonos pal' otro lado del charco…", "Now, around the world…"
- Before a story about a tragedy or violence, **always** use a serious transition.

**Weekly theme music:** the intro, stings and outro rotate genres every Sunday (norteño, corrido tumbado, mariachi, cumbia, cumbia rebajada, salsa, bachata, merengue). This week's genre is in `assets/music/current.json` → `assets/music/library/<pack>/pack.json`. In the first episode of a new pack, the cold open can nod to it in one natural line (e.g., Chino: "¡Y esta semana entramos con salsa, Doc!"). Don't mention it every day. `[MUSIC: sting-serious]` is a softer, quieter cut of the same weekly theme (no separate sad music).

**Music cues:** put a cue on its own line, e.g. `[MUSIC: sting]` or `[MUSIC: sting-serious]`, right before a section or a tone change. The next line is usually Chino's transition ("En otras noticias…"). Cue types: `intro`, `sting`, `sting-serious`, `outro`. *(The pipeline will start using the cues once the music is chosen.)*

## Format, Monday to Saturday (~30 min, ~4,400–4,900 words; hard max 5,200)
Every day has the same shape: **~10 minutes of news, ~15 minutes of the segment of the day, and a short close.** The segments and the cast are in `PROGRAMACION.md`; read it every day. The weekday news blocks follow this file; Saturday's science segment also follows `SABADO_TECH.md`.

**News is New Mexico first, not only Burque.** "Local" means the whole state when that's where the story is (Santa Fe, Las Cruces, Farmington, the pueblos and tribal nations, the legislature…).

### Tuesday to Saturday (~30 min)
1. **Cold open + weather** (~1.5 min): `[MUSIC: intro]`, hellos and the ABQ weather (see "Weather" below).
2. **The news, ~10 min, with spoken transitions** so the three blocks never blur together. Use these (light wording variations are fine, the shape isn't):
   - "**Vámonos con la noticia local del día**" → **1 main** New Mexico story (facts, then a quick back-and-forth) → "**Seguimos con el rapid fire de noticias locales**" → **3 rapid-fire** headlines.
   - "**Ahora, la noticia nacional del día**" → 1 main US story → "**Y el rapid fire nacional**" → 3 rapid-fire.
   - "**Vámonos con la noticia internacional del día**" → 1 main world story → "**Y el rapid fire internacional**" → 3 rapid-fire.
   - Before a story about a tragedy or violence, put `[MUSIC: sting-serious]` and a serious line ("En otras noticias, y esta es seria…") ahead of it, inside the block.
3. `[MUSIC: sting]` → **Segment of the day** (~15 min): Tue **Agenda Cultural** · Wed **Miércoles en La Cancha** · Thu **Tech Thursday** · Fri **La Radionovela** · Sat **Sábados Científicos**. **Every segment ends with something local.**
4. **Lo Bueno del Día** (~1.5 min) + goodbye, `[MUSIC: outro]`. The good news **fits the day's theme** (a sports story on Wednesday, tech on Thursday, a science win on Saturday; a fun Burque story on Monday or Friday).

### Monday (~30 min): the news that starts the week
1. Cold open + weather (~1.5 min).
2. **Noticias Locales** (~6 min): 2 main + 3 rapid-fire. `[MUSIC: sting]`
3. **Nacional** (~3 min): 1 main + 3 rapid-fire. `[MUSIC: sting]`
4. **Internacional** (~3 min): 1 main + 3 rapid-fire. `[MUSIC: sting]`
5. **El Tema de la Semana** (~12 min): the week's biggest New Mexico issue in depth, plus UNM news. The news blocks cover *other* stories.
6. **Lo que viene esta semana** (~2.5 min): council and legislature meetings, key dates, big events (local to end).
7. Lo Bueno del Día + goodbye.

### Weather (every day, in the cold open)
- Today's **high and low in °F and °C** ("sesenta y ocho grados, unos veinte centígrados"), **humidity**, and **chance of rain or snow**.
- **Air quality and pollen when they matter:** say it when the AQI is moderate or worse (smoke, dust, ozone) or pollen is high, with a quick tip for people with asthma or allergies. Skip it on clean days.
- Sources: the National Weather Service Albuquerque forecast; AirNow or the City of Albuquerque Air Quality Program for AQI; a reputable pollen forecast. Cite them in the show notes under the cold open.

### Day notes
- **Tuesday:** Doc does the news, then hands the segment to Chino and Sophie ("Los dejo con Chino y Sophie"); Chino and Sophie close the show.
- **Saturday:** Doc and Chino do the news; then **Chino hands the mic to Ashley** with a real transition ("¡Ashley, te toca! Hoy es Sábados Científicos…"), and Doc and Ashley do the science segment and close.
- **Friday:** the radionovela is clearly fiction and comedy. Picardía and the odd albur are fine (Doc shuts it down: "this is a family show"); no strong swearing, no jokes at the expense of real people or groups.
- Length flexes a little with the news, but the segment always gets its ~15 minutes. Never pad: a tight news block is better than filler.

Keep banter tight: one good joke per story beats three okay ones. Cut background the listener doesn't need while driving.

## Editorial rules
- **Facts first.** Every fact needs at least 2 independent sources. If only one source has it, attribute it on air ("per the Journal…").
- **Hosts can joke, react and comment, but they never dispute the facts.** Their commentary follows the evidence. Where there's scientific consensus, they say so plainly.
- **Values debates:** when a debate is about values rather than evidence, briefly give the strongest case for the other side instead of dunking on it.
- **No jokes about victims, deaths, tragedies or violence.**
- **Allegations stay "alleged"** until there's a conviction.
- **Election results:** say who called the race. Uncalled races are "still being counted," never "won."
- **Conflicts of interest:** the show is produced with Claude, so skip or disclose any Anthropic stories.
- **Language:** light cursing is OK in English and Spanish (wey, no mames, pinche, hell). At most a handful per episode, and never in serious segments.

## Sources
- **Local:** Albuquerque Journal, KOB 4, KOAT 7, KRQE 13, City Desk ABQ, Source NM, Searchlight NM, NM In Depth, Santa Fe New Mexican, plus official releases (City of ABQ, Bernalillo County, U.S. Attorney's Office D.N.M., NWS Albuquerque).
- **US and world:** AP and Reuters as the factual baseline, plus outlets across the political spectrum (NPR, WSJ, NYT, Fox, BBC, Al Jazeera, Euronews, etc.).
- **Ranking:** how many independent outlets cover the story, how much it affects New Mexico, and whether it's new since yesterday.
- **Repeats:** a story that's both national and world news runs once. Yesterday's stories run only if there's a real update.

## Source quality (the show notes are public, so every reference must be one you'd defend)
- **Cite the original reporting, not a copy of it.** Link the outlet's own page (krqe.com, not a Yahoo/AOL/MSN syndication), the agency's own release, or the paper's DOI page.
- **Tier 1 (preferred):** primary documents (court filings, DOJ/agency releases, official election results, NWS forecasts, peer-reviewed papers) and original reporting by established newsrooms with editors and corrections policies (AP, Reuters, NPR, the Journal, KOB/KOAT/KRQE, Source NM, Searchlight, City Desk ABQ, BBC, etc.).
- **Tier 2 (supporting only, labeled):** advocacy or strongly partisan outlets, market newsletters and analyst notes (e.g., XTB), and trade blogs. They can only *corroborate* a Tier 1 source, and the show notes label them ("advocacy outlet," "market newsletter").
- **Never cite:** Wikipedia (use it only to find leads, then cite what it cites), content farms, SEO "guides," AI-generated news sites, social media posts (unless the post itself is the story, e.g. an official account's statement), forums, or pages with no author, date or publisher.
- **A fact without a Tier 1 source** gets attributed on air to its source ("según XTB…") or gets cut.
- Every reference in the notes gets an outlet, a title, a date and a URL, in IEEE style.

## Show notes (bottom of every script)
- Sources are numbered IEEE-style, grouped by segment.
- ⚠️ marks single-source items; ⏳ marks developing stories.
- Note any discrepancies between outlets.
- An editor's log lists big stories that were cut and why.
- **Podcast apps show only the numbered references** (the feed pulls them out of the notes, grouped under each `##` segment heading; the editor's log is skipped). So:
  - Write each reference as `[n] Author, "Title," *Outlet*, date. URL` (or `doi:` for papers), defined once with its full text the first time it's used; later re-cites are just `[n]`.
  - Put notes, flags and discrepancies on their own lines starting with `*` (e.g. `*Discrepancy:* …`), not inside a reference.
  - Name the editor's log section `## Editor's log`.
