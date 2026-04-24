import pathlib

import streamlit as st
import plotly.io as pio

from shared_ui import inject_inner_life_css, render_hero

# --- Custom Font ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans&display=swap');
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .footer-text {
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        color: #666;
        margin-top: 2rem;
        padding: 1rem;
        border-top: 1px solid #eee;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        background-color: #667eea;
    }
    @supports not (-webkit-background-clip: text) {
        .footer-text {
            color: #667eea !important;
            background: none !important;
        }
    }
    .js-plotly-plot .sankey-node text {
        text-shadow: none !important;
    }
    .column-eyebrows {
        display: flex;
        justify-content: space-between;
        padding: 8px 10px 4px 10px;
        font-size: 13px;
        line-height: 1.5;
        color: #64748b;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(
    page_title="Community Dynamics — Emotional Flow: From Poster to Commenter",
    layout="wide",
)

# --- Load precomputed figure ---
# Deterministic from precomputed/emotion_clusters.parquet; pre-serialized at
# build time in ``scripts/build_precomputed.py`` so cold start is just a JSON
# parse (~5 KB file, 5 nodes per side). See CLAUDE.md "perf tier-3".
_FIG_PATH = pathlib.Path("precomputed/figures/community_dynamics_sankey.json")


@st.cache_resource(show_spinner=False)
def load_sankey_figure():
    return pio.from_json(_FIG_PATH.read_text())


# --- Main Function ---
def run():
    inject_inner_life_css()
    render_hero(
        eyebrow="COMMUNITY",
        title="Community Dynamics",
        subtitle="Emotional Flow: From Poster to Commenter",
        description="Hover over to see how emotional tones travel between posters and repliers.",
    )

    fig = load_sankey_figure()

    st.markdown(
        '<div class="column-eyebrows"><span>POSTER</span><span>COMMENTER</span></div>',
        unsafe_allow_html=True,
    )

    sankey_config = {
        'displayModeBar': False,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'community_dynamics_sankey',
            'height': 900,
            'width': 1400,
            'scale': 2
        }
    }

    st.plotly_chart(fig, use_container_width=True, config=sankey_config)

    st.markdown("""
    <div class="footer-text">
        Powered By MinyanLabs ©2026
    </div>
    """, unsafe_allow_html=True)

# --- Run App ---
run()
