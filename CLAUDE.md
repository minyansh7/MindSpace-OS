# CLAUDE.md

Design-intent notes and editorial copy for the MindSpace OS site.
This file documents rationale, removed-but-preserved marketing copy,
and conventions that are not obvious from the code alone.

## Two surfaces, one repo

MindSpace OS ships two sibling deliverables from this repo:

1. **Astro editorial site** (`site/`). Static build, the public reading
   experience. Lives at `site/dist/` after `npm run build`. Hosted on
   Cloudflare Pages (project `mindspace-os`, account
   `985e6531724a5e9ce8670a37ead0d6f1`):
   - Current live URL: https://minyansh7-mindspace-os-publi.mindspace-os.pages.dev
     (canonical domain `mindspaceos.com` once DNS lands).
   - Branch previews: `https://<branch>.mindspace-os.pages.dev`
     auto-built per push when Cloudflare Git integration is connected.
2. **Streamlit interactive app** (`Homepage.py` + `pages/*.py`). Source of
   truth for chart logic. Hosted on Streamlit Cloud at
   https://mindspaceos.streamlit.app . **The editorial site no longer
   iframes the Streamlit app at runtime** — see "Streamlit-to-static
   migration" below.

Canonical data shared by both surfaces lives in `data/canonical.json`
(post counts, archetype palette, page metadata, essay listings). Python
reads it directly; the Astro site reads it via `site/src/lib/canonical.ts`.
A vitest in `site/tests/canonical.test.mjs` enforces no-inline-duplicates.

## Streamlit-to-static migration (2026-04-26)

Originally the editorial site iframed `mindspaceos.streamlit.app/<page>`
for each chart, which meant Streamlit Cloud cold-starts (10–30s) and
Streamlit chrome (sidebar, "Built with Streamlit" footer) leaked into the
reading experience. As of 2026-04-26 all four chart pages render from
self-contained static HTML at `site/public/charts/*.html`, baked by
`python3 scripts/build_chart_figures.py`:

- **`emotion-pulse.html`** (~1.7 MB) — full UMAP scatter with all 2,899
  hover_text strings inlined, archetype radar overlay updates on
  `plotly_hover`. Plotly trace JSON pre-built from
  `precomputed/emotion_clusters_slim.parquet`.
- **`community-dynamics.html`** (~22 KB) — Sankey from
  `precomputed/figures/community_dynamics_sankey.json`. POSTER/COMMENTER
  column eyebrows relabeled to POST/COMMENT and customdata strings
  patched in-place at build time. `layout.height` stripped so the flow
  fills the iframe; `autosize: true` set so it responds to container.
- **`inner-life-currents.html`** (~563 KB) — temporal theme network with
  all 6 quarters' payloads inlined and a JS Time-Travel state machine
  swapping the active payload via `Plotly.react`. Top-10 edges by weight
  rendered with full opacity + hover; the rest fade back as visual
  texture. Cluster labels distributed around the full 2π circle with a
  collision-avoidance pass so adjacent labels don't overlap.
- **`community-weather-report.html`** (~63 KB) — stats bar, weather map
  with seven CSS-animated regions (sunny-pulse, hope-breathe,
  contemplative-drift, gentle-rain-shake, storm-alert), per-condition
  hover ripple bloom, and a Sentiment River Flow Analysis section
  (per-topic cards with QoQ change badge + top-3 challenges by severity).
  Meditation & Mindfulness gets a 0.85x size multiplier so it doesn't
  crowd neighbors. Region positions tuned to keep satellites clear of
  the legend and edges.

Re-run `python3 scripts/build_chart_figures.py` whenever:
- The canonical archetype palette in `data/canonical.json` or the
  `TOPIC_MAPPING` / `WEATHER_TOPIC_COLORS` dicts in the build script change.
- A Streamlit page changes its figure construction or hover template
  (the build script re-implements the Plotly/HTML output rather than
  importing from the Streamlit modules, since they have `st.set_page_config`
  side effects).
- The underlying parquet aggregates in `precomputed/` change.

`<StaticChart src="emotion-pulse.html" />` in
`site/src/components/StaticChart.astro` iframes the local file (zero CORS,
zero cold-start) and appends `?tod=<dawn|morning|...|night>` so each chart
HTML can theme itself in lockstep with the homepage gradient.

