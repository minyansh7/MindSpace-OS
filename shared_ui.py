"""Shared Streamlit UI helpers for MindSpace OS pages.

Kept at the repo root so every page can ``import shared_ui`` without needing
relative-import gymnastics under Streamlit's multipage model.

Typographic and color contracts (see ``CLAUDE.md``):

- Hero h1: 4.75rem / 800 weight / #0f172a (navy); see ``render_hero``.
- Hero eyebrow: 13px / #64748b / 0.18em / uppercase.
- Hero subtitle (h3): 1.75rem / 700 / #0f172a.
- Hero description (p): 1.15rem / #64748b / max-width 780px.
- The @media (max-width: 1200px) breakpoint is the minimum supported size;
  do not reintroduce smaller mobile breakpoints here.
"""
import streamlit as st

# Pinned Plotly.js CDN URL for the ``components.html`` iframes (Emotion
# Pulse UMAP, Inner Life Currents network). Pinned (not ``-latest``) so
# the browser can cache the asset across site deploys and across page
# navigation — ``-latest`` cache-busts whenever the CDN updates.
#
# Version 2.35.2 is the plotly.js that ships with the Python plotly 5.24
# series and is compatible back to plotly>=5.16 (our requirements.txt
# lower bound). The iframes only call stable APIs (newPlot, react,
# restyle, relayout) so minor version drift here is safe.
PLOTLY_CDN_URL = "https://cdn.plot.ly/plotly-2.35.2.min.js"


# CSS shared by the "Inner Life" family (Web, Currents, and any page using
# .main-title / .sub-title / .description / .footer-text / .plot-container).
# Gradient footer degrades to a solid #667eea where -webkit-background-clip
# is unsupported (Firefox/older Safari).
_INNER_LIFE_CSS = """
<style>
.main .block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
    max-width: none;
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
}
@supports not (-webkit-background-clip: text) {
    .footer-text {
        color: #667eea !important;
        background: none !important;
    }
}

.plot-container {
    width: 100%;
    margin: auto;
    position: relative;
}

.hero {
    text-align: center;
    max-width: 960px;
    margin: 0 auto;
    padding: 2.5rem 1rem 1.75rem 1rem;
}

.hero-eyebrow {
    font-size: 13px;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    margin-bottom: 1.25rem;
}

.hero-title {
    font-size: 4.75rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.05;
    letter-spacing: -0.02em;
    margin: 0 0 1.25rem 0;
}

.hero-subtitle {
    font-size: 1.75rem;
    font-weight: 700;
    color: #0f172a;
    line-height: 1.3;
    margin: 0 0 1.25rem 0;
}

.hero-description {
    font-size: 1.15rem;
    color: #64748b;
    line-height: 1.6;
    max-width: 780px;
    margin: 0 auto;
}

@media (max-width: 1200px) {
    .hero-title { font-size: 3.75rem; }
    .hero-subtitle { font-size: 1.5rem; }
}

/* Legacy aliases so pages that still reference main-title/sub-title/description
   pick up the new hero typography without touching the HTML. */
.main-title { font-size: 4.75rem; font-weight: 800; color: #0f172a; letter-spacing: -0.02em; line-height: 1.05; margin: 0 0 1.25rem 0; }
.sub-title { font-size: 1.75rem; font-weight: 700; color: #0f172a; margin: 0 0 1.25rem 0; }
.description { font-size: 1.15rem; color: #64748b; line-height: 1.6; max-width: 780px; margin: 0 auto; }

.annotation-container {
    text-align: left;
    margin: 0.5rem 0 1rem 0;
    padding: 0 200px;
}

@media (max-width: 1200px) {
    .annotation-container {
        padding: 0 100px;
    }
}
</style>
"""

_FOOTER_HTML = """
<div class="footer-text">
    Powered By MinyanLabs ©2026
</div>
"""


def inject_inner_life_css() -> None:
    """Inject the shared Inner Life CSS block (title/footer/plot-container)."""
    st.markdown(_INNER_LIFE_CSS, unsafe_allow_html=True)


def render_hero(eyebrow: str, title: str, subtitle: str, description: str) -> None:
    """Render the canonical MindSpace OS page hero (eyebrow / h1 / h3 / p).

    All pages share this block so the site reads as one visual language. The
    eyebrow is uppercased and letter-spaced, the h1 is an oversized navy
    display type, and the description is slate-grey at a comfortable max-width.
    ``inject_inner_life_css()`` must be called on the same page first.
    """
    st.markdown(
        f"""
<div class="hero">
    <div class="hero-eyebrow">{eyebrow}</div>
    <h1 class="hero-title">{title}</h1>
    <h3 class="hero-subtitle">{subtitle}</h3>
    <p class="hero-description">{description}</p>
</div>
""",
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    """Render the standard MinyanLabs gradient footer."""
    st.markdown(_FOOTER_HTML, unsafe_allow_html=True)
