# Streamlit chart pages — embed follow-ups

> **Status: RESOLVED (2026-04-26).** The Astro editorial site no longer iframes
> Streamlit at runtime — all four chart pages now render from self-contained
> static HTML at `site/public/charts/*.html`, baked by
> `python3 scripts/build_chart_figures.py`. The issues catalogued below were
> fixed by the static-HTML migration. Kept for historical reference. See
> `CLAUDE.md` → "Streamlit-to-static migration (2026-04-26)" for the new
> rendering path.

The new `mindspaceos.com` Astro shell embeds the existing four Streamlit chart pages
via iframe at `/explore/<slug>/`. A live audit (2026-04-25) of the iframes at
1280×800 desktop revealed several issues that originate in the Streamlit pages
themselves, not the shell. This doc lists what to fix on the Streamlit side so the
shell renders cleanly.

## Issues found in the audit

### 1. Multipage sidebar always visible (CRITICAL)

The Streamlit Cloud multipage sidebar listing all 5 pages (Homepage / Emotion Pulse /
Community Dynamics / Community Weather Report / Inner Life Currents) is showing on
all 4 chart pages despite `?embed=true`. It eats ~150px of horizontal space and
duplicates the Astro shell's nav.

**Cause.** `Homepage.py` has `initial_sidebar_state="collapsed"`, but the four
chart pages do NOT. Streamlit re-expands the sidebar when navigating to a page that
doesn't set it.

**Fix.** Add `initial_sidebar_state="collapsed"` to each chart page's
`st.set_page_config(...)` call:

```python
# pages/0_Emotion_Pulse.py
st.set_page_config(
    page_title="Emotion Pulse",
    layout="wide",
    initial_sidebar_state="collapsed",  # add this
)

# pages/1_Community_Dynamics.py
st.set_page_config(
    page_title="Community Dynamics — Emotional Flow: From Poster to Commenter",
    layout="wide",
    initial_sidebar_state="collapsed",  # add this
)

# pages/2_Community_Weather_Report.py
st.set_page_config(
    page_title="Community Weather Report",
    layout="wide",
    initial_sidebar_state="collapsed",  # add this
)

# pages/3_Inner_Life_Currents.py
st.set_page_config(
    page_title="Inner Life Currents",
    layout="wide",
    initial_sidebar_state="collapsed",  # add this
)
```

### 2. Page H1 + subtitle + intro paragraph duplicate the Astro shell

Each Streamlit page renders its own H1 (e.g. "Inner Life Currents"), subtitle (e.g.
"Where Narratives Converge — And How They Evolve"), and intro paragraph at the top.
The Astro shell at `/explore/<slug>/` already shows the H1, subtitle, and a richer
editorial intro above the iframe. Net result: the visitor sees the title + intro
twice, and the chart starts ~400px below the top of the iframe.

Plus: the Streamlit subtitles are stale. The Astro shell uses the canonical strings
from `data/canonical.json` ("How theme connection shift over time" for Inner Life
Currents, etc.). The Streamlit pages still show old strings.

**Fix options** (pick one):

**A) Detect embed mode and skip the title/subtitle/intro inside the Streamlit page.**
Streamlit exposes `st.context.headers` and `st.query_params`. When the page is loaded
with `?embed=true`, suppress the H1 + subtitle + intro:

```python
import streamlit as st

is_embedded = st.query_params.get("embed") == "true"

if not is_embedded:
    render_hero(title="Inner Life Currents", subtitle="...", description="...")
# else: skip the hero, render only the chart
```

This is the cleanest path — Streamlit page stands alone when accessed directly,
strips its hero when embedded.

**B) Strip the hero entirely.** If the Astro shell is now the canonical surface,
the Streamlit pages don't need their own headers. Remove `render_hero(...)` calls
from each page. Trade-off: anyone visiting `mindspaceos.streamlit.app/<page>`
directly sees a chart with no context.

**Recommendation: A** — detect embed mode and skip.

### 3. Streamlit Cloud chrome at the bottom

`?embed=true` hides the Streamlit menu/header/footer but does NOT hide the
"Built with Streamlit 🎈" mark on the bottom-left or the "Fullscreen ↗" button
on the bottom-right. These are baked into the Streamlit Cloud free-tier hosting.

**Fix.** Two paths:
- **Free tier:** can't hide. Live with it, OR upgrade to Streamlit Cloud Teams (paid).
- **Self-host with Streamlit Community Cloud's `client.toolbarMode = "minimal"`** in
  `.streamlit/config.toml`. Doesn't fully hide the Streamlit branding either.

**Recommendation:** accept for v1. Revisit if mindspaceos.com gets enough traffic
to justify the paid tier (~$20/mo).

### 4. Vertical space wasted in the iframe

Inner Life Currents specifically: between the Astro intro, the duplicated
Streamlit hero, the Time Travel filter card, the "119 meditation topics..." callout,
and the chart, the chart begins around y=600px in a 800px iframe — the chart is
mostly below the fold.

**Fix.** Once #1 (hide sidebar) and #2 (suppress hero in embed mode) are applied,
the chart will start much closer to the top of the iframe. The iframe aspect ratio
on the Astro side has also been bumped to a taller `4:5 / 5:4 / 4:3` (mobile/tablet
/desktop) so the chart has more vertical room.

### 5. Filters work, just need clearance

Confirmed working inside the iframe:
- ✓ **Inner Life Currents** Time Travel buttons (← Previous Quarter / Next Quarter →) — clickable, functional.
- ✓ **Community Weather Report** quarter radio + sentiment-derived weather chips — work.
- ✓ **Emotion Pulse** hover-to-discover scatter — works.
- ✓ **Community Dynamics** Sankey hover tooltips — work.

No interactivity is broken. The only filter problem is **vertical clearance** —
once #1 + #2 are fixed, all filters will be visible without scrolling on a 1280×900
viewport.

## After-fix checklist

After deploying the Streamlit changes:

- [ ] Visit `mindspaceos.streamlit.app/Emotion_Pulse?embed=true` directly — sidebar should NOT appear, Streamlit hero should NOT appear, chart should render at top.
- [ ] Same for Community_Dynamics, Community_Weather_Report, Inner_Life_Currents.
- [ ] On `mindspaceos.com/explore/inner-life-currents/`, click "Tap to interact" — Time Travel buttons should be visible without scrolling inside the iframe.
- [ ] Re-run `node scripts/generate-og-placeholders.mjs` and the Playwright screenshot pipeline so the static-screenshot fallbacks reflect the new chrome-free Streamlit pages.

## Order of operations

1. Apply Streamlit changes (#1 mandatory, #2 mandatory, #3 accept) — single PR on `MindSpace-OS` repo, four-line diff.
2. Deploy to Streamlit Cloud (auto-deploys on push to main).
3. Astro shell already has the embed_options + taller aspect ratio (pushed in this branch). No further Astro changes needed once Streamlit is updated.
