import json

import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

from shared_ui import PLOTLY_CDN_URL, inject_inner_life_css, render_hero

st.set_page_config(
    page_title="Emotion Pulse",
    layout="wide"
)

# GoEmotions columns the per-point radar plots. Kept in the order the radar
# θ axis walks them so Python->JS payload is ready to plot without reshuffling.
USER_RADAR_EMOTIONS = [
    "gratitude", "joy", "caring", "love",
    "confusion", "fear", "sadness", "grief",
]
# Display labels for those same 8 axes (emoji + name). Index-aligned.
RADAR_THETA_LABELS = [
    "🙏 Gratitude", "😊 Joy", "🤗 Caring", "❤️ Love",
    "😕 Confusion", "😨 Fear", "😢 Sadness", "💔 Grief",
]

ARCHETYPE_COLORS = {
    "Reflective Caring": "#ff5e78",
    "Soothing Empathy": "#00c49a",
    "Tender Uncertainty": "#6a5acd",
    "Melancholic Confusion": "#9a32cd",
    "Anxious Concern": "#ffc300",
}
ARCHETYPE_SYMBOLS = {
    "Reflective Caring": ("circle", 8),
    "Soothing Empathy": ("diamond", 8),
    "Tender Uncertainty": ("triangle-nw", 9),
    "Melancholic Confusion": ("star-square", 8),
    "Anxious Concern": ("star-triangle-up", 8),
}
# Centroid label offsets (x, y) in UMAP data units. Soothing Empathy pulled
# down slightly (was 4.0) to clear the top-right radar inset.
CENTROID_OFFSETS = {
    "Reflective Caring": (3.9, 1.2),
    "Soothing Empathy": (1.5, 3.4),
    "Tender Uncertainty": (-4.1, -2.5),
    "Melancholic Confusion": (0.5, -1.5),
    "Anxious Concern": (2.4, -0.3),
}


