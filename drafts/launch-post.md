# MindSpace OS — Launch Drafts

Launch copy for Substack + X/Twitter. Title and narrative from the 2026-04-21 UX session.

---

## Substack Post

**Publish URL:** https://minyansh.substack.com/publish/post?type=newsletter

### Title
Pathways, Trees, Web, Currents: Renaming a Data Site Until It Read Like One Voice

### Subtitle
A thirteen-hour pass that renamed every page, stripped decorative noise, and shipped mobile without touching a single desktop pixel.

### Body

I spent a long Saturday with MindSpace OS — the Streamlit site that visualizes emotional and topical patterns across r/meditation discussions from January 2024 to June 2025. Nothing about the underlying analysis changed. What changed was the *shape* of the reading experience: how pages are named, how titles behave, how a reader's eye lands on a chart the first time. By the end I had twenty-six commits and a site that reads more like one piece of writing than six.

Here is what the session actually did.

**A family of names**

The sidebar used to read like a machine log: "Cocurrence Mapping," "Cocurrence Mapping Over Time," "Cocurrence Mapping complex," "Main Topics Sankey." Four of the six pages were really four views of the same idea — how meditation themes connect — but the names admitted no kinship. I renamed them as a family of natural forms:

- Theme Pathways (Sankey — was *Main Topics Sankey*)
- Narrative Trees (detailed river flow — was *Cocurrence Mapping complex*)
- Theme Web (static co-occurrence network — was *Cocurrence Mapping*)
- Theme Currents (temporal network — was *Cocurrence Mapping Over Time*)

Pathways, trees, web, currents. Each is a tangible shape in the physical world, and the set reads as one metaphor family rather than four disconnected files. I also reordered the sidebar so the three network views move from most-structured (Trees) to most-temporal (Currents), which now ships last.

**One H1, one subtitle, one grey description**

Every page had been improvising its header. Some had poetic subtitles ("Where Narratives Collide"), some had none, some stacked three headings on top of the chart. I converged on a single pattern: one H1 at 3rem / 800, one h3 subtitle underneath, one grey descriptive line below that. Nothing else above the fold.

The most interesting call was on Narrative Trees. The old subtitle was "Living Narrative Intelligence Platform," which competed with the H1 for the same semantic space. I dropped the prose subtitle and replaced it with an eyebrow — QUARTER 2025Q2, in 13px / #64748b uppercase — matching the "TIME TRAVEL" eyebrow above the slider. Subtitles should earn their line; a functional state label earns it better than a tagline.

Borkin et al. (2013) on what people recall from charts pushed me toward descriptive H1s, but the work of applying that to a six-page site showed me their limit: when every page's H1 is a declarative finding, the sidebar stops being an anchor. So the site keeps brand H1s ("Emotion Pulse," "Theme Web") and leaves the declarative work to the subtitle line.

**Static decluttering, charts at rest**

Following Tufte's data-ink ratio and Knaflic's preattentive-focus arguments, I did a round of purely static changes — nothing that touched animation timing or motion paths:

- Hid UMAP axis ticks on Emotion Pulse (the coordinates are arbitrary; they were noise).
- Capped Theme Web at forty nodes by default with an opt-out toggle; first paint is always the simplified view.
- Labelled only the top-ten nodes on Theme Currents; the rest appear on hover.
- Dropped the Plotly modebar across the narrative charts. It was chartjunk on a scrolltelling page.
- Stripped decorative emojis from tooltips, timeline headers, and the Cocurrence Complex sidebar — about thirteen emojis from the Sankey alone.

I also replaced a fragile 150-line hand-rolled "button-dot slider" (held together with !important CSS) with a single native st.select_slider. The filters on Narrative Trees that used to be decorative HTML divs are now a real st.slider and st.radio that actually filter df_edges. A reader who moves a knob should see the chart move.

**Mobile, without touching desktop**

The hard constraint I set for myself was: desktop visuals and animations must not change. Every mobile fix had to be gated behind a check that desktop never triggers.

The approach is small. A mobile.py helper reads st.context.headers["User-Agent"] and regex-matches Mobi|Android|iPhone|iPad. Plotly pages branch the render call: on mobile they disable the modebar, bump hoverlabel font size, and tighten margins. For the four components.html iframes, I inject @media (max-width: 768px) CSS blocks inside the iframe HTML. Desktop never matches the query, so its rendering is bit-identical. Mobile gets legible type, wider touch targets, and tooltips that don't spill off-screen (pre-wrapped to 75 characters, since Plotly does not auto-wrap).

Shipping it layer by layer — helper, then Plotly pages, then iframes — meant each commit was independently revertible. That mattered when I was working alone at 1 a.m.

**Closing**

The commits tell a small story: a site that used to feel like six experiments now feels like one. Nothing radical, no redesign. Mostly the work of naming, of deciding what deserves a line of text above a chart, and of keeping the mobile path from leaking into the desktop path. If you want to read the design-intent notes — which pages were renamed from what, which subtitle was cut and why — the CLAUDE.md in the repo documents every editorial call.

---

Explore the live site: https://mindfulness-space-x.streamlit.app
Design-intent notes: github.com/minyansh7/mindfulness-space-l0/blob/main/CLAUDE.md
Newsletter: https://open.substack.com/pub/minyansh

— Min · MinyanLabs © 2026

---

## Twitter / X Posts

**Compose URL:** https://x.com/compose/post

### Option A — Distilled highlight

```
13-hour UX pass on MindSpace OS: 26 commits, zero desktop pixels changed on mobile.

Renamed 4 pages into one metaphor family. Killed 150 lines of !important CSS.

Data storytelling that reads like one voice, not six experiments.

→ [link]
```

### Option B — Quiet

```
Quiet UX pass on MindSpace OS. Nothing radical, no redesign.

Mostly naming, typography, and a mobile path that never touches desktop.

Read the 13-hour story: [link]
```

### Option C — Thread opener

```
Spent 13 hours this weekend on a quiet UX pass across MindSpace OS — a Streamlit site on r/meditation discussions. 26 commits. No redesign.

Mostly: naming, typography, and a mobile path that never touches desktop.

Notes 🧵
```

**Follow-up tweets for the thread (if using C):**

```
Before: Cocurrence Mapping. Cocurrence Mapping Over Time. Cocurrence Mapping complex. Main Topics Sankey.

After: Theme Pathways. Narrative Trees. Theme Web. Theme Currents.

Same four pages. One metaphor family — natural forms you can point to.
```

```
Removed a subtitle I liked: "Living Narrative Intelligence Platform."

It was competing with the H1 for meaning.

Replaced with a functional eyebrow — QUARTER 2025Q2 — matching the TIME TRAVEL eyebrow above the slider. Subtitles earn their line or they go.
```

```
Killed a 150-line hand-rolled "button-dot slider" held together by !important CSS. Replaced with one native st.select_slider.

Turned Narrative Trees filters from decorative HTML divs into a real st.slider + st.radio that actually filter df_edges.
```

```
Mobile without breaking desktop: mobile.py reads User-Agent. Plotly pages branch render calls.

The four components.html iframes get @media (max-width: 768px) CSS injected inline. Desktop never matches the query, so rendering is bit-identical.
```

```
On descriptive H1s: Borkin et al. argue for declarative titles (people recall them).

But apply that to a six-page site and the sidebar stops being an anchor. Kept brand H1s; let the subtitle carry the finding.

H1 stability is a site-level concern, not a chart concern.
```

```
Full writeup — what got renamed, what got cut, the mobile rollout, and why Theme Web now caps at 40 nodes by default: [link]

Replies open for questions.
```
