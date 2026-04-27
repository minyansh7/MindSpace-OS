# Data Visualization Society — Mental Health Awareness Month submission

Submission write-up for the Data Visualization Society (DVS) Mental
Health Awareness Month showcase (May). Use this as the portal
description, the accompanying long-form post, and the social copy.

---

## Title

**MindSpace OS — What 2,899 Reddit Posts on Meditation Actually Sound Like**

## Tagline (≤140 chars)

A six-quarter portrait of r/meditation. Joy ranks 25th of 28 emotions. The
dominant vocabulary isn't calm — it's *I'm trying again*.

## One-paragraph summary (for the portal description field)

MindSpace OS is an editorial mapping of r/meditation across six quarters
(January 2024 – June 2025), built from 2,899 posts and comments. Four
interactive chart pages — emotional archetypes, poster→commenter response
patterns, sentiment over time, and theme co-occurrences — share a single
thesis: meditation discourse is *struggle wrapped around curiosity*, not
the calm-and-bliss register the wellness industry sells. Built solo over
six weeks of evening time, with explicit anti-wellness design choices
(earth-pigment palette, editorial typography, no gradient backgrounds, no
breathing-room platitudes).

---

## Why this belongs in Mental Health Awareness Month

Most mental-health visualization in awareness-month coverage shows what
*clinicians* know — prevalence rates, treatment-gap statistics, suicide
hotline data. This submission shows what *the community itself sounds
like* when it talks about its own practice in a public, anonymous,
non-clinical setting. That's a viewpoint awareness-month coverage almost
never includes — the patient's own vocabulary, before the clinical lens.

Three findings that reframe the awareness conversation:

1. **Joy ranks 25th of 28 emotion categories.** Curiosity, caring, and
   gratitude rank top-3. People meditate the way they journal — to work
   through, not to feel calm. The wellness industry's "find your calm"
   marketing doesn't match what users are actually saying.
2. **Response patterns are emotion-asymmetric.** When someone posts about
   grief, 25% of replies mirror that emotion. When someone posts about
   anxiety, only 7% do. The community has different reflexes for
   different distress types — a finding directly useful for the design
   of mental-health peer-support spaces.
3. **The conversation's emotional center is steady; the flashpoints
   rotate.** Anxiety + Self-Regulation hold 25–30% of posts every
   quarter, but in the high-engagement layer their share swings 24% →
   1% → 25% across six quarters. Distress doesn't leave the room — it
   suppresses and resurfaces.

These are not "isn't meditation lovely" findings. They are a gentler,
truer portrait of how a real community holds itself.

---

## Chart tour (for the portfolio page / Substack accompaniment)

### 1. Emotion Pulse — `mindspaceos.com/explore/emotion-pulse/`

A UMAP scatter of every post embedded with GoEmotions. Five emotional
archetypes emerge from HDBSCAN clustering: Reflective Caring, Soothing
Empathy, Tender Uncertainty, Melancholic Confusion, Anxious Concern.
A radar overlay updates on hover (or tap, on mobile) to show each
point's emotion profile. The seed point chosen on page load is Tender
Uncertainty — the centroid of the corpus's actual emotional register.

### 2. Community Dynamics — `mindspaceos.com/explore/community-dynamics/`

A Sankey of how poster archetypes flow into commenter archetypes.
Asks: when someone posts in *Anxious Concern*, how does the community
respond? Three normalized hover views (Global Share / Poster Share /
Commenter Share) answer different questions — landscape vs reception
vs attraction. The headline: grief gets mirrored 25% of the time;
anxiety gets reassurance 7%.

### 3. Community Weather Report — `mindspaceos.com/explore/community-weather-report/`

A weather-map metaphor for sentiment by topic by quarter. Seven topic
clusters rendered as regions, each tinted by mean sentiment in the
quarter, with five sentiment bands — sunny, clearing up, cloudy, light
showers, storm warning. *Luckily, nothing stormy* across the entire
six-quarter run — the data does not validate the panic register that
some mainstream coverage uses.

### 4. Inner Life Currents — `mindspaceos.com/explore/inner-life-currents/`

A temporal co-occurrence network. Each line connects two themes that
came up in the same conversation; thicker line means more engaged
discussion. A Time Travel slider walks through the six quarters — the
filtered network shows which theme pairings dominated the most active
threads in each window. This is where the U-shape rotation finding
becomes visible.

---

## Methodology — plain English

- **Source:** r/meditation public posts and comments via the Reddit
  API, January 2024 – June 2025. 2,899 documents after deduplication
  and minimum-length filter.