def _ideal_text_color(bg_hex: str) -> str:
    bg_hex = bg_hex.lstrip("#")
    r, g, b = (int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "black" if luminance > 186 else "white"


@st.cache_data(show_spinner=False)
def _build_plot_payload():
    """Turn the slim parquet into the JSON payload the iframe renders.

    Split each archetype's points into an in-range / out-of-range pair so
    only the central 95% of the x-axis carries Plotly hover — matches the
    behaviour the page shipped before the iframe migration.
    """
    df = pd.read_parquet("precomputed/emotion_clusters_slim.parquet")

    x_min, x_max = float(df["umap_x"].min()), float(df["umap_x"].max())
    x_center = (x_min + x_max) / 2
    hover_half = 0.95 * (x_max - x_min) / 2
    in_range = df["umap_x"].between(x_center - hover_half, x_center + hover_half)

    traces = []
    for archetype, color in ARCHETYPE_COLORS.items():
        symbol, size = ARCHETYPE_SYMBOLS[archetype]
        text_color = _ideal_text_color(color)
        bg_color = f"rgba({int(color[1:3],16)},{int(color[3:5],16)},{int(color[5:7],16)},0.9)"

        mask = df["archetype_label"] == archetype
        for mask_subset, hoverinfo in ((mask & in_range, "text"), (mask & ~in_range, "skip")):
            sub = df[mask_subset]
            if sub.empty:
                continue
            traces.append({
                "x": sub["umap_x"].tolist(),
                "y": sub["umap_y"].tolist(),
                "mode": "markers",
                "name": archetype,
                "marker": {
                    "color": color, "opacity": 0.7, "symbol": symbol, "size": size,
                },
                "text": sub["hover_text"].tolist() if hoverinfo == "text" else None,
                "customdata": sub[USER_RADAR_EMOTIONS].values.tolist(),
                "hoverinfo": hoverinfo,
                "hovertemplate": "%{text}<extra></extra>" if hoverinfo == "text" else None,
                "hoverlabel": {
                    "bgcolor": bg_color,
                    "font": {"color": text_color, "size": 12, "family": "Arial, sans-serif"},
                    "align": "left",
                    "bordercolor": "rgba(0,0,0,0.2)",
                    "namelength": -1,
                } if hoverinfo == "text" else None,
                "showlegend": False,
            })

    # Centroid labels (no customdata — keep the hover handler from firing on them)
    centroids = df.groupby("archetype_label")[["umap_x", "umap_y"]].mean()
    for archetype, (cx, cy) in centroids.iterrows():
        dx, dy = CENTROID_OFFSETS.get(archetype, (0, 0))
        traces.append({
            "x": [cx + dx], "y": [cy + dy],
            "mode": "text",
            "text": [f"<b>{archetype}</b>"],
            "textfont": {
                "size": 20,
                "color": ARCHETYPE_COLORS[archetype],
                "family": "sans-serif",
            },
            "hoverinfo": "skip",
            "showlegend": False,
        })

    y_min, y_max = float(df["umap_y"].min()), float(df["umap_y"].max())
    y_range_pad_top = 0.13 * (y_max - y_min)
    y_range_pad_bot = 0.01 * (y_max - y_min)

    return {
        "traces": traces,
        "y_range": [y_min - y_range_pad_bot, y_max + y_range_pad_top],
        "archetype_colors": ARCHETYPE_COLORS,
        "theta_labels": RADAR_THETA_LABELS,
    }


def run():
    inject_inner_life_css()
    render_hero(
        eyebrow="PULSE",
        title="Emotion Pulse",
        subtitle="2,977 meditation posts, each colored by its dominant emotion",
        description="This emotional map reveals how people express their emotions through meditation practices, drawn from 2,977 Reddit posts and comments shared between January 2024 and June 2025.",
    )

    st.markdown("""
    <div class="info-section" style="text-align: left; padding: 0.5rem 1rem;">
        <p style="font-size: 1rem; margin: 0; color: #444; max-width: 1400px; width: 95%; line-height: 1.5;">
            Conducted advanced NLP processing using <strong>Google Research's <a href="https://research.google/blog/goemotions-a-dataset-for-fine-grained-emotion-classification/" target="_blank" style="color: #4285f4; text-decoration: none; border-bottom: 1px dotted #4285f4;">GoEmotions</a> Model</strong> with 27-category emotion classification system and the Fine-grained model trained on 58,000 human-annotated texts, to decode emotional contexts among Reddit's post and comments on Meditation.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="annotation-container">
        <div style="display: flex; justify-content: center;">
            <div style="max-width: 600px; text-align: center;">
                <p style="font-size: 16px; color: #718096; margin: 0; line-height: 1.8; font-weight: 300; opacity: 0.9;">
                    <strong>Each point</strong> marks a message shared on Reddit about meditation.<br>
                    <strong>Color</strong> reflects the dominant emotion underneath each message.<br>
                    <strong>Hover</strong> to discover.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    payload = _build_plot_payload()

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="{PLOTLY_CDN_URL}"></script>
        <style>
            body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background: white; }}
            .plot-wrap {{
                position: relative;
                width: 100%;
                height: 1080px;
            }}
            #umap-plot {{ width: 100%; height: 100%; }}
            #radar-wrap {{
                position: absolute;
                top: 10px;
                right: 10px;
                width: 320px;
                height: 320px;
                background: rgba(255, 255, 255, 0.92);
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.10);
                backdrop-filter: blur(4px);
                -webkit-backdrop-filter: blur(4px);
                z-index: 10;
                pointer-events: none;
            }}
            #radar-plot {{ width: 100%; height: 100%; }}
            #initial-hover-box {{
                position: absolute;
                top: 15px;
                left: 15px;
                right: 350px;
                background-color: rgba(106, 90, 205, 0.95);
                color: white;
                padding: 10px 14px;
                border-radius: 8px;
                font-size: 12px;
                font-family: Arial, sans-serif;
                line-height: 1.4;
                box-shadow: 0 4px 12px rgba(0,0,0,0.4);
                border: 1px solid rgba(255,255,255,0.2);
                z-index: 100;
                opacity: 1;
                transition: opacity 0.6s ease;
                pointer-events: none;
                animation: fadeOut 1s ease-in-out 5s forwards;
            }}
            @keyframes fadeOut {{
                to {{ opacity: 0; pointer-events: none; }}
            }}
        </style>
    </head>
    <body>
        <div class="plot-wrap">
            <div id="umap-plot"></div>
            <div id="radar-wrap"><div id="radar-plot"></div></div>
            <div id="initial-hover-box">
                <b>Emotion Pulse: Tender Uncertainty</b><br>
                <b>Top Emotions:</b> caring: 75% annoying: 71% desire: 70% disapproval: 62% realization: 60% remorse: 60% curiosity: 59% approval: 56% excitement: 54% confusion: 53%<br>
                <b>Post/Comment:</b> Insight Timer used to be amazing. While the community content is a nice-to-have, I mostly used it for the timer feature. However in the past few months the number of disruptive...<br><br>
                <b><span style="text-decoration: underline; text-decoration-color: #ffc300; text-decoration-thickness: 3px;">Hover over</span></b> a point to replace this — and watch the radar in the top-right redraw.
            </div>
        </div>

        <script>
        const PAYLOAD = {json.dumps(payload)};
        const THETA = PAYLOAD.theta_labels;
        const COLORS = PAYLOAD.archetype_colors;

        function hexToRgba(hex, a) {{
            const h = hex.replace('#', '');
            return `rgba(${{parseInt(h.slice(0,2),16)}},${{parseInt(h.slice(2,4),16)}},${{parseInt(h.slice(4,6),16)}},${{a}})`;
        }}

        const umapLayout = {{
            plot_bgcolor: 'white',
            paper_bgcolor: 'white',
            font: {{ color: 'black' }},
            showlegend: false,
            xaxis: {{ showgrid: false, zeroline: false, showticklabels: false, ticks: '', scaleanchor: 'y', scaleratio: 1, fixedrange: true }},
            yaxis: {{ showgrid: false, zeroline: false, showticklabels: false, ticks: '', range: PAYLOAD.y_range, fixedrange: true }},
            hovermode: 'closest',
            autosize: true,
            margin: {{ t: 60, b: 10, l: 40, r: 40 }}
        }};
        const umapConfig = {{
            displayModeBar: false,
            displaylogo: false,
            scrollZoom: false,
            doubleClick: false,
            responsive: true
        }};
        Plotly.newPlot('umap-plot', PAYLOAD.traces, umapLayout, umapConfig);

        // Radar starts blank — just the 8 labelled axes with a 0–1 grid.
        const radarLayout = {{
            polar: {{
                radialaxis: {{
                    visible: true, range: [0, 1],
                    showticklabels: false, ticks: '',
                    gridcolor: 'rgba(0,0,0,0.08)',
                    linecolor: 'rgba(0,0,0,0.12)'
                }},
                angularaxis: {{
                    tickfont: {{ size: 10, family: 'sans-serif', color: '#475569' }},
                    direction: 'clockwise',
                    rotation: 90,
                    gridcolor: 'rgba(0,0,0,0.06)',
                    linecolor: 'rgba(0,0,0,0.12)'
                }},
                bgcolor: 'rgba(255,255,255,0)'
            }},
            margin: {{ t: 36, r: 60, b: 32, l: 60 }},
            showlegend: false,
            paper_bgcolor: 'rgba(255,255,255,0)'
        }};
        // Axis-only scaffolding. One invisible trace at r=0 so Plotly lays
        // out the θ labels immediately; gets replaced on first hover.
        const emptyRadar = [{{
            type: 'scatterpolar',
            r: Array(THETA.length).fill(0),
            theta: THETA,
            mode: 'markers',
            marker: {{ size: 0, color: 'rgba(0,0,0,0)' }},
            hoverinfo: 'skip', showlegend: false
        }}];
        const radarConfig = {{ displayModeBar: false, staticPlot: true, responsive: true }};
        Plotly.newPlot('radar-plot', emptyRadar, radarLayout, radarConfig);

        const umapDiv = document.getElementById('umap-plot');
        umapDiv.on('plotly_hover', (evt) => {{
            const pt = evt.points[0];
            if (!pt || !pt.customdata) return;  // centroid labels carry no customdata
            const scores = pt.customdata;
            const archetype = pt.data.name;
            const color = COLORS[archetype] || '#888';
            Plotly.react('radar-plot', [{{
                type: 'scatterpolar',
                r: [...scores, scores[0]],
                theta: [...THETA, THETA[0]],
                name: archetype,
                mode: 'lines',
                line: {{ color: color, width: 2.5 }},
                fillcolor: hexToRgba(color, 0.32),
                fill: 'toself',
                opacity: 1,
                hoverinfo: 'skip', showlegend: false
            }}], radarLayout, radarConfig);
        }});
        umapDiv.on('plotly_unhover', () => {{
            Plotly.react('radar-plot', emptyRadar, radarLayout, radarConfig);
        }});

        // Seed box fades after 5s via CSS animation. Also dismiss on first
        // cursor move over the plot — whichever happens first.
        const seedBox = document.getElementById('initial-hover-box');
        if (seedBox) {{
            const dismiss = () => {{
                seedBox.style.opacity = '0';
                setTimeout(() => seedBox.remove(), 600);
            }};
            umapDiv.addEventListener('mousemove', dismiss, {{ once: true }});
        }}
        </script>
    </body>
    </html>
    """

    components.html(html_code, height=1100, scrolling=False)

    st.markdown("""
        <div class="footer-text" style="text-align:center; font-size:1rem; font-weight:600; color:#667eea; margin-top:1.5rem; padding:0.8rem; border-top:1px solid #eee;">
            Powered By MinyanLabs ©2026
        </div>
    """, unsafe_allow_html=True)


run()
