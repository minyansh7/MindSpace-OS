# Proposed plans — for review

This file holds proposals that are waiting on your review before implementation.
Nothing here has been built. When you approve an item, I execute it and remove
the entry.

Related files:
- `CLAUDE.md` — design-intent notes for shipped decisions
- `demo/Homepage_v2.py` — runnable homepage redesign preview
- this file — pending proposals

---

## 1. Subtitle candidates (hybrid H1 + insight-subtitle pattern)

Per the research agent's finding, the hybrid pattern keeps the brand H1
(e.g. "Emotion Pulse") as a stable nav anchor and adds a **declarative
subtitle** under it that delivers a defensible finding. Tradeoffs:
two-line headers use more vertical space and every subtitle has to stay
fresh.

For each page, three candidate subtitles below. **I've tried to keep them:**
- Declarative (state what the chart shows, not what you should feel)
- Defensible (no unvalidated "clusters" / statistical claims I can't back up)
- Non-literary (plain language, not metaphor)
- Short (≤ 18 words)

Pick one per page, edit, or tell me to redraft.

### #01 Emotion Pulse
Current H1: **Emotion Pulse** · subtitle: *What people feel*
Data: UMAP of posts colored by dominant emotion (GoEmotions 27-category model).

- **A** — "2,977 r/meditation posts, each colored by its dominant emotion."
- **B** — "Posts using similar emotional language sit close together on this map."
- **C** — "Where the conversation's emotional vocabulary lands — one dot per post."

### #02 Meditation Weather Report
Current H1: **Meditation Weather Report** · subtitle: (currently none)
Data: sentiment over time, by topic, with "weather" metaphor for valence.

- **A** — "Sentiment across r/meditation topics, quarter by quarter (Jan 2024 – Jun 2025)."
- **B** — "How the mood on each meditation topic shifts across six quarters."
- **C** — "Forecasting sentiment: which topics run sunny, stormy, or mixed."

### #03 Theme Pathways
Current H1: **Topic Flow: How Themes Connect** · subtitle: *What People Say Most*
Note: this H1 is already insight-oriented ("how themes connect") so the
subtitle can stay descriptive/short.

- **A** — (keep current "What People Say Most")
- **B** — "Broad themes on the left flow into their top topics on the right."
- **C** — "Which themes produce which conversations."

### #04 Narrative Trees
Current H1: **Narrative Trees** · subtitle: `QUARTER 2025Q2` (eyebrow, not a prose subtitle)
Note: the eyebrow is functional — shows current quarter state. A prose
subtitle would have to fit above or below that.

- **A** — (keep as-is; eyebrow is functional, extra subtitle would compete)
- **B** — Add a subtitle ABOVE the eyebrow: "How meditation discussions branch across themes, filtered by engagement and sentiment."
- **C** — Add a subtitle ABOVE the eyebrow: "A filterable view of which topics co-occur, quarter by quarter."

### #05 Theme Web
Current H1: **Theme Web** · subtitle: *Where Narratives Collide*
Current subtitle is poetic/literary — a candidate for tightening per
the research.

- **A** — "Which meditation topics appear together across the full archive."
- **B** — "All co-occurrences at once — dots = posts, lines = shared topics."
- **C** — "The static map of which topics keep showing up together."

### #06 Theme Currents
Current H1: **Theme Currents** · subtitle: *Where Narratives Converge — And How They Evolve*
Current subtitle is two halves; the second half ("And How They Evolve")
is already insight-oriented.

- **A** — (keep current subtitle)
- **B** — "How theme connections shift across quarters — scrub the Time Travel slider."
- **C** — "Watching the conversation drift: quarter-by-quarter theme co-occurrences."

---

## 2. Per-chart static decluttering (from Part 4 of earlier plan)

Research-backed static changes per chart type. **No animation changes.**
Each item is evidence-based (Tufte data-ink ratio, Knaflic preattentive
focus, Cairo truthfulness).

These are **static visual changes** — things like hiding meaningless axes,
capping node counts, using a gray-and-highlight color scheme. Animations
(transitions, fades, hover-reveal timing) are NOT touched.

### Emotion Pulse (UMAP scatter)
- **Hide axis tick labels entirely.** UMAP axis values are arbitrary; showing
  them adds visual noise (Tufte: data-ink ratio).
- **Keep everything else as-is.** Colors, clustering labels, hover tooltips,
  seed box — all unchanged.

### Meditation Weather Report (heatmap)
- **HOLD** — the current implementation uses a heavy animated custom HTML
  visualization with "weather regions". Per your "no animation changes"
  constraint, no changes proposed here until you relax it.

### Theme Pathways (Sankey)
- **No change needed.** Sankey is already decluttered after the earlier
  emoji-removal pass.

### Narrative Trees (river flow)
- **Mute secondary streams to gray.** The chart currently uses 7 saturated
  colors for 7 theme tributaries. Pick the 3–5 highest-volume per quarter as
  saturated; mute the rest to `#cbd5e1` (light gray). Viewer attention
  follows the few focal streams.
  **Affects animation?** The streams animate in position/height over time.
  Color change is static and does not touch animation timings. ✓ safe under
  your constraint.
- **Alternative if above feels too aggressive:** keep all 7 colors but drop
  the color alpha on non-focal streams from 1.0 → 0.25.

### Theme Web (static network)
- **Cap visible edges by weight.** Currently edges below the engagement
  threshold are already filtered, but the remaining ~100 nodes can still
  hairball. Add a default top-N=40 nodes by engagement with a "Show all"
  toggle.
- **Default "Show all" = off.** First paint is always the simplified view.

### Theme Currents (temporal network)
- **Label only the top-10 nodes per quarter.** Currently all nodes get
  labels; on mobile and even on desktop the labels collapse into each other.
  Top-10 by degree stay visible; rest appear on hover only.

### Universal (all pages)
- **Drop Plotly modebar** on narrative charts (`displayModeBar: False`) —
  it's chartjunk on a scrolltelling page and doesn't help a reader-mode
  user.

### What's held (per your constraint)
- Any change that modifies transition timing, fade durations, motion paths,
  or the "river flow" streaming animation in Narrative Trees / Theme
  Currents / Weather Report. These are out-of-scope until you relax the
  "no animation changes" rule.

---

## 3. Mobile optimization rollout tracker

Target: improve mobile legibility with **zero change to desktop**.

Rollout sequence (each step is independently shippable):

| # | Step | Status | Desktop impact |
|---|---|---|---|
| 1 | `mobile.py` helper with `is_mobile()` | ⏳ | none |
| 2 | Emotion Pulse mobile branch (Plotly) | ⏳ | none |
| 3 | Theme Pathways mobile branch (Plotly Sankey) | ⏳ | none |
| 4 | Theme Web iframe `@media` CSS + node cap | ⏳ | none |
| 5 | Theme Currents iframe `@media` CSS | ⏳ | none |
| 6 | Narrative Trees iframe `@media` CSS | ⏳ | none |
| 7 | Weather Report iframe `@media` CSS or PNG fallback | ⏳ | none |

Approach (from the research brief):
- Detect via `st.context.headers["User-Agent"]` (regex match on `Mobi|Android|iPhone|iPad`)
- Desktop path is literally untouched: `if not is_mobile(): <existing code>`
- For Plotly pages: branch the render call; on mobile, disable modebar,
  bump hoverlabel font, tighten margins
- For `components.html` iframes: inject `@media (max-width: 768px)` CSS
  blocks inside the iframe HTML — desktop never matches the query so
  rendering is bit-identical

## Held items (require changes you've explicitly ruled out for now)

- Anything that modifies animation timings / motion paths on any chart
- Replacing custom JS viz with responsive D3 / Observable Plot
- Unified typography refactor across iframes
- Server-side SVG rendering

These can be revisited when you relax the "no desktop visual or animation
change" constraint.
