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
    </style>
""", unsafe_allow_html=True)

# --- Page Config ---
st.set_page_config(
    page_title="Inner Life Themes — Topic Flow: How Themes Connect",
    layout="wide",
)

# --- Load precomputed figure ---
# The Sankey is deterministic from precomputed/main_topics.parquet and takes
# no runtime inputs, so we pre-serialize the whole figure at build time in
# ``scripts/build_precomputed.py`` and just parse the JSON here. This
# skips ~140 lines of Python (groupby, palette assignment, hover-text
# formatting) that used to run on every cold start.
_FIG_PATH = pathlib.Path("precomputed/figures/themes_sankey.json")


@st.cache_resource(show_spinner=False)
def load_sankey_figure():
    return pio.from_json(_FIG_PATH.read_text())


# --- Main Function ---
def run():
    inject_inner_life_css()
    render_hero(
        eyebrow="THEMES",
        title="Inner Life Themes",
        subtitle="Topic Flow: How Themes Connect",
        description="Hover over to discover theme details.",
    )

    fig = load_sankey_figure()
    
    sankey_config = {
        'displayModeBar': False,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'main_topics_sankey_flow',
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