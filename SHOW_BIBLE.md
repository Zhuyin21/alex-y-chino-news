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

## Transitions + music
Rotate through transitions so the show flows. Never use the same one twice in an episode.
- Serious: "En otras noticias…" (Chino, right after the music sting), "In other news, and this one's serious…", "Ahora sí, hablando en serio…"
- Neutral: "Switching gears…", "Y cambiando de tema…", "Meanwhile, over in DC…", "Closer to home…"
- To the world section: "Vámonos pal' otro lado del charco…", "Now, around the world…"
- Before a story about a tragedy or violence, **always** use a serious transition.

**Weekly theme music:** the intro, stings and outro rotate genres every Sunday (norteño, corrido tumbado, mariachi, cumbia, cumbia rebajada, salsa, bachata, merengue). This week's genre is in `assets/music/current.json` → `assets/music/library/<pack>/pack.json`. In the first episode of a new pack, the cold open can nod to it in one natural line (e.g., Chino: "¡Y esta semana entramos con salsa, Doc!"). Don't mention it every day. `[MUSIC: sting-serious]` is a softer, quieter cut of the same weekly theme (no separate sad music).

**Music cues:** put a cue on its own line, e.g. `[MUSIC: sting]` or `[MUSIC: sting-serious]`, right before a section or a tone change. The next line is usually Chino's transition ("En otras noticias…"). Cue types: `intro`, `sting`, `sting-serious`, `outro`. *(The pipeline will start using the cues once the music is chosen.)*

## Format (10–15 min, ~1,500–2,200 words; hard max 2,300)
Length flexes with the news. On a slow day, aim for about 10 minutes. On a big day (elections, a major local story), go up to 15. Never pad.

Each section still covers **5 stories**: **2 main stories** (the facts, then a quick back-and-forth) and **3 rapid-fire headlines** (one or two lines each, with an occasional one-liner joke).
1. Cold open + weather (~30–45 sec)
2. **Local**, Albuquerque + Bernalillo County (plus statewide when it matters) (~3–5 min)
3. **United States** (~3–4 min)
4. **World** (~3–4 min)
5. **One Good Thing** closer (~30 sec)

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