- **Sentiment + emotion:** GoEmotions classifier (Demszky et al. 2020,
  arXiv:2005.00547). 28 emotion categories per document. We
  acknowledge the GoEmotions training set is Reddit-sourced and skews
  toward Reddit-native vocabulary — bias notation appears on every
  chart's methodology footnote.
- **Embeddings:** Sentence-transformer model. Reduced via UMAP
  (McInnes et al. 2018) to 2D for the Emotion Pulse scatter.
- **Clusters:** HDBSCAN on the UMAP embedding. Five emotional
  archetypes named editorially after inspection of cluster centroids.
- **Filtering for Inner Life Currents:** edges kept only when
  engagement > 30 AND |sentiment| > 0.3. The Weather Report and
  Emotion Pulse use the unfiltered corpus; Currents shows the
  high-engagement layer.
- **Stack:** Python (pandas, plotly, sentence-transformers, hdbscan,
  umap-learn) for analysis. Astro + baked Plotly HTML for the
  editorial site. Cloudflare Pages for hosting. No runtime backend,
  no cold starts.

Full methodology page on the site.

---

## Design philosophy — what's deliberately *not* here

Wellness-app design conventions we excluded on purpose:

- **No gradient backgrounds.** Editorial cream / off-white only.
- **No tropical / pastel palette.** Earth pigments — oxblood for
  clinical anxiety, mustard ochre for noticing/awareness, aubergine
  for Buddhist iconography, deep teal for focused depth, forest green
  for meditation as labor (not lifestyle), walnut brown for daily
  practice, terracotta for embodied warmth. Palette earned each
  cluster in one word.
- **No breathing-room platitudes.** No "take a moment" copy. No mantra
  cards. The site treats the reader as a researcher or an editor, not
  as a meditation customer.
- **No animated "calming" backgrounds.** A weather map that changes
  with the sentiment band, a network that re-flows quarter by quarter
  — animation in service of data, not in service of mood.

The lineage we did borrow from: NYT Upshot, Pudding, FT Visual data
journalism. Long-form editorial pages with one chart and a clear
thesis sentence above it.

---

## Ethical considerations

Reddit posts are technically public but meditators write about
intensely private experiences (grief, dissociation, panic, suicidal
ideation in the lurker layer). We took the following safeguards:

- **Paraphrase policy.** No post is quoted verbatim on the published
  site. Hover-text on the Emotion Pulse scatter shows light
  paraphrases, not the original strings.
- **No usernames, no permalinks** in the published site. The
  underlying parquet retains post IDs for reproducibility but the
  editorial layer never exposes them.
- **Takedown contact.** Documented on the methodology page. Any
  mediator user who recognizes their post can request removal from
  the published artifacts.
- **License.** Source code MIT. Processed dataset (the parquets, no
  raw text) under CC-BY-NC for academic use. Raw Reddit corpus is
  not redistributed.

---

## Author + links

- Built by Min Yan (Minyan Labs).
- Site: https://mindspaceos.com
- Two essays establishing the thesis (Substack):
  - *What 3,000 Reddit Posts on Meditation Actually Sound Like* (Apr 21, 2026)
  - *Meditation Communities Are Not as Calm as They Look* (Apr 24, 2026)
- Capstone v2 essay: {{LAUNCH_URL}} (publishing {{LAUNCH_DATE}})
- Open dataset: HuggingFace, with Zenodo DOI (link once published)
- Source: github.com/minyansh7/MindSpace-OS

---

## DVS submission checklist

- [ ] Project URL: `https://mindspaceos.com`
- [ ] Hi-res still images (1200×675, dark mode) for each chart — drop
      into `site/public/og/`
- [ ] One animated GIF / short MP4 (≤6s) showing Time Travel slider
      walking through Inner Life Currents
- [ ] 140-char tagline (above)
- [ ] One-paragraph summary (above) for portal description field
- [ ] Author bio (≤80 words) — pull from `site/src/pages/about.astro`
- [ ] Tag taxonomy: `mental-health`, `community`, `reddit`,
      `editorial`, `umap`, `goemotions`, `sentiment`, `network`,
      `sankey`, `awareness-month`
- [ ] Submission window: confirm DVS portal opens before launch day
      ({{LAUNCH_DATE}}); if open earlier, submit ahead of public
      site launch with a "preview" note

## Social copy (for DVS Twitter/LinkedIn handle if they pick it up)

> A six-quarter portrait of r/meditation. Joy ranks 25th of 28 emotions.
> Anxiety + Self-Regulation hold ~25–30% of posts every quarter — but
> in the high-engagement layer their share swings 24% → 1% → 25%.
> The community's distress vocabulary suppresses and resurfaces.
>
> https://mindspaceos.com — built solo for Mental Health Awareness Month
