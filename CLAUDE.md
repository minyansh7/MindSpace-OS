# CLAUDE.md

Design-intent notes and editorial copy for the MindSpace OS site.
This file documents rationale, removed-but-preserved marketing copy,
and conventions that are not obvious from the code alone.

## Page-by-page editorial notes

### Theme Pathways (`pages/2_Theme_Pathways.py`)

Previously titled "Main Topics Sankey" / "Main Topics" on the page header.

Removed descriptive line from the page header on 2026-04-21 per editorial
decision to let the chart speak for itself (data-ink ratio / Tufte):

> "This Sankey diagram blends top flowing themes into topic families using
> harmonious colors for clarity and beauty."

Kept here for reference in case the description is wanted back or needed
as alt text / meta description.

### Narrative Trees (`pages/5_Cocurrence_Mapping_complex.py`)

Previously titled "Professional River Flow".

Removed subtitle on 2026-04-21:

> "Living Narrative Intelligence Platform"

Rationale: the subtitle overlapped the meaning of the h1 and competed
visually with the chart below. The eyebrow-styled "QUARTER <label>"
line that replaced it now communicates the one piece of state the user
actually needs before scrolling: which quarter of data they're looking at.
Character style matches the "TIME TRAVEL" eyebrow above the slider for
typographic consistency.

## Color palette (canonical cluster→color mapping)

Both page 3 (Cocurrence Mapping Over Time) and page 5 (Cocurrence Mapping
complex) render the same 7 theme clusters. They must use identical colors
so the site reads as one visual language.

The reference is page 5's chart rendering, which feeds clusters through
`script_custom_cmap` indexed by alphabetically sorted cluster name:

| Cluster                      | Hex       | Name   |
|------------------------------|-----------|--------|
| Anxiety & Mental Health      | `#1f77b4` | blue   |
| Awareness                    | `#808000` | olive  |
| Buddhism & Spirituality      | `#ff7f0e` | orange |
| Concentration & Flow         | `#d62728` | red    |
| Meditation & Mindfulness     | `#9467bd` | purple |
| Practice, Retreat, & Meta    | `#8c564b` | brown  |
| Self-Regulation              | `#17becf` | cyan   |

Page 3's `topic_mapping` dict was synced to match on 2026-04-21.

## Page ordering

Sidebar order (derived from the leading numeric prefix in `pages/*.py`):

1. Emotion Pulse            — `0_Emotion_Pulse.py`
2. Meditation Weather Report — `1_Meditation_Weather_Report.py`
3. Theme Pathways           — `2_Theme_Pathways.py`
4. Cocurrence Mapping Over Time — `3_Cocurrence_Mapping_Over_Time.py`
5. Cocurrence Mapping       — `4_Cocurrence_Mapping.py`
6. Cocurrence Mapping complex — `5_Cocurrence_Mapping_complex.py` (last)

"Cocurrence Mapping" was moved ahead of "complex" on 2026-04-21 so the
simpler view reads first and the more detailed analytical view sits at
the end of the flow.

Archived (kept in repo but hidden from sidebar): `archive/0_Emotion_Pulse_v.py`

## Typographic conventions

**Eyebrow labels** (small uppercase metadata above a value):
`font-size: 13px; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase;`

Used for: "TIME TRAVEL" above the quarter slider, "QUARTER" below the
Narrative Trees title, and any future top-of-card metadata.

**Page title h1**: `font-size: 3rem; font-weight: 800`.

**Footers**: powered-by-Terramare mark is intentional brand; keep.

## Hover/tooltip policy

Plotly hover text is pre-wrapped to 75 characters per line (see
`wrap_hover_text` in `pages/0_Emotion_Pulse.py`) so tooltips fit
inside the chart container on mobile viewports. Plotly does not
auto-wrap; the 75-char pre-wrap is the constraint.

## Session state

Time-trend pages share `st.session_state.slider_index` so switching
between pages preserves the selected quarter. Default is
`len(quarter_labels) - 1` (the latest quarter, currently 2025Q2).
