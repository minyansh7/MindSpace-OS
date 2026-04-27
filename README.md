# MindSpace OS

> A visual field guide to how people actually talk about meditation.

MindSpace OS turns **2,899 posts and comments from meditation on Reddit** (Jan 2024 – Jun 2025) into a navigable field guide — emotional maps, sentiment weather, theme networks, and quarterly shifts. Built to see what a practice community sounds like when nobody's selling anything.

**Live site:** [https://mindspace-os.pages.dev](https://mindspace-os.pages.dev) (canonical domain `mindspaceos.com` once DNS lands).

The project ships as two sibling surfaces from one repo:

- **Editorial site** (`site/`) — Astro static build, the public reading experience. Hosted on Cloudflare Pages. **All four interactive chart pages are baked into self-contained static HTML at build time**, so the editorial site has zero runtime dependency on Streamlit (no cold-start, no hibernation, ~1.5s first load).
- **Streamlit app** (`Homepage.py` + `pages/`) — the source of truth for chart logic (Plotly figures, custom JS visualizations, data wiring). The static `site/public/charts/*.html` embeds are regenerated from this code by `scripts/build_chart_figures.py`. The Streamlit app at [mindspaceos.streamlit.app](https://mindspaceos.streamlit.app) still works for direct-link visitors and as a development surface, but the editorial site no longer iframes it.

---

## What's inside

Four interactive pages, accessible from the sidebar:

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

### Production (everything the live site depends on at runtime)

- **[Astro 6](https://astro.build)** — static-site framework. `output: 'static'`, every page rendered to plain HTML at build time. Component model + content collections power the editorial pages; `getStaticPaths` generates the four `/explore/*` routes from `data/canonical.json`.
- **[Tailwind CSS 4](https://tailwindcss.com)** (via `@tailwindcss/vite`) — utility-first styling, theme tokens declared in `@theme` blocks rather than a separate config file. Time-of-day gradient theming + ripple-on-hover animations ported from the original meditation-circle design language.
- **[@fontsource/*](https://fontsource.org/)** — self-hosted webfonts: **Inter** (UI + display), **Source Serif 4** (editorial body + pull-quotes), **JetBrains Mono** (eyebrows + brand mark). Imported in the layout so they're inlined and don't pop in.
- **[@astrojs/sitemap](https://docs.astro.build/en/guides/integrations-guide/sitemap/)** — generates `sitemap-index.xml` + per-section sitemaps at build.
- **[@astrojs/cloudflare](https://docs.astro.build/en/guides/integrations-guide/cloudflare/)** — Cloudflare Pages adapter (declared in deps; ready to flip from `static` → `server` when dynamic OG cards land).
- **[Plotly.js](https://plotly.com/javascript/)** — loaded from CDN (`cdn.plot.ly/plotly-2.35.2.min.js`) by the four static chart HTMLs. Cached across pages after first load. Powers Emotion Pulse (UMAP scatter + radar overlay), Community Dynamics (Sankey), and Inner Life Currents (force-directed temporal network). Community Weather Report uses pure CSS animations + a hand-rolled Cardinal-spline sparkline; no Plotly.
- **[Cloudflare Pages](https://pages.cloudflare.com/)** — static hosting. Project `mindspace-os`. Connected to GitHub for build-on-push.

### Build (runs locally + in CI; not served at runtime)

- **[Bun](https://bun.sh) + `bun:test`** — JS test runner for build-output assertions (route presence, OG meta, canonical-data sync, no-Streamlit-leak guard, static chart self-containment, no-inline-`ARCHETYPE_COLORS`-in-Python). 54 tests across `site/tests/`.
- **Python 3.11** + **[pandas](https://pandas.pydata.org/)** + **[numpy](https://numpy.org/)** + **[pyarrow](https://arrow.apache.org/)** — drive `scripts/build_chart_figures.py` which bakes the four static chart HTMLs (Plotly trace construction, hover-text formatting, weather-region positioning, all 6 quarters of temporal-network payloads inlined into one file).
- **[Plotly](https://plotly.com/python/) (Python)** — only used at build time, to construct trace JSON consumed by the static HTMLs. No Plotly Python in production.
- **[DuckDB](https://duckdb.org/)** + Parquet aggregates in `precomputed/` — the data layer feeding the chart bake.

### Source of truth (development surface, not in production path)

- **[Streamlit](https://streamlit.io/)** + **Plotly** — `Homepage.py` + `pages/*.py` are the canonical home for chart logic (figure construction, hover templates, custom JS visualizations). Hosted at [mindspaceos.streamlit.app](https://mindspaceos.streamlit.app) for direct-link visitors and as a development surface. **The editorial site does not iframe Streamlit at runtime** — `scripts/build_chart_figures.py` re-implements the Plotly/HTML output and writes self-contained files into `site/public/charts/`. When chart logic changes in `pages/*.py`, the build script needs the same change applied (it deliberately doesn't `import` from the Streamlit modules to avoid `st.set_page_config` side effects).

### NLP / data analysis (one-time pipeline, outputs land in `precomputed/`)

- **[GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions)** — Google Research's 27-emotion classifier; ran over the r/meditation corpus to produce per-post emotion scores.
- **[UMAP](https://umap-learn.readthedocs.io/)** — dimensionality reduction on the GoEmotions embeddings → the `umap_x` / `umap_y` columns Emotion Pulse plots.
- **[Gaussian Mixture Model](https://scikit-learn.org/stable/modules/mixture.html)** — clustered the UMAP embedding into the 5 emotional archetypes.

### Languages

- **TypeScript / Astro** — the editorial site (`site/`).
- **Python 3.11** — chart-bake script + Streamlit app + data pipeline.
- **CSS / HTML** — hand-tuned for the four chart HTMLs (CSS keyframe animations, flex layouts, custom Cardinal-spline sparkline).

---

## Quick start

### Streamlit app

```bash
git clone https://github.com/minyansh7/MindSpace-OS.git
cd MindSpace-OS

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

streamlit run Homepage.py
```

Streamlit will print the local URL and open it in your browser. Navigate between pages via the sidebar.

### Editorial site (Astro)

```bash
cd site
npm install
npm run dev      # local dev server with HMR
npm run build    # static build into site/dist/
npm run preview  # serve the prod build locally
```

The Astro build is what ships to Cloudflare Pages. The four static chart embeds it serves are baked by `python3 scripts/build_chart_figures.py` and live under `site/public/charts/*.html` — re-run that script whenever the chart palette, layout, or data changes.

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
│   ├── tests/                     # bun:test build + canonical-data assertions
│   └── astro.config.mjs
├── data/canonical.json            # single source of truth — archetypes, post counts, page metadata, essays. Read by both Streamlit (Python) and Astro (TS).
├── scripts/
│   ├── _canonical.py              # shared loader: ARCHETYPE_COLORS / TOPIC_MAPPING from canonical.json
│   ├── build_chart_figures.py     # bakes site/public/charts/*.html embeds
│   └── build_precomputed.py       # generates precomputed/ Parquet aggregates
├── precomputed/                   # Parquet aggregates (topics, clusters, timeseries)
├── assets/                        # Streamlit page icons, hero images
├── archive/                       # historical page versions — not rendered
├── CLAUDE.md                      # design-intent notes (naming, color palette, typography, deploy)
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
- **Storage**: Parquet aggregates under `precomputed/` for app runtime

Raw Reddit data is **not redistributed**. The `precomputed/*.parquet` files contain the processed analytical output used by the app.

---

## Credits

- Built by **Minyan Shi** at [MinyanLabs](https://open.substack.com/pub/minyansh)
- Emotion classification based on Google Research's [GoEmotions](https://arxiv.org/abs/2005.00547) taxonomy
- Data sourced from [Reddit](https://reddit.com/) community posts

---

## License

Source available for personal / educational exploration. Please reach out before commercial use or redistribution of the analytical outputs.

© 2026 MinyanLabs
