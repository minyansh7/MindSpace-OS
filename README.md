# MindSpace OS

> A visual field guide to how people actually talk about meditation.

MindSpace OS turns **2,899 posts and comments from r/meditation** (Jan 2024 – Jun 2025) into a navigable field guide — emotional maps, sentiment weather, theme networks, and quarterly shifts. Built to see what a practice community sounds like when nobody's selling anything.

The project ships as two sibling surfaces from one repo:

- **Editorial site** (`site/`) — Astro static build, the public reading experience. Hosted on Cloudflare Pages: [https://mindspace-os.pages.dev](https://mindspace-os.pages.dev) (canonical domain `mindspaceos.com` once DNS lands).
- **Interactive Streamlit app** (`Homepage.py` + `pages/`) — the live charts the editorial site embeds and links into. Hosted on Streamlit Cloud: [https://mindspaceos.streamlit.app](https://mindspaceos.streamlit.app).

---

## What's inside

FOr interactive pages, accessible from the sidebar:

| Page | What it shows |
|---|---|
| **Emotion Pulse** | UMAP map where posts cluster by emotional vocabulary (via GoEmotions). Frustration, awe, curiosity each occupy their own region. |
| **Community Dynamics** | Sankey diagram — poster emotional archetype flowing into commenter emotional archetype. |
| **Community Weather Report** | 18 months of sentiment trends across topics, rendered as weather metaphors (sunny days, storms). |
| **Inner Life Currents** | Temporal network view — how theme connections shift quarter by quarter. |

Community Dynamics and Community Weather Report together show *who meets whom* and *how the mood shifts over time* — the two "Community" pages. Inner Life Currents complements them with a temporal network of theme co-occurrences.

---

## The finding

The dominant emotional register on r/meditation isn't peace. It's **struggle tightly coupled with curiosity**. The community's shared vocabulary is closer to *"trying again"* than *"finding bliss."*

That's what a practice community actually sounds like.

---

## Tech stack

- **Editorial site** (`site/`): [Astro](https://astro.build) static build with Tailwind, `@astrojs/sitemap`. Hosted on Cloudflare Pages (project `mindspace-os`). Imports the canonical archetype + post-count data from `data/canonical.json` so Python and TS read from one source of truth.
- **Streamlit app** (`Homepage.py` + `pages/`): multipage Streamlit, [Plotly](https://plotly.com/python/) for interactive charts, custom `components.html` iframes for the network pages.
- **Static chart bake** (`scripts/build_chart_figures.py`): regenerates the standalone `site/public/charts/*.html` embeds the Astro site iframes when the live Streamlit app is unreachable.
- **Data**: [DuckDB](https://duckdb.org/) (`reddit_progress.duckdb`) + precomputed Parquet aggregates in `precomputed/`.
- **NLP**: [GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions) for emotion classification; [UMAP](https://umap-learn.readthedocs.io/) for dimensionality reduction.
- **Language**: Python 3.11 (Streamlit + data pipeline), TypeScript / Astro (editorial site).

---

### Editorial site (Astro)

```bash
cd site
npm install
npm run dev      # http://localhost:4321 with HMR
npm run build    # static build into site/dist/
npm run preview  # serve the prod build at http://localhost:4321
```

The Astro build is what ships to Cloudflare Pages. The static chart embeds it iframes are baked by `python3 scripts/build_chart_figures.py` and live under `site/public/charts/*.html`.

### Docker

A `Dockerfile` is included for containerized deploys of the Streamlit app. **Note:** the current `CMD` references `app.py` — update to `Homepage.py` before use (or rename the entry point). Streamlit Cloud runs `Homepage.py` directly and does not use the Dockerfile.

---

## Project structure

```
.
├── Homepage.py                    # Streamlit entry point
├── pages/                         # Streamlit multipage auto-discovers these
│   ├── 0_Emotion_Pulse.py
│   ├── 1_Community_Dynamics.py    # Poster → Commenter Sankey
│   ├── 2_Community_Weather_Report.py
│   └── 3_Inner_Life_Currents.py   # temporal network
├── site/                          # Astro editorial site (Cloudflare Pages)
│   ├── src/                       # pages, components, layouts, lib
│   ├── public/                    # static assets, OG cards, baked chart embeds
│   ├── tests/                     # vitest build + canonical-data assertions
│   └── astro.config.mjs
├── data/canonical.json            # single source of truth — archetypes, post counts, page metadata, essays. Read by both Streamlit (Python) and Astro (TS).
├── scripts/
│   ├── build_chart_figures.py     # bakes site/public/charts/*.html embeds
│   └── build_precomputed.py       # generates precomputed/ Parquet aggregates
├── precomputed/                   # Parquet aggregates (topics, clusters, timeseries)
├── assets/                        # Streamlit page icons, hero images
├── archive/                       # historical page versions — not rendered
├── reddit_progress.duckdb         # source database
├── CLAUDE.md                      # design-intent notes (naming, color palette, typography, deploy)
├── drafts/                        # launch copy + Playwright posting scripts
├── docs/                          # long-form writeups
└── requirements.txt
```

---

## Design intent

See [`CLAUDE.md`](CLAUDE.md) for the editorial layer:

- Why each page is named what it is (and what it used to be called)
- The canonical cluster → color mapping (same seven themes across Inner Life Currents and Web)
- Typographic conventions (eyebrow labels, page H1s, hover text wrapping)
- Session-state plumbing across time-trend pages

The design pass that produced the current naming family and stripped decorative noise is documented in a long-form retrospective at [`docs/publish_draft.md`](docs/publish_draft.md).

---

## Data

- **Source**: r/meditation public posts & comments, Jan 2024 – Jun 2025
- **Count**: 2,899 posts and comments (canonical, post response-pattern filter). 2,977 pre-filter, documented in `data/canonical.json` for reproducibility.
- **Processing**: emotion classification → UMAP clustering → theme grouping → temporal binning by quarter
- **Storage**: DuckDB for raw, Parquet aggregates for app runtime

Raw Reddit data is **not redistributed**. The `reddit_progress.duckdb` file contains the processed analytical output used by the app.

---

## Credits

- Built by **Min** at [MinyanLabs](https://open.substack.com/pub/minyansh)
- Emotion classification based on Google Research's [GoEmotions](https://arxiv.org/abs/2005.00547) taxonomy
- Data sourced from [r/meditation](https://reddit.com/r/meditation) community posts

---

## License

Source available for personal / educational exploration. Please reach out before commercial use or redistribution of the analytical outputs.

© 2026 MinyanLabs
