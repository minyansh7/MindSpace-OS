# MindSpace OS — Launch Playbook

Single-source distribution reference for the v2 site launch and Mental Health Awareness Month (May 2026).

Live site: [mindspaceos.com](https://mindspaceos.com) (Cloudflace Pages preview at [mindspace-os.pages.dev](https://mindspace-os.pages.dev) until DNS lands).

Author: Minyan Shi · Minyan Labs · Sydney
Repo: [github.com/minyansh7/MindSpace-OS](https://github.com/minyansh7/MindSpace-OS)

---

## Section 1 — The three findings

The whole launch sits on these three lines. They drive the headline, the tweets, the pitches, the press list. Anchor: **n = 2,899** posts and comments from r/meditation, January 2024 – June 2025.

| Panel | Finding | Number |
|---|---|---|
| **01 / Flow** (relational) | Reassurance leads. Soothing Empathy is the dominant reply shape. | **1 in 4** grief replies mirror grief. **Only 7 of 100** anxiety replies mirror anxiety. |
| **02 / Shape** (taxonomic) | Five emotional archetypes split the conversation. Anxious Concern's fear spike vs Soothing Empathy's warmth. | 5 archetypes (Tender Uncertainty, Reflective Caring, Soothing Empathy, Anxious Concern, Melancholic Confusion) × 8 GoEmotions axes |
| **03 / Constant** (curiosity) | Curiosity holds steady across all five archetypes — the through-line. | Curiosity is **#3 of 28** GoEmotions classes by mean intensity. **82%** of all posts and comments carry a clear curiosity signal. **2.15× joy.** Range across 5 archetypes: 57%–68%. |

**Combined headline (also the Modern-3 featured image H1):**

> Five shapes. One Curiosity. Reassurance flows.

**Editor's-eye second opinion (caring leads, not joy):**

The single most counter-narrative finding. **Caring tops all 28 GoEmotions classes** at mean intensity 0.74 vs joy at 0.29. **Caring outranks joy 2.5×.** Sequence of top 4: Caring → Realization → Curiosity → Confusion.

This is the line for general-public framing — pushes back on wellness-app reductionism without being cynical.

---

## Section 2 — Featured-image inventory

Files at `assets/featured-images/dvs-2026-04-27/`. All Modern-3 (Information+ aesthetic, Inter Tight + Inter + DM Mono).

| File | Dimensions | Use |
|---|---|---|
| `featured-image-3x-square.png` | 3600×3600 | DVS / Nightingale / archival print (12" @ 300 DPI) |
| `featured-image-3x-landscape.png` | 4368×2448 | Print landscape (14.6×8.16" @ 300 DPI) |
| `featured-image-2x.png` | 2400×2400 | High-res digital square |
| `featured-image-landscape-2x.png` | 2912×1632 | High-res Substack hero |
| `featured-image-landscape.png` | 1456×816 | Substack hero default |
| `featured-image-square.png` | 1200×1200 | Web square base |
| `featured-image-ig.png` | 1080×1080 | Instagram square |

**Source HTML** (committed for reproducibility):
- `source-square.html` / `source-square-hq.html` (`html { zoom: 3 }` retina version)
- `source-landscape.html` / `source-landscape-hq.html`
- `source-dynamics.png` (Sankey screenshot, POST/REPLY headers)
- `source-radar-v2.png` (radar — portrait composition for square layouts)
- `source-radar-landscape.png` (radar — horizontal composition for landscape layouts)

**Direct upload URLs** (raw GitHub):
- https://github.com/minyansh7/MindSpace-OS/raw/main/assets/featured-images/dvs-2026-04-27/featured-image-3x-square.png
- https://github.com/minyansh7/MindSpace-OS/raw/main/assets/featured-images/dvs-2026-04-27/featured-image-3x-landscape.png
- https://github.com/minyansh7/MindSpace-OS/raw/main/assets/featured-images/dvs-2026-04-27/featured-image-landscape.png
- https://github.com/minyansh7/MindSpace-OS/raw/main/assets/featured-images/dvs-2026-04-27/featured-image-square.png
- https://github.com/minyansh7/MindSpace-OS/raw/main/assets/featured-images/dvs-2026-04-27/featured-image-ig.png

**Re-rendering:** open the `*-hq.html` source at the matching viewport (3600×3600 for square / 4368×2448 for landscape), screenshot, downsample with PIL LANCZOS for smaller targets. Self-contained — only external dep is Google Fonts CDN.

---

## Section 3 — Twitter / X tweets

Three standalone tweets — different ROI profiles. Don't post all at once; sequence over a launch week (see Section 7 for Beijing-time schedule).

### Tweet 1 — LAUNCH (pin this)

**Image attached:** `featured-image-square.png` (Caring leads / Joy ranks 24th — bar chart visible)

**227 / 280 chars:**

```
On r/meditation, joy ranks 24th of 28 emotions.

Caring is #1. Curiosity is #3. Confusion is #4.

What people carry into meditation isn't bliss. It's the steady act of trying to figure something out.

n=2,899 posts. mindspaceos.com
```

**Why this travels:** counter-narrative + concrete number (Joy 24th) is the rare hook that's both surprising AND unverifiable-in-your-head. Either RT to fact-check or quote-tweet to argue. The chart in the image carries the receipts so it doesn't read as clickbait.

**Pin command:** after posting, hover the tweet → ⋯ menu → "Pin to your profile."

---

### Tweet 2 — Method (Day +4)

**Image attached:** `featured-image-landscape.png` (Modern-3 combined — Sankey + radar + curiosity scoreboard)

**245 / 280 chars:**

```
What does an emotional vocabulary look like? I clustered 2,899 r/meditation posts via GoEmotions + UMAP + GMM into 5 archetypes.

Curiosity runs through all 5 (57–68% intensity).
Fear spikes one. Warmth defines another.

mindspaceos.com
```

**Why this travels in the niche:** legitimizes the dataset with @flowingdata / @ThePudding / @observablehq / DVS Nightingale audience. A reply from one researcher you respect is worth 100 likes from random feed.

---

### Tweet 3 — Relational (Day +2)

**Image attached:** Sankey hero (or `featured-image-3x-square.png` for the combined Modern-3)

**257 / 280 chars:**

```
If you post about grief on r/meditation, 1 in 4 replies will mirror it back.

If you post about anxiety, only 7 of 100 will. The rest reach for reassurance.

The community has unwritten response rules. I mapped them.

n=2,899 posts. mindspaceos.com
```

**Why this travels:** dual-audience. Reads emotionally in a feed but scientifically in a paper review. "Unwritten response rules" invites quote-tweets.

---

## Section 4 — Bluesky variants (300-char limit + better engagement for research content)

**Tag in replies, not in main post** (Bluesky etiquette): `@nightingale.bsky.social`, `@flowingdata.bsky.social`, `@thepudding.bsky.social`, `@observablehq.bsky.social`.

### Bluesky 1 — Counter-narrative (294 chars)

```
On r/meditation, joy ranks 24th of 28 emotions.

Caring is #1. Curiosity is #3. Confusion is #4.

What people carry into meditation isn't bliss. It's the steady act of trying to figure something out together.

2,899 posts, GoEmotions classification.

🔗 mindspaceos.com
```

### Bluesky 2 — Method (282 chars)

```
Mapped the emotional vocabulary of 2,899 r/meditation posts.

GoEmotions classification → UMAP projection → Gaussian Mixture clustering → 5 archetypes.

One sharp contrast: Anxious Concern's fear spike vs Soothing Empathy's warmth.

The constant beneath all 5: curiosity.

🔗 mindspaceos.com
```

### Bluesky 3 — Relational (296 chars)

```
Six months looking at how strangers answer each other on r/meditation.

Grief gets mirrored: 1 in 4 replies stay grief.
Anxiety doesn't: only 7 of 100 stay anxious. The rest reach for reassurance.

The community has unwritten response rules. I mapped them.

🔗 mindspaceos.com
```

---

## Section 5 — Hacker News post

HN rewards **dry, specific titles** + **first-party submission**. Don't repost from Substack — HN crowd reads original sources.

**Title (80-char limit, optimal 50-70):**

```
Show HN: Joy ranks 24th of 28 emotions on r/meditation
```

(Alternate: `Show HN: An emotional anatomy of 2,899 r/meditation posts`)

**URL:** `https://mindspaceos.com`

**First comment (post immediately after submission — high leverage for context):**

> Author here. The site visualizes 2,899 posts and comments from r/meditation (Jan 2024 – Jun 2025) classified via Google Research's GoEmotions (Demszky et al. 2020), projected via UMAP, clustered into 5 archetypes via GMM.
>
> Three findings worth the click:
>
> 1. The dominant emotional vocabulary isn't peace. Caring is the most common emotion (mean intensity 0.74); joy ranks 24th. Curiosity is #3.
>
> 2. Reply patterns have unwritten rules. 1 in 4 replies to grief posts mirror grief. Only 7 of 100 replies to anxiety posts mirror anxiety — the rest reach for reassurance.
>
> 3. Curiosity is the through-line. It runs at 57–68% intensity across all 5 archetypes — the steadiest emotion in the dataset.
>
> Known limitation: GoEmotions was trained on Reddit comments. Applying it back to Reddit measures meditation-talk relative to Reddit baseline, not absolute emotional content. /about#methodology covers this directly.
>
> Source code, dataset notes, methodology: github.com/minyansh7/MindSpace-OS

**Timing:** Tuesday or Wednesday 8–10am PT (5–7am ET wakes the SF-time HN crowd). In Beijing terms: Tuesday or Wednesday **11pm Beijing**. Avoid Friday afternoon (drops fast).

---

## Section 6 — r/dataisbeautiful post

Reddit format requires `[OC]` tag (original content) + clear methodology line. **Square image works best** — feed thumbnail crops 16:9 tightly.

**Title** (300-char limit, optimal Reddit titles 60-80 chars):

```
[OC] I clustered 2,899 r/meditation posts by emotion. Curiosity runs through all 5 archetypes. (n=2,899)
```

**Top comment** (post immediately after submission — Reddit weights it heavily):

> Methodology + tools:
>
> - **Source**: 2,899 posts and comments from r/meditation, January 2024 – June 2025
> - **Emotion classifier**: Google Research's [GoEmotions](https://arxiv.org/abs/2005.00547) (Demszky et al. 2020) — 27 fine-grained emotion classes
> - **Dimensionality reduction**: UMAP on the GoEmotions embedding
> - **Clustering**: Gaussian Mixture Model → 5 emotional archetypes
> - **Stack**: Python (pandas, plotly, scikit-learn) + Astro static site
>
> Known limitation: GoEmotions was trained on Reddit comments, so applying it back to Reddit measures meditation-talk *relative to Reddit baseline*, not absolute emotional content. The /about page covers this in detail.
>
> Site (open dataset, full charts): mindspaceos.com
> Source: github.com/minyansh7/MindSpace-OS

**Image:** `featured-image-square.png` (Modern-3 combined). Square crops cleanly to Reddit's feed thumbnail.

**Post timing**: Sunday 8–10am ET or Tuesday 9–11am ET. Beijing: **Sunday 9pm** or **Tuesday 9pm**. First-30-min upvote velocity determines whether the algorithm pushes you to the front page.

---

## Section 7 — Launch sequence (Beijing time, UTC+8)

You're on the opposite side of the day from your audience. Every action below happens late evening Beijing because:
- Twitter/Bluesky launch window: 9–11am ET = 9–11pm Beijing
- HN front-page voting starts 8am PT = 11pm Beijing same calendar day
- r/dataisbeautiful upvote peaks Sunday 8–10am ET = Sunday 8–10pm Beijing

| Day | Beijing time | Channel | Action |
|---|---|---|---|
| **0** (Tue) | **Wed 10pm** | Twitter | Post Tweet 1, **pin it**, attach `featured-image-square.png` |
| 0 (Tue) | Wed 10:05pm | Bluesky | Post Bluesky 1, attach same image |
| 0 (Tue) | **Tue 11pm** | Hacker News | Submit title → mindspaceos.com, drop first-comment context immediately |
| **+1** (Wed) | Thu 10pm | Twitter | Reply to Tweet 1 with Tweet 3 content (extends thread without losing pin) |
| **+2** (Thu) | Fri 10pm | Twitter | Standalone Tweet 3, attach Sankey image |
| | Fri 10:05pm | Bluesky | Bluesky 3 |
| **+3** (Sun) | Sun 9pm | Reddit | Submit to r/dataisbeautiful with `[OC]` tag + methodology top-comment |
| **+4** (Mon) | Mon 10pm | Twitter | Standalone Tweet 2, attach Modern-3 landscape |
| | Mon 10:05pm | Bluesky | Bluesky 2 |

**Post + 1-hour engagement window, then sleep.** Post at 10pm Beijing, hold the engagement window until 11pm, sleep through US business hours. Reply to overnight engagement next morning. Realistic for one human.

---

## Section 8 — Pre-baked critique replies (copy-paste ready)

Keep these on your phone (Apple Notes / Bear / iCloud Notes synced) so you can reply from bed if needed. Speed of reply matters — first reply within 1hr of a top critic gets the algorithmic boost.

### A — "GoEmotions trained on Reddit, this is circular"

(Most likely from a researcher on Twitter / Bluesky / HN.)

> Yes — that's the methodology's known limitation, covered directly in /about#methodology.
>
> Applying GoEmotions back to Reddit measures r/meditation *relative to a Reddit baseline*, not absolute emotional content. A non-meditation control sub (e.g. r/relationships, r/fitness) is the obvious follow-up — happy to point at the corpus and methodology if anyone wants to run it.

### B — "Sample bias: who posts on Reddit isn't who meditates"

> True. The sample is meditators-who-post-publicly-on-Reddit — about 7 of 10 of whom posted exactly once. It's not a representative sample of meditation practitioners; it's a representative sample of the meditation conversation that happens in public on Reddit. The claim is about the discourse, not the practice.

### C — "Why GoEmotions and not LIWC / VADER / sentence-BERT?"

> GoEmotions gives 27 fine-grained classes vs LIWC's broader categories or VADER's polarity score. For a project specifically about *emotional vocabulary* (not just positive/negative), the higher-resolution taxonomy was load-bearing. Methodology + alternatives discussed at /about#methodology.

### D — "Five archetypes feel like horoscope / personality test bs"

> Fair instinct. They're not personality types — they're emergent clusters from a Gaussian Mixture Model on the GoEmotions embedding, named for what they sound like. Posters drift between them, often within the same post. The radar shows each archetype's emotional fingerprint, not someone's identity.

### E — "What's the y-axis on the curiosity bars? Just '0.68'?"

> Mean GoEmotions intensity score on a 0–1 scale, displayed as percentage for legibility. So 68% = mean intensity of 0.68. Footnote on the figure says "Curiosity Intensity % (scale 0–1) among 5 emotion shapes." Fair to ask — could be clearer.

### F — "Cool but where's the data?"

> Site is the visualization layer; the underlying 2,899-post processed corpus is on the roadmap as a HuggingFace Dataset publication (with DOI). Source code is open at github.com/minyansh7/MindSpace-OS. Reach out (link in /about) if you want early access for research before the formal release.

---

## Section 9 — Mental Health Awareness Month (May) — content angles

May 1 is the start. NAMI runs the official US designation. Greater Good, Mindful, Tricycle, Lion's Roar, Headspace, Calm, NAMI itself, and DVS Nightingale all run special features in May.

### Five angles MindSpace OS can specifically claim

**Angle 1 — "The wellness vocabulary doesn't dominate" (counter-narrative)**
- Lead finding: Joy ranks 24th, Caring is #1, Curiosity is #3
- Audience: general public, wellness-criticism crowd
- Pitch venues: Vox (Sigal Samuel), Anne Helen Petersen, Greater Good
- Why it fits MHAM: pushes back against the "find your zen" reductionism that dominates the month

**Angle 2 — "Caring is #1" (uplifting reframe)**
- Lead finding: Caring leads all 28 GoEmotions classes
- Audience: clinicians, peer support workers, teachers
- Pitch venues: Mindful Magazine, Tricycle, NAMI blog
- Why it fits MHAM: optimistic without being saccharine. People show up to care.

**Angle 3 — "Unwritten response rules" (community + behavior)**
- Lead finding: 1 in 4 grief mirror, 7 of 100 anxiety mirror, Soothing Empathy leads
- Audience: therapists, group facilitators, online community moderators
- Pitch venues: Tara Brach's Substack, Therapy for Black Girls, Greater Good
- Why it fits MHAM: actionable for anyone running peer support spaces

**Angle 4 — "Curiosity holds" (clinical research)**
- Lead finding: 82% of posts carry curiosity ≥ 0.50, runs at 57–68% across all 5 archetypes
- Audience: contemplative science researchers, mindfulness clinicians
- Pitch venues: Mind & Life Institute, Greater Good, Jud Brewer's Substack
- Why it fits MHAM: curiosity is a known protective factor in clinical research; data-supported

**Angle 5 — "The dataset is open" (research community)**
- Lead artifact: dataset + methodology + open source code
- Audience: computational social science, NLP researchers
- Pitch venues: Stevie Chancellor's lab, ICWSM/CSCW community, ArXiv preprint
- Why it fits MHAM: actually useful for the next generation of mental-health-NLP work

### MHAM publication calendar

| Venue | Pitch lead time | Notes |
|---|---|---|
| Greater Good Magazine | ~3 wks | Berkeley quality bar; pitch early April for May |
| Mindful Magazine | ~4–6 wks | Mainstream meditation; pitch even earlier |
| Tricycle | rolling | Buddhist angle helps; methodology angle works too |
| DVS Nightingale | rolling for blog, season for issue | DVS-specific submission doc lives at `docs/dvs-mental-health-month-submission.md` |
| NAMI blog | rolling, May calendar set in March | Lower bar but high relevance |
| Vox Future Perfect | rolling | Sigal Samuel direct pitch |
| Aeon / Psyche | 3-6 mo lead | Long-form essay; would need full essay drafted |

---

## Section 10 — Creator outreach map

Verify handles before pitching — accounts move (especially X → Bluesky migration). Best 8 single accounts for the relational finding (Angle 3) at the end.

### A. Data-viz craft

| Person | Handle | Why fit |
|---|---|---|
| Mona Chalabi | @monachalabi | Data + emotion + mental health constantly |
| Nathan Yau | @flowingdata | Curates "interesting analyses with real data" |
| Federica Fragapane | @fede_fragapane | Narrative-heavy editorial data viz |
| Giorgia Lupi | @giorgialupi | Pentagram partner; *Bruises* (data + illness) |
| Stefanie Posavec | @stefpos | Dear Data co-creator; data art + emotion |
| Nadieh Bremer | @nadiehbremer | Visual Cinnamon; appreciates craft + narrative |
| Shirley Wu | @sxywu | Observable, OpenVis Conf, JS data-viz craft |
| Alberto Cairo | @albertocairo | Functional Art; respects methodology |
| Cole Knaflic | @storywithdata | Storytelling with Data |
| Lisa Charlotte Muth | @lisacmuth | Datawrapper blog |
| John Burn-Murdoch | @jburnmurdoch | FT Visual; methodology defender |
| Jonathan Schwabish | @jschwabish | Urban Institute; "Better Data Visualizations" |
| Hannah Fry | @fryrsquared | BBC math + storytelling |

**The Pudding team:** Matt Daniels (@matthew_daniels), Russell Goldenberg, Will Chase, Michelle McGhee, Caitlyn Ralph

**Publications:** Nightingale Magazine (DVS), Datawrapper Weekly Chart, The Pudding (pitches at thepudding.cool/about), Information is Beautiful Awards (October submission), Observable Notebook newsletter, R Graph Gallery / Yan Holtz

### B. Data storytellers (data + narrative + emotion — bullseye)

| Person | Where | Why fit |
|---|---|---|
| Mona Chalabi | NYT, Guardian | Mental health themes; uses GoEmotions-adjacent data |
| Sigal Samuel | Vox Future Perfect | Philosophy + data; covers meditation/contemplative |
| Kelsey Piper | Vox | Data-driven moral/social narratives |
| Ezra Klein | NYT | Contemplative life + tech + culture |
| Anne Helen Petersen | Culture Study (Substack) | Burnout, wellness culture critique |
| Walter Hickey | Numlock News | Daily data essay |
| Tim Urban | Wait But Why | Long-form essay format |
| Brené Brown | Daring podcast | Emotion researcher, broad reach |
| Caroline Criado Perez | Invisible Women | Data + cultural narrative |
| Asterisk Magazine | asteriskmag.com | Long-form data + research |

### C. Mindfulness teachers / podcasters (Angle 3 audience)

**Highest-fit tier:**

| Person | Handle | Notes |
|---|---|---|
| Tara Brach | @tarabrach | Clinical psych + meditation. RAIN method is *the* response framework — Angle 3 fits her teaching almost exactly. |
| Sharon Salzberg | @sharonsalzberg | Loving-kindness; relational themes are her domain |
| Sam Harris | @samharrisorg | Waking Up app; rationalist audience overlaps with Tweet 2 |
| Dan Harris | @danbharris | Ten Percent Happier; mainstream entry point |
| Sebene Selassie | @sebeneselassie | Body-positive, race + mindfulness; "unwritten rules" lands |
| Oren Jay Sofer | @orenjaysofer | NVC + mindfulness; *Say What You Mean* |
| Light Watkins | @lightwatkins | Broader meditation reach |
| Cory Muscara | @corymuscara | Approachable, narrative voice |
| Susan Piver | @susanpiver | Open Heart Project; data-curious |

**Podcasters:**
- Krista Tippett (@kristatippett) — On Being. Massive lift if it lands; unlikely cold.
- Andrew Huberman (@hubermanlab) — Stanford neuroscience; many meditation episodes
- Lex Fridman (@lexfridman) — long meditation guests
- Hidden Brain (Shankar Vedantam) — would care about community behavior data
- Rich Roll (@richroll) — long-form, mindfulness-adjacent
- Chris Williamson (Modern Wisdom) — has had many meditation guests

### D. Meditation researchers / clinicians

| Person | Affiliation | Why |
|---|---|---|
| Jud Brewer | Brown | Mindfulness + addiction; uses observational data; r/meditation as corpus = exact fit |
| Amishi Jha | UMiami | Attention + mindfulness research |
| Richard Davidson | UW Madison Center for Healthy Minds | Foundational figure |
| Cliff Saron | UC Davis Center for Mind and Brain | Shamatha Project lead |
| Diana Winston | UCLA MARC | Mindful Awareness Research Center |
| Kristin Neff | UT Austin | Self-compassion researcher |
| Christopher Germer | Harvard | Self-compassion clinician |
| Wendy Hasenkamp | Mind & Life Institute | Contemplative science org |
| David DeSteno | Northeastern | Emotion + meditation researcher |
| Ronald Siegel | Harvard | Mindfulness in clinical practice |

**Publications they read:** Mindful Magazine (mindful.org), Tricycle: The Buddhist Review, Lion's Roar, Mind & Life newsletter, Greater Good Magazine (UC Berkeley — Tracy Brower, Jenara Nerenberg), Aeon / Psyche

### E. Therapists & clinical psychologists

| Person | Where | Fit |
|---|---|---|
| Esther Perel | @estherperelofficial | Relational dynamics — "unwritten rules" is her exact language |
| Pauline Boss | Books | Ambiguous loss researcher |
| Diana Fosha | AEDP | Transformational emotional change |
| Carolyn Spring | UK trauma practice | Trauma-informed |
| Janina Fisher | Trauma + parts work | |
| Therapy for Black Girls / Joy Harden Bradford | Podcast | Community-care lens |
| Lori Gottlieb | NYT, *Maybe You Should Talk to Someone* | Therapy + narrative |
| Adam Grant | @adammgrant | Wharton; reposts data work; "most caring response wins" matches Give and Take |
| Brené Brown | Daring podcast | Empathy researcher; foundational |
| Susan David | Author | Emotional agility |

### F. Online community designers & moderators

- CMX Hub / David Spinks — community manager community
- Patrick O'Keefe — Community Signal podcast
- Reddit mod toolkit researchers — Sarah Gilbert, Charlie Kiene
- TWC / Trust & Safety Professional Association
- Reddit's r/depression / r/SuicideWatch mods — exact peer use case
- Substack staff (Notes / Chat) — Hamish McKenzie

### G. Computational social science / NLP researchers

Most likely to cite + replicate the work.

| Person | Affiliation | Why |
|---|---|---|
| **Stevie Chancellor** | UMN | r/depression mod intervention research — *the* peer |
| Munmun De Choudhury | Georgia Tech | Mental health + social media |
| Eric Gilbert | UMich | r/ChangeMyView dynamics |
| Cristian Danescu-Niculescu-Mizil | Cornell | Online conversation analysis |
| Ashton Anderson | Toronto | Communities + behavior |
| Tim Althoff | UW | Counseling chat data |
| Albert-László Barabási | Northeastern | Network dynamics |
| Robb Willer | Stanford | Moral psychology online |
| Michael Bernstein | Stanford HCI | Community design |
| Justine Cassell | CMU | Empathic response in dialogue systems |
| **Diyi Yang** | Stanford NLP | Supportive conversation in online forums — exact fit |
| David Jurgens | UMich | Politeness/support classification |

### H. Peer support practitioners

- Glen Moriarty (founder, 7 Cups)
- Crisis Text Line team — published on response language patterns
- Bob Filbin (former CTL data) — also at Patreon
- NAMI Connection Recovery Support Group trainers
- The Trevor Project crisis counselor trainers
- Wisdo team (peer support app)

### I. Loneliness & social health researchers

- Vivek Murthy (US Surgeon General) — *Together*; declared loneliness epidemic
- Julianne Holt-Lunstad — meta-analyses on loneliness
- Robert Waldinger (Harvard Study of Adult Development) — *The Good Life*
- Marc Schulz — same study, co-author
- Kasley Killam — *The Art and Science of Connection* (2024)
- Robin Dunbar (Oxford) — Dunbar's number, group dynamics

### J. AI-and-empathy researchers (timely + viral)

- Adam Miner (Stanford) — Replika research, AI in mental health
- Tim Althoff (UW), Diyi Yang (Stanford) — listed above
- Anthropic Constitutional AI team — alignment with helpfulness/empathy
- Ethan Mollick (Wharton) — One Useful Thing; AI + behavior
- Inflection / Pi team — empathic AI chat
- Replika team at Luka — would care about training-set patterns

### K. Substack health / mental health writers

- Adam Mastroianni (Experimental History) — psych research + sharp writing
- Scott Alexander (Astral Codex Ten) — psych + statistics
- Sarah Constantin — biomedical research
- The Honest Broker / Ted Gioia — broader cultural lens
- Anne Helen Petersen — wellness criticism (already listed)
- Glennon Doyle — We Can Do Hard Things podcast/writing
- Mari Andrew — illustrated mental health writing

### L. Faith / contemplative-traditions communities

- Richard Rohr — Center for Action and Contemplation
- Brian McLaren — emerging church voices
- Pádraig Ó Tuama — *Poetry Unbound*; held emotion in language
- Krista Tippett (On Being) — major venue
- Cynthia Bourgeault — Centering Prayer

### Best 8 single accounts to pitch with the relational finding

If you only sent one DM each, highest expected-value targets for **Angle 3** (response patterns):

1. **Esther Perel** — "unwritten rules" is her exact language
2. **Stevie Chancellor** — methodology peer; will engage seriously
3. **Diyi Yang** — Stanford NLP supportive-dialogue research; will cite
4. **Vivek Murthy's office** — longshot but symbolic; loneliness epidemic frame
5. **Sebene Selassie** — broader meditation reach + accessibility framing
6. **Adam Grant** — single quote-tweet would cascade
7. **Glen Moriarty (7 Cups)** — operational use case for peer-support training
8. **Tara Brach** — would put it in front of 100k+ podcast listeners

---

## Section 11 — Pitch templates

Three audiences, three voice registers. Tara Brach (clinical-meditation), Therapy for Black Girls (community-care + accessibility), Greater Good (academic/Berkeley).

### Pitch 1 — Tara Brach's Substack / DM

**Subject:** What 2,899 r/meditation posts say about how strangers regulate each other

> Dear Tara,
>
> I've spent the last six months looking at how people answer each other on r/meditation — 2,899 posts and comments from January 2024 to June 2025, classified emotion by emotion using Google Research's GoEmotions model. I built a public site to share what I found at **mindspaceos.com**.
>
> One finding has stayed with me, and I think it would land with your community:
>
> The room has unwritten response rules.
>
> When someone posts about grief, **about 1 in 4 replies mirror grief back.** When someone posts about anxiety, **only 7 of 100 replies stay anxious.** More than half pivot to warm reassurance — what the model classifies as Soothing Empathy. The community never wrote these rules down. They self-organized.
>
> What it looks like in practice: a person spirals in at 2am, asks if it's normal that the breath feels like a brick. The replies don't catch the spiral. They land softer. They say *you're not broken, this is part of it*. The signature emotion in the responses isn't anxiety, isn't even grief — it's caring (which, separately, ranks #1 of 28 emotions across the whole corpus, while joy ranks 24th).
>
> I think your readers — practitioners, teachers, anyone holding a sangha or a recovery group or a Sunday meditation circle — will recognize the pattern. RAIN, after all, is a script for *exactly* the response shape this data shows: pause, name the feeling, soften toward it. Watching strangers do it for each other on a public forum, without a teacher present, without prompting, is its own quiet evidence that the practice generalizes. People show up because they're trying to figure something out together, not because they've already arrived.
>
> Mental Health Awareness Month feels like the right window for this. The dominant May story is wellness apps and "find your zen." This one is messier and more honest: a community of people in mid-struggle, holding each other.
>
> I'd love to share this with your audience however serves you best — happy to:
>
> - Write a guest post for your Substack (~1,200 words, illustrated with the actual charts)
> - Provide source images for you to drop into a post or video of your own
> - Sit for a short conversation on the Tara Brach podcast about the finding and what it suggests about online communities as practice spaces
> - Just send the link and let you do what you want with it
>
> Methodology and limitations are documented openly at /about (GoEmotions trained on Reddit comments — yes, I name the circularity), and the dataset will be open under CC BY 4.0.
>
> Whichever way feels right, I just wanted you to see it.
>
> With care,
> Minyan Shi
> Minyan Labs · Sydney
> mindspaceos.com
> @minyansh

### Pitch 2 — Therapy for Black Girls (Joy Harden Bradford)

Different framing: community-care + accessibility lens. Centers her audience's lived experience around peer support. Less academic, more direct.

**Subject:** Mapping the unwritten rules of how strangers care for each other online

> Dr. Joy,
>
> Your podcast keeps coming back to one question that I think a piece of public-internet data can speak to: who actually shows up when someone asks for help, and what do they say.
>
> I spent six months with 2,899 posts and comments from r/meditation (January 2024 to June 2025), classified by emotional content with Google Research's GoEmotions model. The site is at **mindspaceos.com**.
>
> One finding for your audience specifically:
>
> The strangers most likely to respond with warmth aren't the ones who already feel calm. They're often the ones who've been there.
>
> When someone posts about grief, **about 1 in 4 replies stay grief** — the room moves with the poster. When someone posts about anxiety, **only 7 of 100 replies mirror anxiety** — most of the room reaches toward warmth: gratitude, acknowledgment, "you're not alone." Soothing Empathy is the dominant emotional shape in the replies, not in the posts.
>
> A community of strangers, mostly posting once and leaving, somehow self-organizes a response pattern that looks a lot like what care professionals try to teach: name the feeling, sit with it, don't catch the spiral. They never wrote these rules down. They learned them from each other.
>
> I think this lands for your community and for the therapists you reach because it's quietly hopeful evidence that public-internet spaces can produce real care — when there's enough volume and enough people who recognize the moment.
>
> May feels like the right window. Mental Health Awareness Month is dominated by wellness-app marketing. This one is messier and more honest: people in mid-struggle holding each other.
>
> I'd love to share this with your audience however serves you best:
>
> - A guest post or essay (~1,200 words) on what the data says about peer support online
> - A conversation on the podcast about what it suggests for therapists running peer-process groups
> - Source images you can use in your own writing or videos
> - Or just the link and let you do what you want with it
>
> Methodology and limitations are documented openly at /about — GoEmotions was trained on Reddit comments, so I name the circularity directly.
>
> Whichever way feels right.
>
> With care,
> Minyan Shi
> Minyan Labs · Sydney
> mindspaceos.com
> @minyansh

### Pitch 3 — Greater Good Magazine (UC Berkeley)

Academic register. Lead with the methodology + actionable finding. Berkeley editor cares about quality + applicability.

**Subject:** MHAM pitch — corpus-scale study of response patterns in an online meditation community

> Dear [Editor — Tracy Brower / Jenara Nerenberg / current MHAM editor],
>
> For your Mental Health Awareness Month coverage: I've completed a corpus-scale observational study of response patterns in r/meditation — 2,899 posts and comments from January 2024 through June 2025, classified emotion by emotion using Google Research's GoEmotions taxonomy, projected via UMAP, and clustered via Gaussian Mixture Model into five emotional archetypes. The site visualizing the analysis is at **mindspaceos.com**.
>
> Three findings that I think speak to your readers — both the practitioner-clinician audience and the broader public:
>
> 1. **The dominant emotional vocabulary isn't peace.** Caring is the most common emotion across all 28 GoEmotions classes (mean intensity 0.74); joy ranks 24th of 28. Curiosity is #3. The vocabulary of meditation talk is closer to *"I'm trying again"* than *"I found bliss."* This is a useful counter to the wellness-app reductionism that dominates May coverage.
>
> 2. **Reply patterns have unwritten rules.** Posts about grief draw replies that mirror grief about 1 in 4 times. Posts about anxiety draw replies that mirror anxiety only 7 of 100 times — most of the room reaches toward warm reassurance. The community self-organized a response pattern that resembles trained therapeutic listening.
>
> 3. **Curiosity is the through-line.** It runs at 57–68% intensity across all five archetypes — the steadiest emotion in the corpus. Curiosity is a known protective factor in clinical psychology literature; this provides observational support at corpus scale.
>
> Methodological transparency: GoEmotions was trained on Reddit comments. Applying it back to Reddit measures meditation-talk *relative to a Reddit baseline*, not absolute emotional content. I document this circularity directly in the methodology page. The dataset will be released under CC BY 4.0 with a forthcoming HuggingFace publication.
>
> I can provide this as:
>
> - A 1,200-word feature essay illustrated with the original data visualizations
> - A Q&A with your editor
> - A methodological brief for your peer-reviewed adjacent venues (if Mind & Life or another partner is appropriate)
> - Or just access to the visualization for your team to reference in your own coverage
>
> Code, dataset, methodology: github.com/minyansh7/MindSpace-OS
>
> Thank you for your time. Happy to provide additional context, raw data, or revised framings as useful.
>
> Warm regards,
> Minyan Shi
> Minyan Labs · Sydney
> mindspaceos.com

---

## Section 12 — Custom domain cutover

The site is currently at `mindspace-os.pages.dev`. Canonical target: `mindspaceos.com`.

### Two-step cutover

1. **Register `mindspaceos.com`** via Cloudflare Registrar (~$10.44/yr): https://dash.cloudflare.com/985e6531724a5e9ce8670a37ead0d6f1/domains/register
2. **Attach to Pages project**: https://dash.cloudflare.com/985e6531724a5e9ce8670a37ead0d6f1/pages/view/mindspace-os/domains → "Set up a custom domain" → enter `mindspaceos.com`

SSL provisions automatically in ~5 minutes.

### Hardening (15 extra minutes)

Full DNS records (Always-Use-HTTPS, DNSSEC, null MX, SPF, DMARC, Email Routing for `takedown@`, `hello@`, `press@`) live in: **`docs/dns-hardening-records.md`**.

Includes 6 verification commands (`curl`, `dig`) to confirm each record landed.

### What changes in the codebase after cutover

**Nothing critical.** `astro.config.mjs:site` is already `https://mindspaceos.com`, so:
- All sitemap entries auto-resolve to canonical domain
- All OG meta tags auto-resolve to canonical domain
- All canonical links auto-resolve
- All JSON-LD URL fields auto-resolve

Only post-cutover housekeeping: drop the `mindspace-os.pages.dev` fallback note from README + CLAUDE (cleanup PR can land same day).

---

## Section 13 — Post-launch follow-ups

Track these for the May → June arc.

### Week of May 1
- Post Tweet 1 + pin
- Submit HN
- Bluesky 1
- Email pitches to Mindful, Greater Good, NAMI blog (if not already sent in late April)

### Week of May 5–10
- Targeted DMs to Tara Brach, Sharon Salzberg, Sebene Selassie (Angle 3)
- Standalone Tweet 3 + Bluesky 3

### Week of May 12–17
- Targeted DMs to Jud Brewer, Stevie Chancellor (Angle 4 + Angle 5)
- Submit r/dataisbeautiful

### Week of May 19–24
- Mona Chalabi, Federica Fragapane, Pudding pitch (Angle 1)
- Standalone Tweet 2 + Bluesky 2

### Week of May 26–31
- Retro thread showing what hit
- Outreach to Aeon / Psyche / Asterisk for long-form essay (June or July publication)
- Begin HuggingFace dataset prep for ICWSM/CSCW timing

### Metrics to watch (Cloudflare Web Analytics — already enabled when domain is live)

- Daily uniques (target: 25k in first 30 days, locked decision per upgrade plan)
- Top referrers (HN, Substack, Twitter, Bluesky breakdown)
- Bounce rate per page (`/` vs `/explore/*` vs `/about`)
- Substack subscriber count delta (essays.mindspaceos.com when live)

---

## Appendix — File map

| Doc | What |
|---|---|
| `README.md` | Project overview, tech stack, quick start |
| `CLAUDE.md` | Design intent, color palette, deploy notes |
| `docs/upgrade-plan.md` | The locked v2 plan (autoplan output) |
| `docs/dns-hardening-records.md` | Cloudflare DNS records for canonical-domain cutover |
| `docs/dvs-mental-health-month-submission.md` | DVS Nightingale-specific submission write-up |
| `docs/launch-playbook.md` | This file |
| `docs/mobile-interactive-scoping.md` | Day-30 mobile re-eval scoping |
| `assets/featured-images/dvs-2026-04-27/` | All 7 Modern-3 PNG sizes + source HTML + source charts |

---

*This playbook is a living document. Update Section 13 (follow-ups) after each launch action, and Section 8 (critique replies) when new patterns of pushback emerge.*