The Streamlit Cloud app at `mindspaceos.streamlit.app` still works for
direct-link visitors and remains the development surface for chart
iteration, but the editorial site never depends on it at runtime.

## Deploy

The Astro site goes live on Cloudflare Pages two ways:

- **Cloudflare Git integration (preferred)** — connect at
  https://dash.cloudflare.com/985e6531724a5e9ce8670a37ead0d6f1/pages/view/mindspace-os/settings/builds-deployments
  with build settings: root directory `site`, build command `npm run build`,
  output directory `dist`, framework preset Astro. After this, every push
  to GitHub triggers a Cloudflare build automatically.
- **Manual one-shot** — `cd site && npm run build && npx wrangler pages
  deploy dist --project-name=mindspace-os --branch=<git-branch>`. Used
  when Git integration isn't wired or for ad-hoc previews. Requires
  `wrangler login` first.

**Important:** the chart bake (`python3 scripts/build_chart_figures.py`)
must run BEFORE the Astro build, since the Astro static iframes reference
`site/public/charts/*.html` files. If you forget, the chart pages will
404. Add this to any CI pipeline that builds the site.

## Page-by-page editorial notes

### Community Dynamics (`pages/2_Community_Dynamics.py`)

Previously titled "Main Topics Sankey" / "Main Topics", then "Theme Pathways",
then "Inner Life Themes" (2026-04-23).

Renamed to **Community Dynamics** on 2026-04-24 when the chart itself was
replaced: instead of theme→cluster flow (from `main_topics.parquet`), the
Sankey now shows **poster emotional archetype → commenter emotional
archetype** (from `emotion_clusters.parquet`, joined on the post_id
embedded in the comment URL). The page stepped out of the "Inner Life"
naming family because the new chart's story is social/relational, not
topical.

Column eyebrow labels `POSTER` / `COMMENTER` sit above the plot as small-
caps metadata (same typographic treatment as the "TIME TRAVEL" eyebrow),
matching the source screenshot.

Node ordering: descending volume per side. Node colors pull from
`ARCHETYPE_COLORS` in `pages/0_Emotion_Pulse.py` (canonical archetype
palette — must stay in sync across the two pages). Link ribbons are
colored by the poster's archetype at `rgba(..., 0.4)`.

