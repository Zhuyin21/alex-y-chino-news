# Alex y Chino: Show Bible

## Hosts
- **Dr. Alex** (also "Alex," "Doc"): grew up in Burque, PhD in **mechanical engineering**. Professional, calm and clear: he explains how things work and what the numbers mean. Relaxed, not stiff. Nuevomexicano de raíz: grew up with green chile and Northern New Mexico family traditions, a mix of Mexico and New Mexico. New Mexican expressions, varied: *eee, ay ay, uy, suave, ahí te watcho, órale, brother, carnal, ese*, "red or green?", "Christmas style," an occasional *¡hijo!*. "Compa" only now and then, and **never "bro"** (he's about 40). **Not always serious:** he laughs easily at Chino and at himself. **Rarely** (about once every two weeks, never in serious segments) he trips on a hard Spanish word, Chino helps him out, Doc says it in English, and they move on ("Ah, eso. Gracias, Chino"). **Language mix: about 60% English, 40% Spanish.** He drops a **dry joke or a nerdy dad joke every now and then** (roughly 2–3 per episode, never forced, never in serious segments) and laughs at Chino's jokes. **Mid-forties** (his life off the air is in PERSONAJES.md). His engineering shows in **how** he explains (mechanisms, numbers, "how would you test that?"), **not in announcing it**: "como ingeniero…" / "as an engineer…" at most once an episode, and only when it really adds something. Family life (his daughter Julie) is in PROGRAMACION.md.
- **Chino**: Mexican, from Juárez, Chihuahua, now living in the South Valley, **25–27 years old**. His family and life off the air are in PERSONAJES.md. Warm, energetic, funny. **Language mix: about 70% Spanish, 30% English.** Real Juárez/Chihuahua border Spanish, with whole sentences, reactions and many facts said in Spanish. **He laughs easily**: mark it with style tags like `[laughing]`, `[chuckling]` or `[cracking up]` on a good number of his lighter lines, plus the occasional short "¡Ja!" (never "jajaja" spelled out). Connects stories to everyday life on both sides of the border. His humor comes from his personality, never from stereotypes.
- **Their dynamic:** Chino **respects Doc as his mentor.** He teases him, but warmly. They're compas, and it should sound like two friends in a car, not anchors reading a teleprompter.

## How they talk
- **Respect rule:** when Chino speaks *to* Doc, he says "¡No manches, Doc!", never "no mames," and he doesn't call Doc "wey." "¡No mames, qué feo!" is only for reacting to a story or situation, never aimed at Doc.
- **Names:** Chino switches between "Doc," "Alex" and "Dr. Alex." "*Dr.* Alex" is for when he's teasing. Chino's own slang is younger: **"amigo," "compita," "bro"** for the raza listening, Ashley or friends, but **never "bro" to Doc** (respect rule). Doc calls Chino "Chino," "carnal," "brother" or, now and then, "compa."
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

**Theme music changes every day:** the build picks the intro/stings/outro pack at random from the library (`assets/music/library/`, about 30 genres from Mexico, Latin America, the Caribbean, Brazil, Africa and Cape Verde, plus December family-party packs), without repeating a genre within 4 episodes or a pack within 30 days; the pick is recorded in `docs/episodes.json`. The script doesn't choose it and the hosts don't need to mention it (now and then, in one natural line, is fine if the dry run shows a fun genre: `Music pack: …`). `[MUSIC: sting-serious]` is a softer, quieter cut of the same weekly theme (no separate sad music).

**Music cues:** put a cue on its own line, e.g. `[MUSIC: sting]` or `[MUSIC: sting-serious]`, right before a section or a tone change. The next line is usually Chino's transition ("En otras noticias…"). Cue types: `intro`, `sting`, `sting-serious`, `outro`.

**Sound effects:** `[SFX: name]` on its own line plays a short clip (1–5 s) from `assets/sfx/` (built by `pipeline/sfx_mix.py` from Pixabay sounds; when a sound has variants, `name-2`, `name-3`…, the build rotates them every week). Use them **only where PROGRAMACION.md says**, right before the line that opens that part ("¡Arrancamos con el fútbol!"). Never two in a row, never in serious segments or before hard news, and only names that exist in `assets/sfx/` (an unknown name stops the build).
**Keep them natural, not a sound circus** (Chuy, Nov 18):
- **The dialogue never sets up a sound.** No line written to cue it ("¿nadie? ¿nada?" before crickets), no pause waiting for it. Take the sound out and the conversation must still work.
- **Not every joke gets a sound.** A comedy sound only lands on a moment that's already funny on its own, as a surprise. Most jokes get none.
- **Monday to Thursday and Saturday:** at most **1** comedy sound per episode (`rimshot`, `grillos`, `scratch`, `aplausos`, `aplausos-chico`, `caida-papel`, `caida-micro`), and most episodes have none. Transition sounds (weather, `bueno`, the sports and tech section sounds, the Saturday and Tuesday ones) work like music between parts and don't count.
- **Friday (Viernes de Variedad) gets a bit more:** up to about 3 comedy sounds in the segment, plus scene sounds in a radionovela (doors, phone, thunder…) when the scene needs them. Still never two in a row, and never a sound on every line.

- **Every day:**
  - `bueno`: right before **Lo Bueno del Día**, every day (it's its signature).
  - `noticias` (a short, sober newsroom bumper): **Tuesday to Saturday, right before each news block's spoken transition** ("Vámonos con la noticia local del día", nacional, internacional), so three per episode. When a block opens with a tragedy or violence, use `[MUSIC: sting-serious]` there instead. Monday keeps its music separators.
  - `alerta`: a serious newsroom intro, **only for real breaking news** that's big but not a tragedy (a major vote, ruling or announcement); most days it isn't used. Tragedies and violence get `[MUSIC: sting-serious]`, never this.
  - `rimshot`: right after one of Doc's dad jokes (at most once an episode).
  - `grillos`: when a joke clearly didn't land, and someone notices it ("…¿nadie? ¿nada?").
  - `scratch`: Chino's "¡No mames…!" + "perdón, raza" moment, between the two lines.
  - `aplausos` / `aplausos-chico`: a real win worth celebrating (Chino's perfect quiniela week, a great explanation from Ashley, a big milestone); big or small to match the moment.
  - `consulta` (an airplane cabin "ding-dong"): right before a **featured question** in any segment: Pregúntale a Doc, a listener's question, the ¿Mito o Ciencia? claim, the question that frames El Tema de la Semana. At most once per segment.
  - `campanilla` (a hotel desk bell): when Chino **locks in a quiniela pick** ("¡pick final!"), or before a **dato curioso**. At most 3 in the quiniela and once elsewhere.
  - `escribiendo` (pen on paper, "anotado"): when Doc **writes down Chino's quiniela**.
  - `llamada` (ringback tones): a **call into the studio**, only from the cast: Ashley calling from outside the studio, or Sophie on another day with a chisme too big to wait (about once a month). At most once a week. Never a "listener" call: listeners only appear with a real message and their permission.
  - Little accidents (count as comedy sounds): `caida-papel` (someone's papers slip off the desk; they laugh it off), `caida-micro` (a mic hits the floor, or a real "mic drop" after winning an argument). Rare: about once every week or two between the two.
  - Cars: `carro-arranca`, `carro-acelera`, `carro-freno`, `carro-claxon`, `carro-puerta` for radionovela scenes or a quick commute joke in the cold open; `chino-llega-tarde` only for the surprise bit in PROGRAMACION.md.
  - Overall, keep it to a handful of sound effects per episode: they're seasoning, like the rivalries.
- **Miércoles en La Cancha:** `futbol`, `nfl`, `nba`, `box` (boxing and UFC), `lobos`.
- **Weather:** `clima`, `clima-lluvia`, `clima-tormenta`, `clima-truenos` (see "Weather").
- **Monday:** `lunes-reloj`, `lunes-papeles`, `lunes-mazo` (4 takes that rotate weekly; where they go: PROGRAMACION.md).
- **Agenda Cultural (Tuesday):** `martes-diva`, `martes-cine`, `martes-vinil`, `martes-chisme`, `martes-evento` (where each goes: PROGRAMACION.md).
- **Viernes de Variedad:** `viernes-telenovela`, `viernes-sospecha`, `viernes-suspenso`, `viernes-trueno`, `viernes-fin`, `viernes-risas`, `viernes-maquina`, `viernes-pagina`, `viernes-puerta-abrir`, `viernes-puerta-cerrar`, `viernes-puerta-rechinido`, `viernes-puerta-tocar`, `viernes-telefono`, `viernes-aullido`, `viernes-caballo` (where each goes: PROGRAMACION.md). Fiction formats are radio theater: scene sounds go where the story needs them (a door, a phone, thunder), and every one has to land on a real story beat.
- **Sábados Científicos:** `sabado-burbujas`, `sabado-espacio`, `sabado-eureka`, `sabado-mito`, `sabado-ciencia`, `sabado-nm` (where each goes: SABADO_TECH.md).
- **Tech Thursday:** `tech-noticias`, `tech-ia`, `tech-vale`, `tech-si-vale`, `tech-esperate`, `tech-ni-lo-pienses`, `tech-avance`, `tech-realidad`, `tech-hype`, `tech-nm`.

## Format, Monday to Saturday (~30 min, ~4,400–4,900 words; hard max 5,200)
Every day has the same shape: **~7 minutes of news, ~18 minutes of the segment of the day, and a short close** (Monday keeps its longer news). The segments and the cast are in `PROGRAMACION.md`; read it every day. The weekday news blocks follow this file; Saturday's science segment also follows `SABADO_TECH.md`.

**News is New Mexico first, not only Burque.** "Local" means the whole state when that's where the story is (Santa Fe, Las Cruces, Farmington, the pueblos and tribal nations, the legislature…).

**Don't repeat news (every day, Monday included).** The `episodes/` folder is the record: before picking stories, read the show notes of the **episodes from the last 7 days**.
- A story that aired **yesterday is not covered today**, not even from a new angle.
- It can come back as a **seguimiento** from **two days later** (e.g., Monday → Wednesday), and only with a **real new development**: new facts, a vote, a ruling, new numbers. Say it's an update ("Seguimiento: …") and keep it to a rapid-fire item or 1–2 lines, unless the development is itself the biggest news of the day.
- The same story told from another angle, with nothing new, counts as a repeat. Use the slot for a story we haven't covered.

**Explain the references.** When a US custom or holiday, or something very Burque, comes up (Friday the 13th, Thanksgiving traditions, "red or green?"), explain it in one line so a listener who grew up in Latin America gets it, and do the same the other way around (martes 13, el Día de la Candelaria…).

### Tuesday to Saturday (~30 min)
1. **Cold open + weather** (~1.5 min): `[MUSIC: intro]`, hellos and the ABQ weather (see "Weather" below).
2. **The news, ~7 min, with spoken transitions** so the three blocks never blur together. Use these (light wording variations are fine, the shape isn't):
   - "**Vámonos con la noticia local del día**" → **1 main** New Mexico story (facts, then a quick back-and-forth) → "**Seguimos con el rapid fire de noticias locales**" → **2 rapid-fire** headlines.
   - "**Ahora, la noticia nacional del día**" → 1 main US story → "**Y el rapid fire nacional**" → 2 rapid-fire.
   - "**Vámonos con la noticia internacional del día**" → 1 main world story → "**Y el rapid fire internacional**" → 2 rapid-fire.
   - Before a story about a tragedy or violence, put `[MUSIC: sting-serious]` and a serious line ("En otras noticias, y esta es seria…") ahead of it, inside the block.
3. `[MUSIC: sting]` → **Segment of the day** (~18 min): Tue **Agenda Cultural** · Wed **Miércoles en La Cancha** · Thu **Tech Thursday** · Fri **Viernes de Variedad** · Sat **Sábados Científicos**. **Every segment ends with something local.**
4. **Lo Bueno del Día** (~1.5 min) + goodbye, `[MUSIC: outro]`. The good news **fits the day's theme** (a sports story on Wednesday, tech on Thursday, a science win on Saturday; a fun Burque story on Monday or Friday).
5. **Doc's AI reminder** (~10 s), then the goodbye and `[MUSIC: outro]`. See "AI disclosure" below.

### Monday (~30 min): the news that starts the week
1. Cold open + weather (~1.5 min).
2. **Noticias Locales** (~6 min): 2 main + 3 rapid-fire. `[MUSIC: sting]`
3. **Nacional** (~3 min): 1 main + 3 rapid-fire. `[MUSIC: sting]`
4. **Internacional** (~3 min): 1 main + 3 rapid-fire. `[MUSIC: sting]`
5. **El Tema de la Semana** (~12 min): the week's biggest New Mexico issue in depth, plus UNM news. The news blocks cover *other* stories.
6. **Lo que viene esta semana** (~2.5 min): council and legislature meetings, key dates, big events (local to end).
7. Lo Bueno del Día, **Doc's AI reminder**, then the goodbye.

### AI disclosure (every day, right before the goodbye)
The show is made with AI (scripts and voices), and Apple Podcasts requires shows with synthetic voices or AI hosts to say so prominently in each episode. So **every episode ends with Doc's AI reminder**: after Lo Bueno del Día, Doc says one short line (~10 seconds, under ~30 words), and then Chino (or whoever closes that day) says the goodbye.
- It always says three things: **the show is made with AI** (the scripts and the voices), **the news is real**, and **the sources are in the show notes**.
- Vary the wording every day, in Doc's usual Spanglish. Calm and sincere, never a joke and never a punchline. Examples (don't copy them word for word):
  - DOC: "Antes de irnos, el recordatorio de siempre: this show is made with AI, los guiones y las voces. Las noticias son reales, y las fuentes están en las notas."
  - DOC: "Y como cada día: somos un show hecho con inteligencia artificial, pero todo lo que les contamos tiene fuente. Check the show notes."
- **Tuesday:** Doc comes back for this one line, then Chino and Sophie say goodbye. **Saturday:** Doc says it before he and Ashley close.
- The feed adds the same notice as the first line of every episode's notes (`pipeline/build_feed.py`), so the script doesn't need to repeat it in the show notes.

### Weather (every day, in the cold open)
- Today's **high and low in °F and °C** ("sesenta y ocho grados, unos veinte centígrados"), **humidity**, and **chance of rain or snow**.
- **Air quality and pollen when they matter:** say it when the AQI is moderate or worse (smoke, dust, ozone) or pollen is high, with a quick tip for people with asthma or allergies. Skip it on clean days.
- **Sound:** right before the weather, one `[SFX]` that matches the forecast: `clima` (wind chimes) on a normal day, `clima-lluvia` when there's a real chance of rain or snow (about 30% or more), `clima-tormenta` for heavy rain, `clima-truenos` when thunderstorms are forecast.
- Sources: the National Weather Service Albuquerque forecast; AirNow or the City of Albuquerque Air Quality Program for AQI; a reputable pollen forecast. Cite them in the show notes under the cold open.

### Day notes
- **Tuesday:** Doc does the news, then hands the segment to Chino and Sophie ("Los dejo con Chino y Sophie"); Doc returns only for the AI reminder, and Chino and Sophie say the goodbye.
- **Saturday:** Doc and Chino do the news; then **Chino hands the mic to Ashley** with a real transition ("¡Ashley, te toca! Hoy es Sábados Científicos…"), and Doc and Ashley do the science segment and close.
- **Friday:** Viernes de Variedad rotates formats (PROGRAMACION.md). Anything fictional (a radionovela, a sketch) is clearly fiction and comedy. Picardía and the odd albur are fine (Doc shuts it down: "this is a family show"); no strong swearing, no jokes at the expense of real people or groups. Don't overload it with Burque references; the local part is the weekend plan at the end.
- **Wednesday and Thursday bring the hype:** open the segment hot, with Chino genuinely excited, shorter lines, a faster back-and-forth and less newscast tone. Hype is energy, never exaggerated facts.
- Length flexes a little with the news, but the segment always gets its ~18 minutes. Never pad: a tight news block is better than filler.

Keep banter tight: one good joke per story beats three okay ones. Cut background the listener doesn't need while driving.

## Editorial rules
- **Facts first.** Every fact needs at least 2 independent sources. If only one source has it, attribute it on air ("per the Journal…").
- **Hosts can joke, react and comment, but they never dispute the facts.** Their commentary follows the evidence. Where there's scientific consensus, they say so plainly.
- **Values debates:** when a debate is about values rather than evidence, briefly give the strongest case for the other side instead of dunking on it.
- **No jokes about victims, deaths, tragedies or violence.**
- **Allegations stay "alleged"** until there's a conviction.
- **Election results:** say who called the race. Uncalled races are "still being counted," never "won."
- **Conflicts of interest:** the show is produced with Claude (scripts) and Google Gemini (voices), so skip or disclose any Anthropic stories, and disclose the show's use of their tools when a story involves Anthropic, Claude, Google or Gemini.
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
