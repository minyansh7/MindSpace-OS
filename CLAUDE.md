# CLAUDE.md

Design-intent notes and editorial copy for the MindSpace OS site.
This file documents rationale, removed-but-preserved marketing copy,
and conventions that are not obvious from the code alone.

## Page-by-page editorial notes

### Inner Life Themes (`pages/2_Inner_Life_Themes.py`)

Previously titled "Main Topics Sankey" / "Main Topics", then "Theme Pathways".
Renamed to "Inner Life Themes" on 2026-04-23 as part of the unified
"Inner Life" naming family across pages 2–5.

Removed descriptive line from the page header on 2026-04-21 per editorial
decision to let the chart speak for itself (data-ink ratio / Tufte):

> "This Sankey diagram blends top flowing themes into topic families using
> harmonious colors for clarity and beauty."

Kept here for reference in case the description is wanted back or needed
as alt text / meta description.

### Inner Life Trees (`pages/5_Inner_Life_Trees.py`)

Previously titled "Professional River Flow" (h1) and "Cocurrence Mapping complex"
(sidebar), then "Narrative Trees". File renamed from `5_Cocurrence_Mapping_complex.py`
on 2026-04-21 and to `5_Inner_Life_Trees.py` on 2026-04-23.

Removed subtitle on 2026-04-21:

> "Living Narrative Intelligence Platform"

Rationale: the subtitle overlapped the meaning of the h1 and competed
visually with the chart below. The eyebrow-styled "QUARTER <label>"
line that replaced it now communicates the one piece of state the user
actually needs before scrolling: which quarter of data they're looking at.
Character style matches the "TIME TRAVEL" eyebrow above the slider for
typographic consistency.

### Inner Life Currents (`pages/4_Inner_Life_Currents.py`)

Previously titled "The Connected Narrative" (h1) and "Cocurrence Mapping
Over Time" (sidebar), then "Theme Currents". Renamed to "Inner Life
Currents" on 2026-04-23. Shows how theme co-occurrences evolve quarter
by quarter via the shared quarter slider.

### Inner Life Web (`pages/3_Inner_Life_Web.py`)

Previously titled "The Narrative Web" (h1) and "Cocurrence Mapping"
(sidebar), then "Theme Web". Renamed to "Inner Life Web" on 2026-04-23.
Shows the static co-occurrence network across all data (no time axis).

## Color palette (canonical cluster→color mapping)

Both Inner Life Currents and Inner Life Trees render the same 7 theme clusters.
They must use identical colors so the site reads as one visual language.

The reference is the Inner Life Trees chart rendering, which feeds clusters
through `script_custom_cmap` indexed by alphabetically sorted cluster name:

| Cluster                      | Hex       | Name   |
|------------------------------|-----------|--------|
| Anxiety & Mental Health      | `#1f77b4` | blue   |
| Awareness                    | `#808000` | olive  |
| Buddhism & Spirituality      | `#ff7f0e` | orange |
| Concentration & Flow         | `#d62728` | red    |
| Meditation & Mindfulness     | `#9467bd` | purple |
| Practice, Retreat, & Meta    | `#8c564b` | brown  |
| Self-Regulation              | `#17becf` | cyan   |

Inner Life Currents' `topic_mapping` dict was synced to match on 2026-04-21.

## Page ordering and naming family

Sidebar order (derived from the leading numeric prefix in `pages/*.py`):

1. Emotion Pulse              — `0_Emotion_Pulse.py`
2. Meditation Weather Report  — `1_Meditation_Weather_Report.py`
3. Inner Life Themes          — `2_Inner_Life_Themes.py` (Sankey)
4. Inner Life Web             — `3_Inner_Life_Web.py` (static co-occurrence network)
5. Inner Life Currents        — `4_Inner_Life_Currents.py` (temporal network)
6. Inner Life Trees           — `5_Inner_Life_Trees.py` (river-flow, filterable, last)

The four relationship-oriented pages (3–6) visualize theme connections
from progressively more dynamic angles under the shared "Inner Life" family:

- **Inner Life Themes**: Sankey of how top themes flow into topic clusters
  (broad, read-once overview)
- **Inner Life Web**: static co-occurrence graph — who connects to whom
  across the full archive
- **Inner Life Currents**: the same connections rendered as a temporal
  network, quarter by quarter
- **Inner Life Trees**: deep branching view with engagement-level
  filters, sentiment filters, quarter slider, and a sidebar analytics
  panel — the most interactive page, and the final stop in the tour

So the progression is: *flow → static snapshot → temporal motion → deep
filterable drill-down*. The last page is the most interactive by design.

Together, the four form a metaphor family — themes, trees, web,
currents — each a tangible natural form grouped under "Inner Life".

Archived (kept in repo but hidden from sidebar): `archive/0_Emotion_Pulse_v.py`

## Typographic conventions

**Eyebrow labels** (small uppercase metadata above a value):
`font-size: 13px; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase;`

Used for: "TIME TRAVEL" above the quarter slider, "QUARTER" below the
Inner Life Trees title, and any future top-of-card metadata.

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
  Planned as a follow-up post to the 48k-Reddit intro in
  `drafts/launch-post.md`.