Link hover shows three normalized views of the same count: Global Share
(of all pairs), Poster Share (of that poster's outgoing flow), and
Commenter Share (of that commenter's incoming flow). Each answers a
different question — landscape, reception, attraction.

Removed descriptive line on 2026-04-21 (from the predecessor chart) per
data-ink ratio:

> "This Sankey diagram blends top flowing themes into topic families using
> harmonious colors for clarity and beauty."

Kept here for reference.

### Inner Life Trees — archived 2026-04-24

Previously at `pages/5_Inner_Life_Trees.py` (titled "Professional River Flow"
→ "Narrative Trees" → "Inner Life Trees"). Archived to
`archive/5_Inner_Life_Trees.py` on 2026-04-24 and removed from the live
sidebar. The remaining three "Inner Life" pages (Themes, Web, Currents)
are the ongoing naming family.

### Inner Life Currents (`pages/3_Inner_Life_Currents.py`)

Previously titled "The Connected Narrative" (h1) and "Cocurrence Mapping
Over Time" (sidebar), then "Theme Currents". Renamed to "Inner Life
Currents" on 2026-04-23. Shows how theme co-occurrences evolve quarter
by quarter via the shared quarter slider.

### Inner Life Web — archived 2026-04-24

Previously at `pages/3_Inner_Life_Web.py` (titled "The Narrative Web"
→ "Cocurrence Mapping" → "Theme Web" → "Inner Life Web"). Archived to
`archive/3_Inner_Life_Web.py` on 2026-04-24 and removed from the live
sidebar. The static co-occurrence view was made redundant by
Inner Life Currents (which carries the same connections plus a time
axis), so the site was simplified to a single network page.

### Community Weather Report (`pages/2_Community_Weather_Report.py`)

Previously titled "Meditation Weather Report". Renamed to "Community
Weather Report" on 2026-04-24 to sit thematically alongside Community
Dynamics — both pages tell the *community* story (who meets whom, and
how the mood shifts over time). Page content is unchanged; the rename
is purely editorial.

## Color palette (canonical cluster→color mapping)

Editorial earth-pigment palette (NYT Upshot / Pudding / FT Visual lineage).
Replaced the matplotlib defaults on 2026-04-26 after a /design-consultation
review with two outside voices both rejecting matplotlib defaults as
"Jupyter notebook colors" and the prior Weather Report saturated tropical
palette as wellness-app coded — both wrong for an editorial data-journalism
site explicitly positioned against wellness aesthetics.

Each color earns its cluster in one word: oxblood for clinical anxiety,
mustard ochre for noticing/awareness, aubergine for Buddhist robe iconography
(non-cliché), deep teal for focused depth, forest green for meditation as
labor (not lifestyle), walnut brown for daily zafu/monastery practice,
terracotta for embodied warmth.

| Cluster                      | Hex       | Name           |
|------------------------------|-----------|----------------|
| Anxiety & Mental Health      | `#B23A48` | oxblood red    |
| Awareness                    | `#E8A93B` | mustard ochre  |
| Buddhism & Spirituality      | `#6B4F8F` | muted aubergine|
| Concentration & Flow         | `#1F6F8B` | deep teal      |
| Meditation & Mindfulness     | `#4A7C59` | forest green   |
| Practice, Retreat, & Meta    | `#8B6F47` | walnut brown   |
| Self-Regulation              | `#D97757` | terracotta     |

Pages using this palette (must stay in sync):
- `pages/3_Inner_Life_Currents.py` → `topic_mapping` dict
- `scripts/build_chart_figures.py` → `TOPIC_MAPPING` (Inner Life Currents
  static build) and `WEATHER_TOPIC_COLORS` (Community Weather Report —
  primary is canonical, secondary/border derived for gradient/border use)

Legibility caveat: the earth palette sits ~35–55% luminance, so on the
homepage's time-of-day gradient backgrounds two pairings can be tight
(forest-green on morning teal, terracotta on dawn coral). For weather-map
regions specifically, add a 1px dark stroke on small chips. For chart
panels (white card, deep navy network background), no mitigation needed.

## Page ordering and naming family

Sidebar order (derived from the leading numeric prefix in `pages/*.py`):

1. Emotion Pulse              — `0_Emotion_Pulse.py`
2. Community Dynamics         — `1_Community_Dynamics.py` (Sankey, poster → commenter)
3. Community Weather Report   — `2_Community_Weather_Report.py` (sentiment over time)
4. Inner Life Currents        — `3_Inner_Life_Currents.py` (temporal theme network)

The four live pages tell one story arc, from individual emotional
vocabulary to community mood to theme connections over time:

- **Emotion Pulse**: introduces the 5 emotional archetypes via a UMAP
  map of the GoEmotions embedding
- **Community Dynamics**: Sankey of how those archetypes flow from
  posters to their commenters (who responds to whom, emotionally)
- **Community Weather Report**: 18 months of sentiment across topics,
  rendered as weather metaphors — *how the community mood shifts*
- **Inner Life Currents**: theme co-occurrences rendered as a temporal
  network, quarter by quarter

So the progression is: *individual → social → temporal mood → temporal
theme connections*.

Archived (kept in repo but hidden from sidebar):
- `archive/0_Emotion_Pulse_v.py`
- `archive/3_Inner_Life_Web.py` (static co-occurrence network;
  retired 2026-04-24, superseded by Inner Life Currents)
- `archive/5_Inner_Life_Trees.py` (was the deep filterable drill-down;
  retired 2026-04-24)

## Precomputed artifacts (perf tier-3)

`scripts/build_precomputed.py` produces two artifacts under `precomputed/`
that the site loads directly, so the runtime never rebuilds them:

- **`precomputed/emotion_clusters_slim.parquet`** — the 4 columns the
  Emotion Pulse page actually reads (`umap_x`, `umap_y`, `hover_text`,
  `archetype_label`) with `hover_text` already wrapped to the 75-char
  tooltip width. Shrinks the source parquet from 3.7 MB to ~420 KB and
  removes the 2,977-row Python wrap loop from cold-start cost.
- **`precomputed/figures/community_dynamics_sankey.json`** — the full
  Plotly figure JSON for the Community Dynamics Sankey (poster → commenter
  emotional archetype flow). The page calls `plotly.io.from_json()` to
  load it, skipping the groupby / palette / hover-text formatting that
  would otherwise run on every cold start. 5 nodes per side → small
  payload (~20 KB), effectively free to parse.

Run `python3 scripts/build_precomputed.py` whenever the source parquet
(`precomputed/emotion_clusters.parquet`) changes, or the wrap rules /
archetype palette / Sankey hover template in the build script change.
The source parquet is kept in the repo for reproducibility.

## Typographic conventions

**Eyebrow labels** (small uppercase metadata above a value):
`font-size: 13px; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase;`

Used for: "TIME TRAVEL" above the quarter slider and any future
top-of-card metadata.

**Page title h1**: `font-size: 3rem; font-weight: 800`.

**Footers**: powered-by-Terramare mark is intentional brand; keep.

## Hover/tooltip policy

Plotly hover text is pre-wrapped to 75 characters per line (see
`wrap_hover_text` in `pages/0_Emotion_Pulse.py`) so tooltips fit
inside the chart container at typical desktop widths. Plotly does
not auto-wrap; the 75-char pre-wrap is the constraint.

## Session state

Time-trend pages share `st.session_state.slider_index` so switching
between pages preserves the selected quarter. Default is
`len(quarter_labels) - 1` (the latest quarter, currently 2025Q2).

## Target viewport: desktop only

As of commit `62b4a11b`, all mobile optimization was deliberately removed
(`mobile.py`, `is_mobile()` branches in Plotly pages, and
`@media (max-width: 768|480|320px)` blocks in `components.html` iframes).

Design intent: this is a data-storytelling site meant to be read on a
desktop-sized viewport. The mobile pass shipped briefly and was pulled
back because the cost of maintaining two render paths (and the risk of
leaking mobile tweaks into desktop) wasn't justified by the mobile
traffic the site was actually getting. The `@media (max-width: 1200px)`
blocks remain — those handle narrow-but-still-desktop sizing.

If mobile ever returns, the previous implementation is in the git
history (see the diff of `62b4a11b`) and the retrospective is in
`docs/publish_draft.md`.

## Launch workflow (`drafts/`)

Launch copy and automation for publishing the site live:

- **`drafts/launch-post.md`** — the canonical source of truth for both
  Substack post and Twitter copy. Has a `## Substack Post` section
  (title / subtitle / body) and a `## Twitter / X Posts` section with
  options A/B/C plus thread follow-ups. All posting scripts parse this
  file, so edit markdown → re-run, no re-coding needed.
- **`drafts/post_to_substack.py`** — interactive Playwright runner.
  `--login` flow persists session; `--draft` inserts the draft into
  the Substack editor. Stops before the Publish click (guardrail).
- **`drafts/post_to_twitter.py`** — same pattern for X/Twitter. Supports
  `--option A|B|C`, `--thread` (posts the full chain), `--review` (fills
  compose but doesn't click Post), and `--link URL` (substitutes
  `[link]` placeholders).
- **`drafts/post_all.sh`** — orchestrator. Runs the Substack drafter →
  waits for the user to publish manually and paste the live URL →
  runs the Twitter poster with `--link <URL>` substituted. Chains the
  whole launch in one flow.
- **`drafts/post_substack_auto.py`** / **`post_twitter_auto.py`** —
  non-interactive variants. No `input()` pauses; they poll for
  authenticated state instead. Built for agent-invoked execution.
  Known limitation: X's anti-automation currently blocks sign-in in
  a Playwright-controlled Chromium.

Profile directories (`~/.playwright-profiles/substack-<slug>/`,
`~/.playwright-profiles/twitter/`) persist browser sessions between
runs — log in once, reuse indefinitely.

## Related writeups (`docs/`)

- **`docs/publish_draft.md`** — long-form retrospective on the 13-hour
  UX pass that produced the Themes/Trees/Web/Currents naming family
  (later unified as "Inner Life Themes/Trees/Web/Currents"),
  the one-H1 header convergence, and the (now-removed) mobile rollout.
  Planned as a follow-up post to the r/meditation intro in
  `drafts/launch-post.md`.
