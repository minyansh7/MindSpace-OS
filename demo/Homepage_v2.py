"""
DEMO — proposed Homepage v2 for MindSpace OS.

This file is intentionally placed OUTSIDE the `pages/` folder so Streamlit's
multi-page auto-discovery does not route it. The live site's `Homepage.py`
is unchanged.

To preview locally:
    cd /Users/minyan/Documents/mindfulness-space-l0
    streamlit run demo/Homepage_v2.py --server.port 8502

Then open http://localhost:8502

Design patterns (from research on Pudding + Our World in Data):
- Numbered vertical feed, not a card grid (Pudding)
- Hero = tagline + stat counters (OWID)
- One-line hook teaser per feature, <= 14 words (Pudding voice)
- Two named sections grouping the 6 features (OWID topic sections)
- "Start here" pointer to reduce cold-start paralysis
- Total prose budget: ~80 words

Live Homepage.py is NOT modified. Swap by renaming this file to Homepage.py
and moving the current one aside when you're ready.
"""
import streamlit as st

st.set_page_config(
    page_title="MindSpace OS — Homepage Demo",
    layout="centered",  # narrow column, Pudding-feed feel
)

# Hide Streamlit's auto-sidebar for the demo
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 780px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Banner to flag this is a demo preview
st.info(
    "🧪 **Demo preview.** This is a proposed `Homepage_v2` — the live "
    "`Homepage.py` is unchanged. Run with `streamlit run demo/Homepage_v2.py`."
)

# --- Hero ---------------------------------------------------------------
st.markdown(
    """
    <div style="padding: 1.5rem 0 0.5rem 0;">
        <h1 style="font-size: 2.75rem; font-weight: 800; margin: 0;
                   letter-spacing: -0.02em; color: #0f172a;">
            MindSpace OS
        </h1>
        <p style="font-size: 1.05rem; color: #475569; margin: 0.9rem 0 0 0;
                  line-height: 1.55; max-width: 38rem;">
            Patterns across thousands of r/meditation posts,
            drawn from January 2024 through June 2025.
        </p>
        <div style="margin-top: 1.25rem; display: flex; gap: 2rem; flex-wrap: wrap;
                    font-size: 12px; color: #64748b; letter-spacing: 0.08em;
                    text-transform: uppercase;">
            <span><strong style="color: #0f172a; font-size: 18px; font-weight: 800;
                   letter-spacing: -0.01em; text-transform: none;
                   margin-right: 6px;">6</strong>charts</span>
            <span><strong style="color: #0f172a; font-size: 18px; font-weight: 800;
                   letter-spacing: -0.01em; text-transform: none;
                   margin-right: 6px;">18</strong>months of data</span>
            <span><strong style="color: #0f172a; font-size: 18px; font-weight: 800;
                   letter-spacing: -0.01em; text-transform: none;
                   margin-right: 6px;">2</strong>lenses</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# --- Start here pointer -------------------------------------------------
st.markdown(
    """
    <p style="font-size: 13px; color: #64748b; margin: 1.25rem 0 0 0;">
        <a href="#01-emotion-pulse" style="color: #6366f1;
           text-decoration: none; font-weight: 600;">
            Start here ↓
        </a>
    </p>
    """,
    unsafe_allow_html=True,
)

# --- Helpers ------------------------------------------------------------
def section_eyebrow(text: str) -> None:
    st.markdown(
        f"""
        <div style="font-size: 12px; color: #64748b; letter-spacing: 0.1em;
                    text-transform: uppercase; margin: 2.5rem 0 -0.25rem 0;
                    font-weight: 700;">
            {text}
        </div>
        """,
        unsafe_allow_html=True,
    )


def feed_item(num: str, title: str, teaser: str, href: str, anchor: str | None = None) -> None:
    anchor_attr = f'id="{anchor}"' if anchor else ""
    st.markdown(
        f"""
        <a href="{href}" style="text-decoration: none; color: inherit;">
          <div {anchor_attr} style="border-top: 1px solid #e2e8f0;
                                     padding: 1.4rem 0; display: flex; gap: 1.5rem;
                                     align-items: baseline; transition: background 0.15s;">
            <div style="font-variant-numeric: tabular-nums; color: #94a3b8;
                        font-size: 13px; font-weight: 700; min-width: 2.5rem;
                        letter-spacing: 0.05em;">#{num}</div>
            <div style="flex: 1;">
                <div style="font-size: 1.25rem; font-weight: 700; color: #0f172a;
                            letter-spacing: -0.01em;">{title}</div>
                <p style="font-size: 0.95rem; color: #475569;
                          margin: 0.35rem 0 0 0; line-height: 1.55;">{teaser}</p>
            </div>
            <div style="color: #cbd5e1; font-size: 18px;">→</div>
          </div>
        </a>
        """,
        unsafe_allow_html=True,
    )


# --- The Mood -----------------------------------------------------------
section_eyebrow("The Mood")

feed_item(
    "01",
    "Emotion Pulse",
    "What does r/meditation feel like? An emotion map, one dot per post.",
    href="/Emotion_Pulse",
    anchor="01-emotion-pulse",
)
feed_item(
    "02",
    "Meditation Weather Report",
    "Sentiment forecasts: which topics get sunny, which storm, quarter by quarter.",
    href="/Meditation_Weather_Report",
)

# --- The Themes ---------------------------------------------------------
section_eyebrow("The Themes")

feed_item(
    "03",
    "Theme Pathways",
    "Themes flow into topics. Trace what leads where.",
    href="/Theme_Pathways",
)
feed_item(
    "04",
    "Theme Web",
    "Which topics keep showing up together? A connection map of the archive.",
    href="/Theme_Web",
)
feed_item(
    "05",
    "Theme Currents",
    "How the conversation drifts. Watch theme connections shift quarter by quarter.",
    href="/Theme_Currents",
)
feed_item(
    "06",
    "Narrative Trees",
    "A river of meditation stories with filters to dig into any branch.",
    href="/Narrative_Trees",
)

# --- Footer -------------------------------------------------------------
st.markdown(
    """
    <div style="border-top: 1px solid #e2e8f0; padding: 2.5rem 0 0.5rem 0;
                text-align: center; font-size: 12px; color: #94a3b8;
                letter-spacing: 0.05em;">
        Powered by Terramare ᛘ𓇳 · Demo preview
    </div>
    """,
    unsafe_allow_html=True,
)
