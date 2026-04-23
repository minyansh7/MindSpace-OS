# MindSpace OS

> A visual field guide to how people actually talk about meditation.

MindSpace OS is an interactive Streamlit site that turns **2,977 posts from r/meditation** (Jan 2024 – Jun 2025) into six navigable views — emotional maps, sentiment weather, theme networks, and quarterly shifts. Built to see what a practice community sounds like when nobody's selling anything.

**Live site:** [https://mindspaceos.streamlit.app]

---

## What's inside

Six interactive pages, accessible from the sidebar:

| Page | What it shows |
|---|---|
| **Emotion Pulse** | UMAP map where posts cluster by emotional vocabulary (via GoEmotions). Frustration, awe, curiosity each occupy their own region. |
| **Meditation Weather Report** | 18 months of sentiment trends across topics, rendered as weather metaphors (sunny days, storms). |
| **Inner Life Themes** | Sankey diagram — how broad themes branch into specific discussions. |
| **Inner Life Trees** | Filterable co-occurrence trees, time-sliced by quarter, with engagement + sentiment filters. |
| **Inner Life Web** | Static co-occurrence network across the full archive. Capped at 40 nodes by default; toggle shows the full hairball. |
| **Inner Life Currents** | Temporal network view — how theme connections shift quarter by quarter. |

The four network-style pages (Themes, Trees, Web, Currents) form an "Inner Life" metaphor family — each a different angle on how meditation themes connect.

---

## The finding

The dominant emotional register on r/meditation isn't peace. It's **struggle tightly coupled with curiosity**. The community's shared vocabulary is closer to *"trying again"* than *"finding bliss."*

That's not a failure mode — that's what a practice community actually sounds like when nobody's selling anything.

---

## Tech stack

- **App framework**: [Streamlit](https://streamlit.io/) (multipage)
- **Visualization**: [Plotly](https://plotly.com/python/) for interactive charts; custom `components.html` iframes for the network pages
- **Data**: [DuckDB](https://duckdb.org/) (`reddit_progress.duckdb`) + precomputed Parquet aggregates in `precomputed/`
- **NLP**: [GoEmotions](https://github.com/google-research/google-research/tree/master/goemotions) for emotion classification; [UMAP](https://umap-learn.readthedocs.io/) for dimensionality reduction
- **Language**: Python 3.11

---

## Local development

```bash
# Clone
git clone https://github.com/minyansh7/Mindfulness-Space-L0.git
cd Mindfulness-Space-L0

# Create venv (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -r requirements.txt

# Run
streamlit run Homepage.py
```

Open http://localhost:8501. Navigate between pages via the sidebar.

### Docker

A `Dockerfile` is included for containerized deploys. **Note:** the current `CMD` references `app.py` — update to `Homepage.py` before use (or rename the entry point). Streamlit Cloud runs `Homepage.py` directly and does not use the Dockerfile.

---

## Project structure

```
.
├── Homepage.py                    # entry point — landing page with page cards
├── pages/                         # Streamlit multipage auto-discovers these
│   ├── 0_Emotion_Pulse.py
│   ├── 1_Meditation_Weather_Report.py
│   ├── 2_Inner_Life_Themes.py     # Sankey
│   ├── 3_Inner_Life_Web.py        # static co-occurrence network
│   ├── 4_Inner_Life_Currents.py   # temporal network
│   └── 5_Inner_Life_Trees.py      # filterable river-flow trees
├── precomputed/                   # Parquet aggregates (topics, clusters, timeseries)
├── assets/                        # page icons, hero images
├── archive/                       # historical page versions — not rendered
├── reddit_progress.duckdb         # source database
├── CLAUDE.md                      # design-intent notes (naming rationale, color palette, typography conventions)
├── drafts/                        # launch copy + Playwright posting scripts
├── docs/                          # long-form writeups
└── requirements.txt
```

---

## Design intent

See [`CLAUDE.md`](CLAUDE.md) for the editorial layer:

- Why each page is named what it is (and what it used to be called)
- The canonical cluster → color mapping (same seven themes across Inner Life Trees, Currents, Web)
- Typographic conventions (eyebrow labels, page H1s, hover text wrapping)
- Session-state plumbing across time-trend pages

The design pass that produced the current naming family (Inner Life Themes, Trees, Web, Currents) and stripped decorative noise is documented in a long-form retrospective at [`docs/publish_draft.md`](docs/publish_draft.md).

---

## Data

- **Source**: r/meditation public posts & comments, Jan 2024 – Jun 2025
- **Count**: 2,977 posts processed
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
