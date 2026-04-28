#!/usr/bin/env python3
"""
Phase 1 chart export.

Produces self-contained HTML files for the two Plotly-based chart pages so the
Astro site can serve them directly from Cloudflare Pages — no Streamlit at runtime,
zero cold-start latency.

Outputs:
  site/public/charts/emotion-pulse.html        (replicates pages/0_Emotion_Pulse.py)
  site/public/charts/community-dynamics.html   (renders precomputed Sankey JSON)

Run from the repo root:
  python3 scripts/build_chart_figures.py

Re-run whenever the source parquet/JSON changes. Same cadence as
scripts/build_precomputed.py.
"""

import json
import pathlib
import re
from typing import Any

import numpy as np
import pandas as pd

from _canonical import ARCHETYPE_COLORS, TOPIC_MAPPING

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_PUBLIC = ROOT / "site" / "public"
CHARTS_DIR = SITE_PUBLIC / "charts"

PLOTLY_CDN_URL = "https://cdn.plot.ly/plotly-2.35.2.min.js"


def _shift_rgb(hex_color: str, delta: int) -> str:
    """Adjust each channel by `delta`, clamped to [0, 255]. +25 lifts; -30 darkens."""
    h = hex_color.lstrip("#")
    rgb = [max(0, min(255, int(h[i:i + 2], 16) + delta)) for i in (0, 2, 4)]
    return "#" + "".join(f"{v:02X}" for v in rgb)


# Mobile baseline injected into every chart's <style>. Keeps each chart
# readable + tappable at narrow viewports without dedicated per-chart logic.
# Per-chart polish (label collision tuning, region repositioning, etc.) lives
# in each chart's own <style>. This is the floor.
MOBILE_CSS = """
        /* Tablet-and-below fluid scaling. clamp() lets sizes flex across
           the full phone-to-tablet range (320px iPhone SE → 1024px iPad
           landscape) without step breakpoints. The radar overlay and
           seed pop-up stay visible but scale down proportionally. */
        @media (max-width: 1024px) {
            body { font-size: clamp(13px, 1.6vw, 16px); }
            .modebar { display: none !important; }
            .hovertext {
                font-size: clamp(11px, 2.2vw, 14px) !important;
                max-width: clamp(220px, 60vw, 360px) !important;
            }
            button, [role="button"], input[type="checkbox"] + label,
            .quarter-btn, .nav-btn, .toggle-btn, .quarter-chip {
                min-height: 44px;
                touch-action: manipulation;
            }
            /* Radar floor at 140px so all 8 emotion axes render legibly.
               Below ~140 Plotly clips most axis labels. */
            #radar-wrap, .radar-overlay {
                width: clamp(140px, 25vw, 240px) !important;
                height: clamp(140px, 25vw, 240px) !important;
                top: 4px !important; right: 4px !important;
            }
            /* Seed box: right offset stays clear of radar's left edge.
               Drop the max-height clamp so the box auto-sizes to its
               (terse) mobile content; the previous 70-120px ceiling
               clipped text when it wrapped to more lines at narrow
               widths. The mobile content is 3 short lines, will sit
               naturally around 60-90px depending on wrap. */
            #initial-hover-box {
                right: clamp(155px, 30vw, 270px) !important;
                max-width: clamp(160px, 55vw, 600px) !important;
                max-height: none !important;
                font-size: clamp(10px, 2.4vw, 13px) !important;
                padding: clamp(6px, 1.6vw, 10px) clamp(8px, 2vw, 14px) !important;
                line-height: 1.35 !important;
                overflow: visible !important;
            }
            .stats-bar, .legend, .quarter-strip {
                font-size: clamp(11px, 1.8vw, 14px) !important;
                padding: clamp(6px, 1.5vw, 10px) !important;
            }
        }
        /* Phone heights — vh-based so chart fits the device, not pixel ladder. */
        @media (max-width: 768px) {
            .plot-wrap { height: clamp(560px, 80vh, 720px) !important; }
        }
        @media (max-width: 480px) {
            .plot-wrap { height: clamp(520px, 78vh, 660px) !important; }
        }
        /* Small-mobile (≤360px): Galaxy Fold folded, older Androids,
           iPhone SE 1st gen. Seed + radar previously consumed the chart's
           horizontal space; shrink both, swap to ultra-terse seed payload,
           and tighten chip legend so all 5 fit on one row. Bumps radar bg
           transparency so chart shows through where they overlap. */
        @media (max-width: 360px) {
            #radar-wrap, .radar-overlay {
                width: 110px !important;
                height: 110px !important;
                background: rgba(255, 255, 255, 0.78) !important;
            }
            #initial-hover-box {
                right: 124px !important;
                max-width: 50vw !important;
                font-size: 10px !important;
                padding: 5px 8px !important;
                line-height: 1.3 !important;
                background-color: rgba(106, 90, 205, 0.92) !important;
            }
            /* Single-line seed at the smallest screens. The mobile variant
               still wraps to 4 lines at 280-320px; tiny variant is one
               headline + one hint, ~50px tall. */
            .seed-content-mobile { display: none !important; }
            .seed-content-tiny   { display: block !important; }
            #archetype-legend {
                gap: 4px !important;
                padding: 8px 6px 2px !important;
                font-size: 10px !important;
            }
            #archetype-legend .chip {
                padding: 2px 6px !important;
                gap: 4px !important;
            }
            #archetype-legend .chip::before {
                width: 8px !important; height: 8px !important;
            }
        }
"""


# ----------------------------------------------------------------------------
# Emotion Pulse — UMAP scatter + radar overlay + initial hover seed box
#
# Replicates pages/0_Emotion_Pulse.py::_build_plot_payload() and the surrounding
# html_code template. Kept in lockstep with the Streamlit version; if the
# Streamlit page changes, update here.
# ----------------------------------------------------------------------------

USER_RADAR_EMOTIONS = [
    "gratitude", "joy", "caring", "love",
    "confusion", "fear", "sadness", "grief",
]
RADAR_THETA_LABELS = [
    "🙏 Gratitude", "😊 Joy", "🤗 Caring", "❤️ Love",
    "😕 Confusion", "😨 Fear", "😢 Sadness", "💔 Grief",
]
# Mobile-friendly short forms of archetype labels for narrow viewports
# (<768px). The full label is positioned for a 1100px desktop canvas;
# at phone width the trailing word truncates ("Soothing E..." / "Anxious C...").
ARCHETYPE_SHORT_LABELS = {
    "Reflective Caring": "Reflective",
    "Soothing Empathy": "Soothing",
    "Tender Uncertainty": "Tender",
    "Melancholic Confusion": "Melancholic",
    "Anxious Concern": "Anxious",
}
ARCHETYPE_SYMBOLS = {
    "Reflective Caring": ("circle", 8),
    "Soothing Empathy": ("diamond", 8),
    "Tender Uncertainty": ("triangle-nw", 9),
    "Melancholic Confusion": ("star-square", 8),
    "Anxious Concern": ("star-triangle-up", 8),
}
CENTROID_OFFSETS = {
    "Reflective Caring": (3.9, 1.2),
    "Soothing Empathy": (-3.0, 3.0),
    "Tender Uncertainty": (-4.1, -2.5),
    "Melancholic Confusion": (0.5, -1.5),
    "Anxious Concern": (2.4, -0.3),
}


def _ideal_text_color(bg_hex: str) -> str:
    bg_hex = bg_hex.lstrip("#")
    r, g, b = (int(bg_hex[i:i + 2], 16) for i in (0, 2, 4))
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "black" if luminance > 186 else "white"


def build_emotion_pulse_payload() -> dict[str, Any]:
    df = pd.read_parquet(ROOT / "precomputed/emotion_clusters_slim.parquet")

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

    # Bake the raw cluster centroid alongside each label trace so the JS
    # label-mode handler can compute viewport-proportional positions
    # (centroid + offset × scale, where scale is fluid 0.25 → 1.0 across
    # 320px → 1100px viewport widths). Plotly ignores unknown top-level
    # trace keys, so these pass through harmlessly.
    centroids = df.groupby("archetype_label")[["umap_x", "umap_y"]].mean()
    for archetype, (cx, cy) in centroids.iterrows():
        dx, dy = CENTROID_OFFSETS.get(archetype, (0, 0))
        traces.append({
            "x": [float(cx + dx)], "y": [float(cy + dy)],
            "mode": "text",
            "text": [f"<b>{archetype}</b>"],
            "textfont": {"size": 20, "color": ARCHETYPE_COLORS[archetype], "family": "sans-serif"},
            "hoverinfo": "skip",
            "showlegend": False,
            "_centroid_x": float(cx),
            "_centroid_y": float(cy),
        })

    y_min, y_max = float(df["umap_y"].min()), float(df["umap_y"].max())
    y_range_pad_top = 0.13 * (y_max - y_min)
    y_range_pad_bot = 0.01 * (y_max - y_min)

    seed_mask = df["hover_text"].str.contains("Insight Timer used to be amazing", na=False)
    if seed_mask.any():
        seed_row = df[seed_mask].iloc[0]
        seed_radar_values = [float(seed_row[c]) for c in USER_RADAR_EMOTIONS]
        seed_archetype = str(seed_row["archetype_label"])
        # Pull the "Top Emotions:" segment out of the seed's hover_text so
        # the initial overlay can carry the same emotion-with-% breakdown
        # the active-hover tooltip shows. Source has soft <br>-wraps inside
        # the segment; collapse to one space-separated line.
        ht = str(seed_row["hover_text"])
        m = re.search(r"<b>Top Emotions:</b>(.*?)<b>Post/Comment:", ht, flags=re.DOTALL)
        seed_top_emotions = re.sub(r"\s+", " ", m.group(1).replace("<br>", " ")).strip() if m else None
    else:
        seed_radar_values = None
        seed_archetype = None
        seed_top_emotions = None

    return {
        "traces": traces,
        "y_range": [y_min - y_range_pad_bot, y_max + y_range_pad_top],
        "archetype_colors": ARCHETYPE_COLORS,
        "short_labels": ARCHETYPE_SHORT_LABELS,
        "theta_labels": RADAR_THETA_LABELS,
        "seed_radar_values": seed_radar_values,
        "seed_archetype": seed_archetype,
        "seed_top_emotions": seed_top_emotions,
    }


def build_emotion_pulse_shell() -> str:
    """Phase 3a: shell HTML for emotion-pulse. The shell paints a skeleton
    instantly, then fetches emotion-pulse-data.json (~470KB gzip) in
    parallel and hydrates the Plotly trace via init(). Cuts first-paint
    LCP from ~2s to ~400ms on cold cache because the shell is <10KB and
    Plotly.js already streams from CDN.

    Failure path: if the JSON fetch errors (404, network drop, parse
    error), the skeleton replaces with a "refresh to retry" message
    instead of leaving an empty chart silently.
    """
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emotion Pulse — MindSpace OS</title>
    <script src="{PLOTLY_CDN_URL}"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: Arial, sans-serif; background: white; }}
        .plot-wrap {{ position: relative; width: 100%; height: 1080px; }}
        #umap-plot {{ width: 100%; height: 100%; }}
        #radar-wrap {{
            position: absolute;
            top: 0px; right: 10px;
            width: 240px; height: 240px;
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
            top: 15px; left: 15px; right: 350px;
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
        }}
        /* Three seed-box content variants:
             - desktop:  full emotion list + post-quote (>1024px)
             - mobile:   archetype + 3 emotions + tap hint (361-1024px)
             - tiny:     archetype + tap hint, single line (≤360px)
           Swapped via @media to avoid clipping at narrow widths. */
        .seed-content-desktop {{ display: block; }}
        .seed-content-mobile  {{ display: none; }}
        .seed-content-tiny    {{ display: none; }}
        @media (max-width: 1024px) {{
            .seed-content-desktop {{ display: none; }}
            .seed-content-mobile  {{ display: block; }}
        }}
        /* HTML archetype legend below the chart on mobile/tablet. The
           in-chart text-trace labels get hidden via Plotly.restyle so the
           data points read clean; this strip carries the cluster→color
           legend instead. */
        #archetype-legend {{
            display: none;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
            padding: 12px 14px;
            font-family: Arial, sans-serif;
            font-size: clamp(11px, 2.4vw, 13px);
        }}
        #archetype-legend .chip {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 4px 10px;
            border-radius: 999px;
            background: rgba(255,255,255,0.85);
            border: 1px solid rgba(0,0,0,0.06);
            color: #1e293b;
            white-space: nowrap;
        }}
        #archetype-legend .chip::before {{
            content: '';
            display: inline-block;
            width: 10px; height: 10px;
            border-radius: 50%;
            background: var(--c);
        }}
        @media (max-width: 1024px) {{
            #archetype-legend {{ display: flex; }}
        }}
{MOBILE_CSS}
    </style>
</head>
<body>
    <div class="plot-wrap">
        <div id="umap-plot"></div>
        <div id="radar-wrap"><div id="radar-plot"></div></div>
        <div id="initial-hover-box">
            <div class="seed-content-desktop">
                <b>Emotion Pulse: Tender Uncertainty</b><br>
                <b>Top Emotions:</b> caring: 75% annoying: 71% desire: 70% disapproval: 62% realization: 60% remorse: 60% curiosity: 59% approval: 56% excitement: 54% confusion: 53%<br>
                <b>Post/Comment:</b> Insight Timer used to be amazing. While the community content is a nice-to-have, I mostly used it for the timer feature. However in the past few months the number of disruptive...<br><br>
                <span style="color: inherit; border-bottom: 4px solid #FFD700; padding-bottom: 1px; font-weight: 700;">Hover</span> to discover details - and watch its emotion radar.
            </div>
            <div class="seed-content-mobile">
                <b>Tender Uncertainty</b><br>
                caring 75% &middot; annoying 71% &middot; desire 70%<br>
                <span style="color: inherit; border-bottom: 3px solid #FFD700; font-weight: 700;">Tab a dot</span> for details.
            </div>
            <div class="seed-content-tiny">
                <b>Tender Uncertainty</b><br>
                <span style="color: inherit; border-bottom: 2px solid #FFD700; font-weight: 700;">Tab a dot</span> for details.
            </div>
        </div>
    </div>
    <div id="archetype-legend" aria-label="Archetype legend">
        <span class="chip" style="--c: #ff5e78">Reflective Caring</span>
        <span class="chip" style="--c: #00c49a">Soothing Empathy</span>
        <span class="chip" style="--c: #6a5acd">Tender Uncertainty</span>
        <span class="chip" style="--c: #9a32cd">Melancholic Confusion</span>
        <span class="chip" style="--c: #ffc300">Anxious Concern</span>
    </div>

    <script>
    // Phase 3a: skeleton element + fetch wrapper. The skeleton sits behind
    // the chart wrap and gets removed by init() once Plotly has painted.
    (function injectSkeleton() {{
        var sk = document.createElement('div');
        sk.id = 'chart-skeleton';
        sk.style.cssText = 'position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-family:Arial,sans-serif;font-size:14px;background:#fafafa;z-index:5;';
        sk.textContent = 'Loading…';
        var wrap = document.querySelector('.plot-wrap');
        if (wrap) wrap.appendChild(sk);
    }})();

    fetch('./emotion-pulse-data.json')
        .then(function (r) {{ if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); }})
        .then(function (payload) {{ init(payload); }})
        .catch(function (err) {{
            console.error('emotion-pulse: data fetch failed', err);
            var sk = document.getElementById('chart-skeleton');
            if (sk) {{
                sk.textContent = 'Chart failed to load. Refresh to retry.';
                sk.style.color = '#64748b';
            }}
        }});

    function init(PAYLOAD) {{
    var skEl = document.getElementById('chart-skeleton');
    if (skEl) skEl.remove();
    const THETA = PAYLOAD.theta_labels;
    const COLORS = PAYLOAD.archetype_colors;

    function hexToRgba(hex, a) {{
        const h = hex.replace('#', '');
        return `rgba(${{parseInt(h.slice(0,2),16)}},${{parseInt(h.slice(2,4),16)}},${{parseInt(h.slice(4,6),16)}},${{a}})`;
    }}

    const umapLayout = {{
        plot_bgcolor: 'white', paper_bgcolor: 'white', font: {{ color: 'black' }},
        showlegend: false,
        xaxis: {{ showgrid: false, zeroline: false, showticklabels: false, ticks: '', scaleanchor: 'y', scaleratio: 1, fixedrange: true }},
        yaxis: {{ showgrid: false, zeroline: false, showticklabels: false, ticks: '', range: PAYLOAD.y_range, fixedrange: true }},
        hovermode: 'closest', autosize: true,
        margin: {{ t: 60, b: 10, l: 40, r: 40 }}
    }};
    const umapConfig = {{ displayModeBar: false, displaylogo: false, scrollZoom: false, doubleClick: false, responsive: true }};
    Plotly.newPlot('umap-plot', PAYLOAD.traces, umapLayout, umapConfig);

    // Viewport-aware archetype label sizing + positioning. Three things
    // scale with viewport width across the 320px → 1280px range:
    //   - text: full label vs short ("Anxious Concern" → "Anxious") at <=1024
    //   - font size: lerp from 13 (320px) up to 20 (>=1100px)
    //   - data-coordinate position: offset × scale, where scale = clamp(0.25, w/1100, 1.0)
    // The fluid scale keeps labels close to their cluster centroid on small
    // phones (iPhone SE 320px → 0.29 scale) and pushes them outward as the
    // canvas grows toward desktop.
    const SHORT_LABELS = PAYLOAD.short_labels || {{}};
    function lerp(a, b, t) {{ return a + (b - a) * t; }}
    function applyArchetypeLabelMode() {{
        const w = window.innerWidth;
        const narrow = w <= 1024;
        // On narrow viewports the text-trace labels overplot the data
        // points and are hard to read no matter where they sit. Hide them
        // entirely; the HTML #archetype-legend strip below the chart
        // carries the cluster→color mapping instead.
        const offsetScale = Math.max(0.15, Math.min(1.0, 0.15 + (w - 320) / 800 * 0.85));
        const fontSize = Math.round(lerp(13, 20, Math.max(0, Math.min(1, (w - 320) / (1100 - 320)))));
        const traces = PAYLOAD.traces;
        const updates = {{ text: [], 'textfont.size': [], x: [], y: [], visible: [] }};
        const indices = [];
        traces.forEach((t, i) => {{
            if (t.mode !== 'text' || !Array.isArray(t.text) || t.text.length !== 1) return;
            const raw = String(t.text[0]).replace(/<[^>]+>/g, '');
            const short = SHORT_LABELS[raw];
            if (!short) return;
            indices.push(i);
            updates.text.push([narrow ? `<b>${{short}}</b>` : `<b>${{raw}}</b>`]);
            updates['textfont.size'].push(fontSize);
            updates.visible.push(narrow ? false : true);
            if (t._centroid_x != null && t._centroid_y != null) {{
                const dx = t.x[0] - t._centroid_x;
                const dy = t.y[0] - t._centroid_y;
                updates.x.push([t._centroid_x + dx * offsetScale]);
                updates.y.push([t._centroid_y + dy * offsetScale]);
            }} else {{
                updates.x.push(t.x);
                updates.y.push(t.y);
            }}
        }});
        if (indices.length) Plotly.restyle('umap-plot', updates, indices);
    }}
    applyArchetypeLabelMode();

    // Viewport-aware hover content. Desktop hover text is pre-wrapped to
    // 75 chars/line and lists 10 emotions + a 200-char post excerpt.
    // On phones that overflows the chart canvas: text gets cut off
    // ("exciteme...") and the tooltip covers the entire plot. On <=768px
    // rewrite each marker trace's text to: archetype name + the Top
    // Emotions segment with %s, dropping the Post/Comment quote and the
    // prior "See radar →" affordance.
    function compactHoverText(s) {{
        const raw = String(s || '');
        // Title: keep the archetype name as-is, just strip the inline <b>
        // tags so we re-wrap with our own bold.
        const title = raw.split('<br>')[0].replace(/<\/?b>/g, '').trim();
        // Top Emotions: pulled out of the segment between its label and
        // "Post/Comment:". Plotly hover renders SVG text with no auto-wrap;
        // chunk pairs onto their own line so the tooltip fits a 360px
        // viewport. Pair = "<emotion>: <pct>%".
        const m = raw.match(/<b>Top Emotions:<\/b>([\s\S]*?)<b>Post\/Comment:/i);
        let emotionsHtml = '';
        if (m) {{
            const flat = m[1].replace(/<br\s*\/?>/gi, ' ').replace(/\s+/g, ' ').trim();
            const pairs = flat.match(/[a-z][a-z\- ]*?:\s*\d{{1,3}}%/gi) || [];
            // 2 per row keeps each line ~22-26 chars (≤220px at 11px font).
            const rows = [];
            for (let i = 0; i < pairs.length; i += 2) {{
                rows.push(pairs.slice(i, i + 2).join(' · '));
            }}
            emotionsHtml = rows.join('<br>');
        }}
        return `<b>${{title}}</b>${{emotionsHtml ? '<br>' + emotionsHtml : ''}}`;
    }}
    function applyHoverContentMode() {{
        const w = window.innerWidth;
        const narrow = w <= 768;
        const traces = PAYLOAD.traces;
        const updates = {{ text: [] }};
        const indices = [];
        traces.forEach((t, i) => {{
            if (t.mode !== 'markers' || !Array.isArray(t.text) || t.hoverinfo === 'skip') return;
            indices.push(i);
            updates.text.push(narrow ? t.text.map(compactHoverText) : t.text);
        }});
        if (indices.length) Plotly.restyle('umap-plot', updates, indices);
    }}
    applyHoverContentMode();

    let resizeTimer;
    window.addEventListener('resize', () => {{
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {{
            applyArchetypeLabelMode();
            applyHoverContentMode();
            radarLayout = buildRadarLayout();
            Plotly.react('radar-plot', currentRadar, radarLayout, radarConfig);
        }}, 150);
    }});

    // Radar layout — responsive so all 8 axes stay visible at phone widths.
    // The fixed desktop margins (60/60 horizontal, 36/32 vertical) collapse
    // the polar plot area to nothing inside the ≤360px 110×110 wrap, which
    // is why the polygon rendered invisible. Scale margins + axis-label
    // font size down with viewport width so the polygon fills the wrap.
    function buildRadarLayout() {{
        const w = window.innerWidth;
        const tiny = w <= 360;
        const narrow = w <= 768;
        const margin = tiny
            ? {{ t: 14, r: 18, b: 14, l: 18 }}
            : (narrow ? {{ t: 22, r: 30, b: 22, l: 30 }} : {{ t: 36, r: 60, b: 32, l: 60 }});
        const tickSize = tiny ? 7 : (narrow ? 8 : 10);
        return {{
            polar: {{
                radialaxis: {{ visible: true, range: [0, 1], showticklabels: false, ticks: '', gridcolor: 'rgba(0,0,0,0.08)', linecolor: 'rgba(0,0,0,0.12)' }},
                angularaxis: {{ tickfont: {{ size: tickSize, family: 'sans-serif', color: '#475569' }}, direction: 'clockwise', rotation: 90, gridcolor: 'rgba(0,0,0,0.06)', linecolor: 'rgba(0,0,0,0.12)' }},
                bgcolor: 'rgba(255,255,255,0)'
            }},
            margin: margin,
            showlegend: false,
            paper_bgcolor: 'rgba(255,255,255,0)'
        }};
    }}
    let radarLayout = buildRadarLayout();
    const emptyRadar = [{{
        type: 'scatterpolar', r: Array(THETA.length).fill(0), theta: THETA,
        mode: 'markers', marker: {{ size: 0, color: 'rgba(0,0,0,0)' }},
        hoverinfo: 'skip', showlegend: false
    }}];
    const radarConfig = {{ displayModeBar: false, staticPlot: true, responsive: true }};
    function buildRadarTrace(scores, archetype) {{
        const color = COLORS[archetype] || '#6a5acd';
        return [{{
            type: 'scatterpolar', r: [...scores, scores[0]], theta: [...THETA, THETA[0]],
            name: archetype, mode: 'lines',
            line: {{ color: color, width: 2.5 }},
            fillcolor: hexToRgba(color, 0.32), fill: 'toself', opacity: 1,
            hoverinfo: 'skip', showlegend: false
        }}];
    }}
    const seedRadar = (PAYLOAD.seed_radar_values && PAYLOAD.seed_archetype)
        ? buildRadarTrace(PAYLOAD.seed_radar_values, PAYLOAD.seed_archetype)
        : emptyRadar;
    let currentRadar = seedRadar;
    Plotly.newPlot('radar-plot', currentRadar, radarLayout, radarConfig);

    const umapDiv = document.getElementById('umap-plot');
    const seedBox = document.getElementById('initial-hover-box');
    let seedDismissed = false;
    function dismissSeedBox() {{
        if (seedDismissed || !seedBox) return;
        seedDismissed = true;
        seedBox.style.opacity = '0';
        setTimeout(() => seedBox.remove(), 600);
    }}

    // Touch detection: hover is emulated as fire-once on tap, then unhover
    // immediately fires when the touch ends. On touch devices we want the
    // radar to persist after a tap (the user just lifted their finger;
    // resetting the radar means they can never see what they tapped).
    // Skip the unhover handler on touch-only devices.
    const isTouch = window.matchMedia('(hover: none)').matches;
    umapDiv.on('plotly_hover', (evt) => {{
        const pt = evt.points[0];
        if (!pt || !pt.customdata) return;
        currentRadar = buildRadarTrace(pt.customdata, pt.data.name);
        Plotly.react('radar-plot', currentRadar, radarLayout, radarConfig);
        dismissSeedBox();
    }});
    if (!isTouch) {{
        umapDiv.on('plotly_unhover', () => {{
            currentRadar = seedRadar;
            Plotly.react('radar-plot', currentRadar, radarLayout, radarConfig);
        }});
    }}
    // Plotly fires plotly_click reliably on tap. Belt-and-suspenders so
    // the radar updates even if hover doesn't fire on the platform.
    umapDiv.on('plotly_click', (evt) => {{
        const pt = evt.points[0];
        if (!pt || !pt.customdata) return;
        currentRadar = buildRadarTrace(pt.customdata, pt.data.name);
        Plotly.react('radar-plot', currentRadar, radarLayout, radarConfig);
        dismissSeedBox();
    }});
    }} /* end init(PAYLOAD) */
    </script>
</body>
</html>"""


# ----------------------------------------------------------------------------
# Community Dynamics — Sankey from precomputed JSON.
#
# Reads precomputed/figures/community_dynamics_sankey.json (the figure already
# serialized by scripts/build_precomputed.py) and wraps it in a minimal HTML
# shell that loads Plotly from CDN.
# ----------------------------------------------------------------------------

def build_community_dynamics_html() -> str:
    fig_path = ROOT / "precomputed" / "figures" / "community_dynamics_sankey.json"
    fig = json.loads(fig_path.read_text())

    # Free the Sankey from its baked layout.height (670px) so the flow fills whatever
    # vertical space the iframe gives it. Without this the ribbons are clipped at top
    # and bottom regardless of container size. Also tighten margins for more flow room.
    layout = fig.setdefault('layout', {})
    layout.pop('height', None)
    layout['autosize'] = True
    # Bottom margin 80 (vs the prior 8) leaves a strip below the Sankey for the
    # native Plotly hover tooltip — without it, hovers on bottom-row ribbons get
    # clipped by the iframe edge.
    layout['margin'] = {'l': 10, 'r': 10, 't': 8, 'b': 80}

    # Strip raw-count rows from hover tooltips. Node tooltips drop "Posts" and
    # "Connected comments"; link (ribbon) tooltips drop "Count". The normalized
    # share % rows (Global / Post / Comment Share) carry the same info.
    drop_re = re.compile(r'^\s*(Posts|Connected comments|Count)\s*:', re.IGNORECASE)
    def _strip_counts(html: str) -> str:
        parts = html.split('<br>')
        kept = [p for p in parts if not drop_re.match(re.sub(r'<[^>]+>', '', p))]
        return '<br>'.join(kept)
    trace = fig.get('data', [{}])[0]
    node = trace.get('node', {})
    if 'customdata' in node:
        node['customdata'] = [_strip_counts(c) for c in node['customdata']]
    link = trace.get('link', {})
    if 'customdata' in link:
        link['customdata'] = [_strip_counts(c) for c in link['customdata']]

    fig_json = json.dumps(fig)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community Dynamics — MindSpace OS</title>
    <script src="{PLOTLY_CDN_URL}"></script>
    <style>
        html, body {{ height: 100%; }}
        body {{
            margin: 0; padding: 0;
            font-family: 'DM Sans', system-ui, -apple-system, Arial, sans-serif;
            background: white;
            display: flex; flex-direction: column;
        }}
        .column-eyebrows {{
            flex: 0 0 auto;
            display: flex; justify-content: space-between;
            padding: 12px 32px 6px 32px;
            font-size: 13px; line-height: 1.2;
            color: #64748b; letter-spacing: 0.02em;
            font-weight: 600;
        }}
        /* The plot consumes whatever vertical space remains so the Sankey ribbons
           span the full iframe height. */
        #sankey-plot {{ flex: 1 1 auto; width: 100%; min-height: 0; }}
        .hover-hint-row {{
            flex: 0 0 auto;
            text-align: center;
            padding: 0 32px 8px 32px;
            font-size: 14px;
            color: #4A5568;
            line-height: 1.5;
        }}
        .hover-hint {{
            color: #4A5568;
            border-bottom: 4px solid #FFD700;
            padding-bottom: 1px;
            font-weight: 700;
        }}
        /* Hint-text toggle — touch devices don't hover. The (hover: none) media
           query swaps "Hover" copy for "Tap" so the prompt teaches the right
           gesture per input modality. */
        .hint-mouse {{ display: inline; }}
        .hint-touch {{ display: none; }}
        @media (hover: none) {{
            .hint-mouse {{ display: none; }}
            .hint-touch {{ display: inline; }}
        }}
        /* Tap readout — Plotly Sankey doesn't fire hover on touch devices,
           only click. Show the customdata in this panel below the chart on
           touch so mobile users get the same info desktop hover provides. */
        .tap-readout {{
            display: none;
            flex: 0 0 auto;
            margin: 6px 16px 12px;
            padding: 6px 0;
            font-size: 13px; line-height: 1.5; color: #2c3e50;
            /* Reserve a fixed slot at the bottom of the iframe so the
               readout never gets clipped when populated. Worst case is
               1 title + 3 share lines × ~20px line-height + padding. */
            min-height: 100px;
            box-sizing: border-box;
        }}
        .tap-readout.empty {{
            color: #94a3b8; font-style: italic;
        }}
        .tap-readout b {{ color: #2c3e50; }}
        .tap-readout .tr-title {{ display: block; font-weight: 700; margin-bottom: 2px; }}
        .tap-readout .tr-stat {{ display: block; }}
        @media (hover: none) {{
            .tap-readout {{ display: block; }}
        }}
{MOBILE_CSS}
    </style>
</head>
<body>
    <div class="hover-hint-row">
      <span class="hint-mouse"><span class="hover-hint">Hover</span> to see how emotions flow from posts to replies</span>
      <span class="hint-touch"><span class="hover-hint">Tap</span> a ribbon to see how emotions flow from posts to replies</span>
    </div>
    <div class="column-eyebrows"><span>Posts</span><span>Replies</span></div>
    <div id="sankey-plot"></div>
    <div id="tap-readout" class="tap-readout empty">Tap a ribbon or node above for details.</div>
    <script>
    const FIG = {fig_json};
    const config = {{
        displayModeBar: false, displaylogo: false, responsive: true,
        modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
    }};
    // The serialized figure already has its own layout. Pass through unchanged.
    Plotly.newPlot('sankey-plot', FIG.data, FIG.layout, config).then((gd) => {{
        // Force Plotly to measure the flex-sized container after first paint and on resize,
        // otherwise the Sankey can underdraw on tall iframes.
        Plotly.Plots.resize('sankey-plot');
        // Touch fallback: Plotly Sankey hover is mouseenter-only, so phones
        // never see the tooltip. Wire plotly_click to render the same
        // customdata into the #tap-readout panel below the chart.
        const readout = document.getElementById('tap-readout');
        gd.on('plotly_click', (e) => {{
            if (!e || !e.points || !e.points.length) return;
            const pt = e.points[0];
            const html = pt.customdata || pt.label || '';
            if (!html) return;
            // Reformat: first <br>-segment is the title (archetype pair or
            // node name), remaining segments collapse to one " / "-joined
            // line of stats. Drops the inline color/size styling that the
            // baked customdata included for the desktop tooltip.
            const segs = String(html).split(/<br\s*\/?>/i).map(s => s.trim()).filter(Boolean);
            if (!segs.length) return;
            const stripStyle = (s) => s.replace(/<b\b[^>]*>/gi, '<b>');
            const titleRaw = stripStyle(segs[0]);
            // Strip the outer <b>...</b> from the title segment so we wrap it
            // ourselves via .tr-title (consistent weight, no nested bold).
            const titleText = titleRaw.replace(/^<b>(.*?)<\/b>$/i, '$1');
            // Drop raw-count segments (Count, Posts, Comments, Connected
            // comments). The normalized share views (Global / Post / Comment)
            // carry the same info in % form, which scales cleaner on mobile.
            const dropRegex = /^(Count|Posts|Comments|Connected comments)\s*:/i;
            const stats = segs.slice(1)
                .filter(s => !dropRegex.test(s.replace(/<[^>]+>/g, '')))
                .map(stripStyle);
            // Each remaining segment renders on its own line for scannability.
            const statsHtml = stats.map(s => `<span class="tr-stat">${{s}}</span>`).join('');
            readout.classList.remove('empty');
            readout.innerHTML = `<span class="tr-title">${{titleText}}</span>${{statsHtml}}`;
        }});
    }});
    let resizeTimer = null;
    window.addEventListener('resize', () => {{
        clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => Plotly.Plots.resize('sankey-plot'), 120);
    }});
    </script>
</body>
</html>"""


# ----------------------------------------------------------------------------
# Inner Life Currents — temporal network, Time Travel slider across 6 quarters.
#
# Replicates pages/3_Inner_Life_Currents.py::build_currents_payload() and the
# surrounding html_code template. Pre-builds payloads for all 6 quarters and
# inlines them into one HTML; client-side JS handles Time Travel switching
# (Previous Quarter / Next Quarter buttons) without a server.
# ----------------------------------------------------------------------------

# TOPIC_MAPPING is imported from _canonical above. See CLAUDE.md for naming
# intent (earth-pigment palette, NYT Upshot / Pudding lineage).


def _avoid_label_collisions(labels: list[dict], min_dist: float, push_step: float) -> list[dict]:
    """Fixed-point relax: pairs of labels closer than min_dist are pushed apart along the
    vector connecting them. Bounded iterations so it always terminates. Used by Inner Life
    Currents to keep cluster labels from stacking when their data centroids land close."""
    out = [dict(l) for l in labels]
    for _ in range(8):
        moved = False
        for i in range(len(out)):
            for j in range(i + 1, len(out)):
                dx = out[i]['x'] - out[j]['x']
                dy = out[i]['y'] - out[j]['y']
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < min_dist:
                    if dist < 1e-6:
                        # Identical positions — push apart along an arbitrary axis.
                        dx, dy, dist = 1.0, 0.0, 1.0
                    nx, ny = dx / dist, dy / dist
                    push = (min_dist - dist) / 2 + push_step / 2
                    out[i]['x'] += nx * push
                    out[i]['y'] += ny * push
                    out[j]['x'] -= nx * push
                    out[j]['y'] -= ny * push
                    moved = True
        if not moved:
            break
    return out


def build_currents_payload(df_nodes: pd.DataFrame, df_edges: pd.DataFrame, quarter: str) -> dict[str, Any]:
    """Pure-Python replication of pages/3_Inner_Life_Currents.py:build_currents_payload."""
    nodes_q = df_nodes[df_nodes['quarter'] == quarter].copy()
    edges_q = df_edges[df_edges['quarter'] == quarter].copy()

    total_nodes_q = len(nodes_q)
    total_edges_q = len(edges_q)

    edge_coord_set = set(zip(edges_q['x0'].to_numpy(), edges_q['y0'].to_numpy()))
    edge_coord_set.update(zip(edges_q['x1'].to_numpy(), edges_q['y1'].to_numpy()))
    node_coord_tuples = list(zip(nodes_q['x'].to_numpy(), nodes_q['y'].to_numpy()))
    connected_count = int(sum(c in edge_coord_set for c in node_coord_tuples))

    # Rotate coords (-y, x) — same as Streamlit page.
    nodes_q['x_rot'] = -nodes_q['y']
    nodes_q['y_rot'] = nodes_q['x']
    edges_q['x0_rot'] = -edges_q['y0']
    edges_q['y0_rot'] = edges_q['x0']
    edges_q['x1_rot'] = -edges_q['y1']
    edges_q['y1_rot'] = edges_q['x1']

    unique_clusters = sorted(nodes_q['cluster_name'].dropna().unique())
    cluster_color_map = {
        c: TOPIC_MAPPING.get(c, {'color': '#808080'})['color']
        for c in unique_clusters
    }

    coord_to_cluster = dict(zip(
        zip(nodes_q['x_rot'].to_numpy(), nodes_q['y_rot'].to_numpy()),
        nodes_q['cluster_name'].to_numpy(),
    ))

    top_edge_cutoff = None
    if not edges_q.empty:
        top_k = min(10, len(edges_q))
        top_edge_cutoff = float(edges_q['weight'].nlargest(top_k).min())

    edge_data = []
    for rec in edges_q.to_dict('records'):
        start_cluster = coord_to_cluster.get((rec['x0_rot'], rec['y0_rot']), "Unknown")
        end_cluster = coord_to_cluster.get((rec['x1_rot'], rec['y1_rot']), "Unknown")
        weight = float(rec['weight'])
        edge_data.append({
            'x0': float(rec['x0_rot']),
            'y0': float(rec['y0_rot']),
            'x1': float(rec['x1_rot']),
            'y1': float(rec['y1_rot']),
            'weight': weight,
            'color': rec['color'],
            'is_top': bool(top_edge_cutoff is not None and weight >= top_edge_cutoff),
            'hover_text': f"<b>Topics:</b> {start_cluster} ↔ {end_cluster}<br><b>Themes:</b> {rec['theme_1']} ↔ {rec['theme_2']}<br><b>Engagement Score:</b> {int(weight)}<br><b>Sentiment:</b> {rec['sentiment']:.2f}"
        })

    node_data = []
    for cluster in unique_clusters:
        cluster_slice = nodes_q[nodes_q['cluster_name'] == cluster]
        color = cluster_color_map[cluster]
        for rec in cluster_slice.to_dict('records'):
            raw = rec['avg_score']
            if isinstance(raw, set):
                avg_score_display = int(next(iter(raw)))
            else:
                avg_score_display = int(float(raw))
            try:
                sentiment_value = float(rec['sentiment']) if pd.notna(rec['sentiment']) else 0.0
            except (TypeError, ValueError):
                sentiment_value = 0.0
            node_data.append({
                'x': float(rec['x_rot']),
                'y': float(rec['y_rot']),
                'size': float(rec['scaled_size']),
                'color': color,
                'cluster': cluster,
                'hover_text': f"<b>Topic:</b> {rec['cluster_name']}<br><b>Theme:</b> {rec['theme']}<br><b>Engagement Score:</b> {avg_score_display}<br><b>Sentiment:</b> {sentiment_value:.2f}"
            })

    centroids = nodes_q.groupby('cluster_name').apply(
        lambda g: pd.Series({
            'x': float(np.average(g['x_rot'], weights=g['scaled_size'])),
            'y': float(np.average(g['y_rot'], weights=g['scaled_size']))
        })
    ).reset_index()
    # Distribute labels around the full 2π so adjacent clusters don't stack.
    angle_offset = np.linspace(0, 2 * np.pi, len(centroids), endpoint=False)
    angle_offset += np.pi / len(centroids)
    radius_offset = 0.45
    centroids['x'] += radius_offset * np.cos(angle_offset)
    centroids['y'] += radius_offset * np.sin(angle_offset)
    centroids['cos'] = np.cos(angle_offset)
    initial_label_data = [
        {
            'x': float(row['x']),
            'y': float(row['y']),
            'text': row['cluster_name'],
            'color': cluster_color_map[row['cluster_name']],
            'textposition': 'middle right' if row['cos'] < -0.15 else ('middle left' if row['cos'] > 0.15 else 'middle center'),
        }
        for row in centroids.to_dict('records')
    ]
    # Belt-and-suspenders: detect any pair of labels still close enough to visually overlap
    # in the rotated network space, and nudge the lower-y one further down. Distance threshold
    # is tuned for ~14px font over the typical canvas span.
    label_data = _avoid_label_collisions(initial_label_data, min_dist=0.18, push_step=0.10)

    connected_percentage = (connected_count / total_nodes_q * 100) if total_nodes_q > 0 else 0.0

    return {
        'edge_data': edge_data,
        'node_data': node_data,
        'label_data': label_data,
        'cluster_color_map': cluster_color_map,
        'total_nodes_q': total_nodes_q,
        'total_edges_q': total_edges_q,
        'connected_count': connected_count,
        'connected_percentage': connected_percentage,
    }


def build_inner_life_currents_html() -> str:
    df_nodes = pd.read_parquet(ROOT / "precomputed/timeseries/df_nodes.parquet")
    df_edges = pd.read_parquet(ROOT / "precomputed/timeseries/df_edges.parquet")

    quarters = sorted(df_nodes['quarter'].unique())  # 2024Q1 ... 2025Q2
    quarter_labels = [f"{q[:4]}Q{q[-1]}" for q in quarters]
    payloads = {q: build_currents_payload(df_nodes, df_edges, q) for q in quarters}

    payloads_json = json.dumps({q: payloads[q] for q in quarters})
    quarters_json = json.dumps(quarters)
    quarter_labels_json = json.dumps(quarter_labels)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Inner Life Currents — MindSpace OS</title>
    <script src="{PLOTLY_CDN_URL}"></script>
    <style>
        body {{
            margin: 0; padding: 16px 0 0;
            font-family: 'Inter', system-ui, -apple-system, Arial, sans-serif;
            background: white;
            overflow-x: hidden;
        }}
        .controls {{
            display: grid;
            grid-template-columns: 1fr 2fr 1fr;
            gap: 16px;
            align-items: center;
            max-width: 960px;
            margin: 0 auto 12px;
            padding: 0 16px;
        }}
        .controls button {{
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 500;
            color: #4A5568;
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 25px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            padding: 10px 16px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1);
        }}
        .controls button:hover:not(:disabled) {{
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
            border-color: rgba(102, 126, 234, 0.5);
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2);
            color: #667eea;
        }}
        .controls button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }}
        .time-travel {{
            text-align: center;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border: 1px solid rgba(102, 126, 234, 0.2);
            border-radius: 20px;
            padding: 12px 16px;
            min-height: 44px;
            display: flex; align-items: center; justify-content: center;
            font-size: 18px; font-weight: 600; color: #4A5568;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
        }}
        .stats {{
            /* Always at least 16px breathing room from each side of the iframe.
               At wide widths the box still caps at 960px. */
            max-width: min(960px, calc(100% - 32px));
            margin: 0 auto 8px;
            padding: 12px 16px;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
            border-left: 4px solid #667eea;
            border-radius: 0.5rem;
            font-size: 0.9rem;
            color: #4A5568;
            line-height: 1.4;
            box-sizing: border-box;
        }}
        .stats .hover-hint {{
            color: #4A5568;
            border-bottom: 4px solid #FFD700;
            padding-bottom: 1px;
            font-weight: 600;
        }}
        .container {{
            position: relative;
            width: 100%;
            height: calc(100vh - 220px);
            min-height: 600px;
        }}
        #plotDiv {{ width: 100%; height: 100%; }}
        .quarter-overlay {{
            position: absolute;
            top: 15px; left: 15px;
            z-index: 1000;
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px; font-weight: 500;
            letter-spacing: 0.5px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            backdrop-filter: blur(10px);
        }}
{MOBILE_CSS}
    </style>
</head>
<body>
    <div class="controls">
        <button id="prev-btn" type="button">← Previous Quarter</button>
        <div class="time-travel">Time Travel</div>
        <button id="next-btn" type="button">Next Quarter →</button>
    </div>
    <div class="stats" id="stats"></div>
    <div class="container">
        <div class="quarter-overlay" id="quarter-label"></div>
        <div id="plotDiv"></div>
    </div>

    <script>
    const PAYLOADS = {payloads_json};
    const QUARTERS = {quarters_json};
    const QUARTER_LABELS = {quarter_labels_json};

    let currentIndex = QUARTERS.length - 1;  // default: latest quarter

    function getResponsiveLayout() {{
        const w = window.innerWidth;
        let leftMargin, rightMargin, plotHeight, labelFontSize, hoverFontSize;
        if (w <= 480)      {{ leftMargin = rightMargin = 20;  plotHeight = Math.max(380, window.innerHeight * 0.78); labelFontSize = 10; hoverFontSize = 10; }}
        else if (w <= 768) {{ leftMargin = rightMargin = 50;  plotHeight = Math.max(455, window.innerHeight * 0.78); labelFontSize = 10; hoverFontSize = 11; }}
        else if (w <= 1024){{ leftMargin = rightMargin = 100; plotHeight = Math.max(524, window.innerHeight * 0.78); labelFontSize = 14; hoverFontSize = 12; }}
        else               {{ leftMargin = rightMargin = 200; plotHeight = Math.max(524, window.innerHeight * 0.78); labelFontSize = 14; hoverFontSize = 12; }}
        return {{
            plot_bgcolor: 'white', paper_bgcolor: 'white',
            font: {{ color: 'black' }},
            xaxis: {{ showgrid: false, zeroline: false, showticklabels: false, scaleanchor: 'y', scaleratio: 1, fixedrange: true }},
            yaxis: {{ showgrid: false, zeroline: false, showticklabels: false, fixedrange: true }},
            hovermode: 'closest', hoverdistance: 25,
            hoverlabel: {{
                bgcolor: 'rgba(255,255,255,0.96)', bordercolor: 'rgba(160,160,160,0.4)',
                font: {{ family: 'DM Sans, sans-serif', color: '#2c3e50', size: hoverFontSize }}
            }},
            autosize: true, height: plotHeight,
            margin: {{ t: 0, b: 0, l: leftMargin, r: rightMargin }},
            showlegend: false, dragmode: false,
            _meta: {{ labelFontSize, hoverFontSize }}
        }};
    }}

    function getTraces(payload, layout) {{
        const traces = [];
        const labelFontSize = layout._meta.labelFontSize;
        const hoverFontSize = layout._meta.hoverFontSize;

        payload.edge_data.forEach((edge) => {{
            const isTop = edge.is_top;
            traces.push({{
                x: [edge.x0, edge.x1], y: [edge.y0, edge.y1],
                mode: 'lines',
                line: {{
                    width: isTop ? Math.min(8, edge.weight * 0.02) : Math.min(2, edge.weight * 0.015),
                    color: edge.color
                }},
                opacity: isTop ? 0.75 : 0.12,
                hoverinfo: 'skip', showlegend: false, name: 'edge_lines'
            }});
        }});

        const hoverX = [], hoverY = [], hoverTexts = [];
        payload.edge_data.forEach((edge) => {{
            if (!edge.is_top) return;
            const dx = edge.x1 - edge.x0, dy = edge.y1 - edge.y0;
            const edgeLength = Math.sqrt(dx * dx + dy * dy);
            const numPoints = Math.max(5, Math.floor(edgeLength * 20));
            for (let i = 0; i < numPoints; i++) {{
                const t = i / (numPoints - 1);
                hoverX.push(edge.x0 + t * dx);
                hoverY.push(edge.y0 + t * dy);
                hoverTexts.push(edge.hover_text);
            }}
        }});
        if (hoverX.length > 0) {{
            traces.push({{
                x: hoverX, y: hoverY, mode: 'markers',
                marker: {{ size: 12, color: 'rgba(0,0,0,0)', line: {{ width: 0 }} }},
                hoverinfo: 'text', hovertext: hoverTexts,
                hoverlabel: {{
                    bgcolor: 'rgba(255,255,255,0.96)', bordercolor: 'rgba(160,160,160,0.4)',
                    font: {{ family: 'DM Sans, sans-serif', color: '#2c3e50', size: hoverFontSize }}
                }},
                showlegend: false, name: 'edge_hover_points'
            }});
        }}

        const clusters = [...new Set(payload.node_data.map((n) => n.cluster))];
        clusters.forEach((cluster) => {{
            const cn = payload.node_data.filter((n) => n.cluster === cluster);
            if (cn.length === 0) return;
            const sizes = cn.map((n) => window.innerWidth <= 768 ? n.size * 0.8 : n.size);
            traces.push({{
                x: cn.map((n) => n.x), y: cn.map((n) => n.y),
                mode: 'markers',
                marker: {{ size: sizes, color: cn[0].color, opacity: 0.55, line: {{ width: 0.5, color: 'white' }} }},
                hoverinfo: 'skip', showlegend: false, name: `cluster_${{cluster}}`
            }});
        }});

        payload.label_data.forEach((label, idx) => {{
            traces.push({{
                x: [label.x], y: [label.y],
                mode: 'text', text: [`<b>${{label.text}}</b>`],
                textposition: label.textposition || 'middle center',
                textfont: {{ size: labelFontSize, color: label.color, family: 'sans-serif' }},
                showlegend: false, hoverinfo: 'none', name: `label_${{idx}}`
            }});
        }});

        return traces;
    }}

    function render() {{
        const quarter = QUARTERS[currentIndex];
        const label = QUARTER_LABELS[currentIndex];
        const payload = PAYLOADS[quarter];
        const layout = getResponsiveLayout();
        const traces = getTraces(payload, layout);

        document.getElementById('quarter-label').textContent = label;
        document.getElementById('prev-btn').disabled = currentIndex === 0;
        document.getElementById('next-btn').disabled = currentIndex === QUARTERS.length - 1;

        const pct = payload.connected_percentage.toFixed(1);
        document.getElementById('stats').innerHTML = `
            <strong>${{payload.connected_count}} meditation topics</strong> are connected to each other out of <strong>${{payload.total_nodes_q}} total topics</strong>
            (<strong>${{pct}}%</strong>). The bold lines show the <strong>top 10 connections by engagement</strong>; quieter pairings remain as faint threads for context.<br>
            <span class="hover-hint">Hover</span> for detailed topics, themes, and sentiment behind it.`;

        const config = {{
            displayModeBar: false, displaylogo: false, responsive: true,
            scrollZoom: false, doubleClick: false, staticPlot: false
        }};
        Plotly.react('plotDiv', traces, layout, config);
    }}

    document.getElementById('prev-btn').addEventListener('click', () => {{
        if (currentIndex > 0) {{ currentIndex--; render(); }}
    }});
    document.getElementById('next-btn').addEventListener('click', () => {{
        if (currentIndex < QUARTERS.length - 1) {{ currentIndex++; render(); }}
    }});

    let resizeTimeout;
    window.addEventListener('resize', () => {{
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(render, 200);
    }});

    render();
    </script>
</body>
</html>"""


# ----------------------------------------------------------------------------
# Community Weather Report — quarter-keyed weather map with stats bar.
#
# Replicates pages/2_Community_Weather_Report.py (the 2200-line Streamlit page),
# specifically the stats bar + weather map + quarter selector. The below-fold
# Sentiment River Flow Analysis is dropped from v1; the weather map is the
# headline visualization.
# ----------------------------------------------------------------------------

WEATHER_REGION_POSITIONS = {
    'Meditation & Mindfulness':  {'left': '42%', 'top': '52%'},
    'Self-Regulation':           {'left': '42%', 'top': '16%'},
    'Anxiety & Mental Health':   {'left': '16%', 'top': '32%'},
    'Awareness':                 {'left': '17%', 'top': '64%'},
    'Buddhism & Spirituality':   {'left': '63%', 'top': '32%'},
    'Concentration & Flow':      {'left': '66%', 'top': '64%'},
    'Practice, Retreat, & Meta': {'left': '42%', 'top': '84%'},
}

# Weather Report palette derived from canonical primary. `secondary` is +25-RGB
# lifted for the gradient pair; `border` is -30-RGB darkened for the region
# outline. Three-tone structure preserves the weather-map's depth (gradient fill
# + darker rim) instead of collapsing to a single flat color.
WEATHER_TOPIC_COLORS = {
    name: {
        "primary": cfg["color"],
        "secondary": _shift_rgb(cfg["color"], +25),
        "border": _shift_rgb(cfg["color"], -30),
    }
    for name, cfg in TOPIC_MAPPING.items()
}


# Sentiment-tier ladder. Single source for the per-region weather class
# (label/emoji), the climate-aggregate badge, and the JS tooltip color.
# Order: highest threshold first; lookup walks until s >= min.
WEATHER_TIERS = [
    {"min":  0.395, "type": "sunny",         "emoji": "☀️", "label": "Sunny",         "label_long": "Sunny and Positive", "color": "lime"},
    {"min":  0.295, "type": "partly-cloudy", "emoji": "⛅", "label": "Partly Cloudy", "label_long": "Clearing Up",        "color": "yellow"},
    {"min": -0.3,   "type": "cloudy",        "emoji": "☁️", "label": "Cloudy",        "label_long": "Overcast",           "color": "orange"},
    {"min": -0.6,   "type": "rainy",         "emoji": "🌧️","label": "Rainy",         "label_long": "Light Showers",      "color": "orange"},
    {"min": -999.0, "type": "stormy",        "emoji": "⛈️","label": "Stormy",        "label_long": "Storm Warning",      "color": "red"},
]


def _tier_for(s: float) -> dict:
    return next(t for t in WEATHER_TIERS if s >= t["min"])


def _weather_type(s: float) -> str:
    return _tier_for(s)["type"]


_WEATHER_EMOJI = {t["type"]: t["emoji"] for t in WEATHER_TIERS}
_WEATHER_DESC = {t["type"]: t["label_long"] for t in WEATHER_TIERS}


def process_weather_quarter(df_q: pd.DataFrame) -> list[dict]:
    """Replicates pages/2_Community_Weather_Report.py:process_weather_data for one quarter."""
    if df_q.empty:
        return []
    volume_stats = df_q.groupby('cluster_name').size().reset_index(name='volume')
    sentiment_stats = df_q.groupby('cluster_name')['sentiment_score'].mean().reset_index()
    stats = volume_stats.merge(sentiment_stats, on='cluster_name')
    stats['sentiment'] = stats['sentiment_score']

    vol_min, vol_max = stats['volume'].min(), stats['volume'].max()
    if vol_max > vol_min:
        vol_norm = (stats['volume'] - vol_min) / (vol_max - vol_min)
        stats['region_size'] = (vol_norm * 150 + 100).fillna(100).clip(upper=300).astype(int)
    else:
        stats['region_size'] = 100

    # Per-cluster size adjustment. Meditation & Mindfulness has dominant volume,
    # so volume-only sizing made its region visually swallow the rest of the
    # weather map. Trim ~22% so it stays the largest region but composes with
    # neighbors instead of dominating them. Applied across all quarters.
    SIZE_MULTIPLIER = {
        'Meditation & Mindfulness': 0.78,
    }
    stats['region_size'] = stats.apply(
        lambda r: int(r['region_size'] * SIZE_MULTIPLIER.get(r['cluster_name'], 1.0)),
        axis=1,
    )

    out = []
    for rec in stats.to_dict('records'):
        wt = _weather_type(float(rec['sentiment']))
        out.append({
            'cluster_name': rec['cluster_name'],
            'volume': int(rec['volume']),
            'sentiment': float(rec['sentiment']),
            'weather_type': wt,
            'weather_emoji': _WEATHER_EMOJI[wt],
            'weather_desc': _WEATHER_DESC[wt],
            'region_size': int(rec['region_size']),
        })
    return out


def get_top_challenges_per_region(df_q: pd.DataFrame) -> dict[str, list[dict]]:
    """Top-3 pain_topic_label values per cluster_name in one quarter.
    Replicates pages/2_Community_Weather_Report.py:get_top_challenges_by_region. """
    out: dict[str, list[dict]] = {}
    if df_q.empty or 'pain_topic_label' not in df_q.columns:
        return out
    total = len(df_q)
    for cluster, group in df_q.groupby('cluster_name'):
        non_null = group['pain_topic_label'].dropna()
        if non_null.empty:
            out[cluster] = []
            continue
        top3 = non_null.value_counts().head(3)
        out[cluster] = [
            {
                'text': challenge,
                'count': int(count),
                'pct': float((count / total) * 100),
                'severity': 'high' if (count / total) * 100 >= 2.0
                            else ('medium' if (count / total) * 100 >= 1.0 else 'low'),
            }
            for challenge, count in top3.items()
        ]
    return out


def build_weather_report_html() -> str:
    df = pd.read_parquet(ROOT / "precomputed/pain_points_clusters.parquet")
    df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
    df = df.dropna(subset=['sentiment_score', 'cluster_name'])
    # The parquet's `quarter` column is pandas Period; cast to plain "YYYYQN" strings.
    df['quarter'] = df['quarter'].astype(str)

    quarters = ['2024Q1', '2024Q2', '2024Q3', '2024Q4', '2025Q1', '2025Q2']
    per_q: dict[str, dict] = {}

    for q in quarters:
        df_q = df[df['quarter'] == q]
        regions = process_weather_quarter(df_q)
        challenges = get_top_challenges_per_region(df_q)

        sunny   = sum(1 for r in regions if r['weather_type'] == 'sunny')
        cloudy  = sum(1 for r in regions if r['weather_type'] == 'cloudy')
        rainy   = sum(1 for r in regions if r['weather_type'] == 'rainy')
        stormy  = sum(1 for r in regions if r['weather_type'] == 'stormy')
        avg_s   = sum(r['sentiment'] for r in regions) / max(1, len(regions))
        total_v = sum(r['volume'] for r in regions)

        tier = _tier_for(avg_s)

        per_q[q] = {
            'regions':        regions,
            'challenges':     challenges,
            'sunny':          sunny,
            'cloudy':         cloudy,
            'rainy':          rainy,
            'stormy':         stormy,
            'avg_sentiment':  avg_s,
            'total_volume':   total_v,
            'unique_topics':  len({r['cluster_name'] for r in regions}),
            'climate_emoji':  tier["emoji"],
            'climate_label':  tier["label"],
            'sentiment_color': tier["color"],
        }

    # quarterly avg sentiment series for sparkline
    sentiments = [per_q[q]['avg_sentiment'] for q in quarters]

    payload = {
        'quarters':        quarters,
        'per_quarter':     per_q,
        'sentiments':      sentiments,
        'positions':       WEATHER_REGION_POSITIONS,
        'topic_colors':    WEATHER_TOPIC_COLORS,
        'weather_tiers':   [{k: t[k] for k in ("min", "type", "color")} for t in WEATHER_TIERS],
    }
    payload_json = json.dumps(payload)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Community Weather Report — MindSpace OS</title>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script>
      // Read tod=<slot> from the iframe URL (set by StaticChart.astro from the
      // host page's data-time-of-day). If absent (e.g. someone opened this file
      // directly), the CSS fallback in <html> renders the evening palette.
      (function () {{
        var m = location.search.match(/[?&]tod=([^&]+)/);
        if (m) document.documentElement.dataset.timeOfDay = decodeURIComponent(m[1]);
      }})();
    </script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        /* Time-of-day gradient — same five slots as global.css. The chart's own
           script sets data-time-of-day on <html>; we read it here.
           Default (no JS / SSR) falls back to evening, the original chart palette. */
        html {{ --time-gradient: linear-gradient(135deg, #A29BFE 0%, #FD79A8 100%); }}
        html[data-time-of-day="dawn"]      {{ --time-gradient: linear-gradient(135deg, #FF6B6B 0%, #FFB347 100%); }}
        html[data-time-of-day="morning"]   {{ --time-gradient: linear-gradient(135deg, #4ECDC4 0%, #45B7D1 100%); }}
        html[data-time-of-day="afternoon"] {{ --time-gradient: linear-gradient(135deg, #45B7D1 0%, #96CEB4 100%); }}
        html[data-time-of-day="evening"]   {{ --time-gradient: linear-gradient(135deg, #A29BFE 0%, #FD79A8 100%); }}
        html[data-time-of-day="night"]     {{ --time-gradient: linear-gradient(135deg, #6C5CE7 0%, #2D3436 100%); }}

        body {{
            margin: 0; padding: 16px;
            font-family: 'DM Sans', system-ui, -apple-system, Arial, sans-serif;
            background: transparent;
            overflow-x: hidden;
        }}
        .quarter-controls {{
            display: flex; flex-wrap: wrap; gap: 6px; justify-content: center;
            max-width: 1100px; margin: 0 auto 12px;
        }}
        .q-btn {{
            font-family: 'DM Sans', sans-serif;
            font-size: 13px; font-weight: 600; letter-spacing: 0.3px;
            padding: 8px 14px;
            border: 1px solid rgba(102, 126, 234, 0.3);
            background: rgba(255, 255, 255, 0.6);
            color: #4A5568;
            border-radius: 18px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .q-btn:hover {{ border-color: #667eea; color: #667eea; }}
        .q-btn.active {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-color: transparent;
            color: white;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}

        .stats-bar {{
            display: flex; justify-content: space-between; gap: 8px; flex-wrap: wrap;
            background: var(--time-gradient);
            border-radius: 15px;
            padding: 10px 14px;
            margin: 0 auto 8px;
            max-width: 1100px;
            color: white;
        }}
        .stat-card {{
            padding: 7px 12px; min-width: 90px; flex: 1;
            display: flex; flex-direction: column; align-items: center; text-align: center;
            background: rgba(255, 255, 255, 0.08);
            border-radius: 10px;
        }}
        .stat-row {{ display: flex; align-items: center; justify-content: center; }}
        .stat-row.h37 {{ height: 37px; }}
        .stat-row.h21 {{ height: 21px; }}
        .stat-row.h16 {{ height: 16px; }}
        .stat-big   {{ font-size: 24px; font-weight: 700; line-height: 1; }}
        .stat-big.small {{ font-size: 18px; }}
        .stat-mid   {{ font-size: 11px; opacity: 0.9; font-weight: 500; }}
        .stat-small {{ font-size: 9px; opacity: 0.7; }}
        .stat-small.color {{ font-weight: 600; opacity: 0.95; }}

        .weather-map-container {{
            position: relative; width: 100%; height: 568px;
            background: var(--time-gradient);
            border-radius: 20px;
            overflow: hidden;
            margin: 0 auto;
            max-width: 1100px;
        }}

        .weather-region {{
            position: absolute;
            transform: translate(-50%, -50%);
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            color: white;
            font-family: 'DM Sans', sans-serif;
            text-align: center;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border-style: solid;
            border-width: 3px;
        }}

        /* Hover ripple bloom — radial gradient expands from region center on hover.
           Direct port from the original Streamlit page; gives every region consistent
           interactive feedback even when the per-condition animation is subtle. */
        .weather-region::before {{
            content: '';
            position: absolute;
            top: 50%; left: 50%;
            width: 0; height: 0;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,255,255,0.3) 0%, transparent 30%);
            transform: translate(-50%, -50%);
            transition: all 0.6s ease;
            pointer-events: none;
            z-index: -1;
        }}
        .weather-region:hover::before {{
            width: 200%;
            height: 200%;
        }}

        .weather-emoji {{ margin-bottom: 8px; }}
        .region-title {{ font-weight: 800; line-height: 1.2; margin-bottom: 5px; }}
        .weather-desc {{ opacity: 0.9; font-weight: 500; }}

        /* Per-condition animations — strict port of the original Streamlit page.
           Each weather type has its own motion personality. !important so the
           animation always wins over the base .weather-region transform. */
        .sunny {{ animation: sunny-pulse 3s ease-in-out infinite !important; }}
        @keyframes sunny-pulse {{
            0%, 100% {{ transform: translate(-50%, -50%) scale(1); filter: brightness(1) drop-shadow(0 0 15px rgba(255, 215, 0, 0.3)); box-shadow: 0 8px 25px rgba(0,0,0,0.15), 0 0 20px rgba(255, 215, 0, 0.2); }}
            50%      {{ transform: translate(-50%, -50%) scale(1.05); filter: brightness(1.15) drop-shadow(0 0 30px rgba(255, 215, 0, 0.6)); box-shadow: 0 12px 35px rgba(0,0,0,0.25), 0 0 35px rgba(255, 215, 0, 0.4); }}
        }}
        .partly-cloudy {{ animation: hope-breathe 4s ease-in-out infinite !important; }}
        @keyframes hope-breathe {{
            0%, 100% {{ transform: translate(-50%, -50%) translateY(0px) scale(1); filter: brightness(1); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
            25%      {{ transform: translate(-50%, -50%) translateY(-5px) scale(1.02); filter: brightness(1.08); box-shadow: 0 15px 30px rgba(0,0,0,0.2); }}
            75%      {{ transform: translate(-50%, -50%) translateY(3px) scale(0.98); filter: brightness(0.95); box-shadow: 0 5px 20px rgba(0,0,0,0.1); }}
        }}
        .cloudy {{ animation: contemplative-drift 8s ease-in-out infinite !important; }}
        @keyframes contemplative-drift {{
            0%, 100% {{ transform: translate(-50%, -50%) translateX(0px) translateY(0px) scale(1); filter: brightness(0.95); box-shadow: 0 8px 25px rgba(0,0,0,0.15); }}
            25%      {{ transform: translate(-50%, -50%) translateX(3px) translateY(-2px) scale(1.01); filter: brightness(1.02); box-shadow: 0 10px 30px rgba(0,0,0,0.18); }}
            50%      {{ transform: translate(-50%, -50%) translateX(-2px) translateY(4px) scale(0.995); filter: brightness(0.88); box-shadow: 0 6px 20px rgba(0,0,0,0.12); }}
            75%      {{ transform: translate(-50%, -50%) translateX(2px) translateY(2px) scale(1.005); filter: brightness(0.98); box-shadow: 0 9px 28px rgba(0,0,0,0.16); }}
        }}
        .rainy {{ animation: gentle-rain-shake 5s ease-in-out infinite !important; }}
        @keyframes gentle-rain-shake {{
            0%, 100% {{ transform: translate(-50%, -50%) translateX(0px) scale(1); filter: brightness(0.85); box-shadow: 0 6px 20px rgba(0,0,0,0.2); }}
            25%      {{ transform: translate(-50%, -50%) translateX(-2px) scale(0.99); filter: brightness(0.8); box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
            75%      {{ transform: translate(-50%, -50%) translateX(2px) scale(1.01); filter: brightness(0.9); box-shadow: 0 8px 25px rgba(0,0,0,0.25); }}
        }}
        .stormy {{ animation: storm-alert 2s ease-in-out infinite !important; }}
        @keyframes storm-alert {{
            0%, 100% {{ transform: translate(-50%, -50%) scale(1); filter: brightness(0.7) contrast(1.2); box-shadow: 0 8px 25px rgba(0,0,0,0.3), 0 0 15px rgba(255, 0, 0, 0.3); }}
            50%      {{ transform: translate(-50%, -50%) scale(1.03); filter: brightness(1.1) contrast(1.5); box-shadow: 0 12px 35px rgba(0,0,0,0.4), 0 0 25px rgba(255, 0, 0, 0.5); }}
        }}

        .weather-region:hover {{
            transform: translate(-50%, -50%) scale(1.1) !important;
            z-index: 1000 !important;
            filter: brightness(1.05) saturate(1.05) !important;
            box-shadow: 0 6px 16px rgba(0,0,0,0.3), 0 0 10px rgba(255,255,255,0.05), inset 0 0 20px rgba(255,255,255,0.1) !important;
            animation-play-state: paused !important;
            border-width: 4px !important;
        }}
        .weather-region:hover .region-tooltip {{ opacity: 1 !important; transform: translateY(5px) !important; }}
        .weather-region:hover .weather-emoji {{ transform: scale(1.2); }}

        .region-tooltip {{
            position: absolute;
            top: 100%; left: -10px;
            transform: translateY(8px);
            background: rgba(0,0,0,0.85);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.4);
            color: white;
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 10px;
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 2000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            min-width: 180px; max-width: 220px;
            text-align: left; line-height: 1.3;
        }}
        .region-tooltip .t-title {{ font-weight: 700; font-size: 11px; margin-bottom: 4px; }}
        .region-tooltip .t-row {{ font-size: 9px; opacity: 0.9; }}
        .region-tooltip .t-row strong {{ font-weight: 700; opacity: 1; }}

        .weather-legend {{
            position: absolute;
            top: 15px; right: 20px;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(15px);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 15px;
            padding: 12px;
            color: white;
            font-family: 'DM Sans', sans-serif;
            font-size: 11px;
            min-width: 140px; max-width: 180px;
            z-index: 100;
        }}
        .weather-legend .legend-title {{ font-size: 12px; font-weight: 800; margin-bottom: 6px; }}
        .legend-item {{ margin-bottom: 4px; display: flex; align-items: center; gap: 8px; line-height: 1.1; }}
        .legend-emoji {{ font-size: 14px; flex-shrink: 0; }}
        .legend-text {{ flex: 1; font-size: 10px; font-weight: 600; }}
        .legend-footer {{ margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 9px; }}

        @media (prefers-reduced-motion: reduce) {{
            .sunny, .partly-cloudy, .cloudy, .rainy, .stormy {{ animation: none !important; }}
        }}

        /* Sentiment River Flow Analysis (below the weather map) */
        .river-flow {{
            max-width: 1100px;
            margin: 24px auto 0;
            padding: 0;
        }}
        /* River-flow header — quiet editorial sub-chapter.
           No card chrome (no dark-glass background, no border, no blur) so it
           doesn't compete with the weather map above. White text reads on the
           page's purple gradient; the trend pill carries the colored signal. */
        .river-header {{
            text-align: center;
            margin: 28px auto 18px;
            padding: 0 18px;
            max-width: 680px;
            color: rgba(255, 255, 255, 0.95);
        }}
        .river-title {{
            font-size: 14px; font-weight: 600;
            letter-spacing: 0.02em;
            color: rgba(255, 255, 255, 0.95);
            font-family: 'DM Sans', sans-serif;
            margin: 0 0 6px;
            line-height: 1.3;
        }}
        .trend-summary {{
            display: inline-flex; align-items: center; gap: 8px;
            padding: 4px 10px;
            border-radius: 999px;
            border: 1px solid rgba(255, 255, 255, 0.18);
            font-size: 11px; font-weight: 600;
            letter-spacing: 0.02em;
            color: rgba(255, 255, 255, 0.95) !important;
            background: rgba(255, 255, 255, 0.10);
        }}
        .trend-dot {{
            width: 7px; height: 7px;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.06);
            flex-shrink: 0;
        }}
        /* Cards scroll area — visible window of one row (two cards side-by-side),
           rest scrolls. Cards are denser now (see .topic-card padding/spacing
           below), so a row of 2 cards is ~340px tall. Cap at 360px so the user
           sees one full row and a tiny hint of the next, signaling scroll. */
        .topic-grid-scroll {{
            max-height: 360px;
            overflow-y: auto;
            padding: 4px 6px 16px;
            margin: 0 -6px;
            mask-image: linear-gradient(to bottom, black 0%, black calc(100% - 24px), transparent 100%);
            -webkit-mask-image: linear-gradient(to bottom, black 0%, black calc(100% - 24px), transparent 100%);
        }}
        .topic-grid-scroll::-webkit-scrollbar {{ width: 8px; }}
        .topic-grid-scroll::-webkit-scrollbar-track {{ background: transparent; }}
        .topic-grid-scroll::-webkit-scrollbar-thumb {{
            background: rgba(15, 23, 42, 0.18);
            border-radius: 4px;
        }}
        .topic-grid-scroll::-webkit-scrollbar-thumb:hover {{ background: rgba(15, 23, 42, 0.32); }}

        /* Force exactly 2 columns at every width — user explicitly asked for it.
           !important defeats any specificity battle. minmax(0, 1fr) lets cards
           shrink below their content size if the iframe is narrow. No media-
           query collapse. */
        .topic-grid {{
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 14px;
            margin-top: 6px;
            width: 100%;
        }}
        @media (max-width: 768px) {{
            .topic-grid {{
                grid-template-columns: 1fr !important;
            }}
        }}
        .topic-card {{
            min-width: 0;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-top: 4px solid var(--cluster-color, #94a3b8);
            border-radius: 12px;
            padding: 12px 14px 12px;
            box-shadow: 0 3px 10px rgba(15, 23, 42, 0.07);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        .topic-card:hover {{
            transform: translateY(-1px);
            box-shadow: 0 8px 22px rgba(15, 23, 42, 0.12);
        }}
        .topic-row {{
            display: flex; align-items: center; gap: 8px;
            margin-bottom: 6px;
        }}
        .topic-emoji {{ font-size: 18px; }}
        .topic-name {{
            font-weight: 700; font-size: 14px;
            color: #1e293b;
            font-family: 'DM Sans', sans-serif;
            flex: 1;
            line-height: 1.2;
        }}
        .topic-change {{
            font-size: 10px; font-weight: 700;
            padding: 2px 7px; border-radius: 8px;
            white-space: nowrap;
        }}
        .change-up   {{ background: rgba(16, 185, 129, 0.12); color: #047857; }}
        .change-down {{ background: rgba(249, 115, 22, 0.12); color: #c2410c; }}
        .change-flat {{ background: rgba(100, 116, 139, 0.12); color: #475569; }}

        .topic-meta {{
            display: flex; align-items: center; gap: 10px;
            margin-bottom: 8px;
        }}
        .meta-sentiment {{
            font-size: 22px; font-weight: 800;
            color: var(--cluster-color, #1e293b);
            font-family: 'DM Sans', sans-serif;
            line-height: 1;
            letter-spacing: -0.01em;
        }}
        .meta-volume {{
            display: flex; flex-direction: column;
            font-size: 9px; color: #64748b;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            font-weight: 600;
            line-height: 1.15;
        }}
        .meta-volume strong {{
            color: #1e293b; font-size: 12px;
            letter-spacing: 0; text-transform: none;
            font-weight: 700;
        }}
        .meta-weather-pill {{
            margin-left: auto;
            padding: 3px 9px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 600;
            background: var(--cluster-tint, rgba(148,163,184,0.14));
            color: var(--cluster-color, #475569);
            letter-spacing: 0.02em;
            white-space: nowrap;
        }}

        .challenge-list {{
            display: flex; flex-direction: column; gap: 6px;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid #f1f5f9;
        }}
        .challenge-list-title {{
            font-size: 10px; font-weight: 600;
            color: #475569;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            margin-bottom: 1px;
        }}
        .challenge {{
            display: flex; align-items: flex-start; gap: 8px;
            font-size: 12px;
            color: #1e293b;
            line-height: 1.4;
        }}
        .severity-dot {{
            display: inline-block;
            width: 6px; height: 6px;
            border-radius: 50%;
            margin-top: 6px;
            flex-shrink: 0;
        }}
        .severity-dot.high   {{ background: #ef4444; }}
        .severity-dot.medium {{ background: #f97316; }}
        .severity-dot.low    {{ background: #94a3b8; }}
        .challenge-text {{ flex: 1; }}
        .challenge-stats {{
            font-size: 9px;
            color: #94a3b8;
            margin-top: 1px;
            letter-spacing: 0.02em;
        }}
        .challenge-empty {{
            font-size: 11px;
            color: #94a3b8;
            font-style: italic;
            padding: 4px 0;
        }}
{MOBILE_CSS}
    </style>
</head>
<body>
    <div class="quarter-controls" id="q-controls"></div>
    <div class="stats-bar" id="stats-bar"></div>
    <div class="weather-map-container" id="weather-map">
        <div id="weather-regions"></div>
        <div class="weather-legend">
            <div class="legend-title">Weather Legend</div>
            <div class="legend-item"><span class="legend-emoji">☀️</span><span class="legend-text">Sunny and Positive (0.4+)</span></div>
            <div class="legend-item"><span class="legend-emoji">⛅</span><span class="legend-text">Clearing Up (0.3+)</span></div>
            <div class="legend-item"><span class="legend-emoji">☁️</span><span class="legend-text">Overcast (-0.3/0.3)</span></div>
            <div class="legend-item"><span class="legend-emoji">🌧️</span><span class="legend-text">Light Showers (-0.6)</span></div>
            <div class="legend-item"><span class="legend-emoji">⛈️</span><span class="legend-text">Storm Warning (-0.6+)</span></div>
            <div class="legend-footer">
                <strong id="legend-q">2025Q2</strong><br>
                <strong>Region Size = Discussion Volume</strong><br><span style="color: #ffffff; border-bottom: 4px solid #FFD700; padding-bottom: 1px; font-weight: 700;">Hover</span> to discover details.
            </div>
        </div>
    </div>

    <div class="river-flow" id="river-flow"></div>

    <script>
    const PAYLOAD = {payload_json};
    const QUARTERS = PAYLOAD.quarters;
    const PER_Q = PAYLOAD.per_quarter;
    const SENTIMENTS = PAYLOAD.sentiments;
    const POSITIONS = PAYLOAD.positions;
    const TOPIC_COLORS = PAYLOAD.topic_colors;

    let currentIndex = QUARTERS.length - 1;  // default 2025Q2

    function hexToRgba(hex, a) {{
        const h = hex.replace('#', '');
        const r = parseInt(h.substring(0,2), 16);
        const g = parseInt(h.substring(2,4), 16);
        const b = parseInt(h.substring(4,6), 16);
        return `rgba(${{r}}, ${{g}}, ${{b}}, ${{a}})`;
    }}

    // Cardinal-spline sparkline path. Same approach as the Streamlit page.
    function sparklinePath(values, width, height, tension) {{
        if (values.length < 2) return `M 0,${{height/2}} L ${{width}},${{height/2}}`;
        const minV = Math.min(...values), maxV = Math.max(...values);
        const norm = maxV > minV ? values.map(v => (v - minV) / (maxV - minV)) : values.map(_ => 0.5);
        const points = norm.map((v, i) => [i / (values.length - 1) * width, height - v * height]);
        if (points.length < 3) return `M ${{points[0][0]}},${{points[0][1]}} L ${{points[1][0]}},${{points[1][1]}}`;

        function cardinal(p0, p1, p2, p3, t) {{
            const t2 = t*t, t3 = t2*t;
            const c0 = -tension*t3 + 2*tension*t2 - tension*t;
            const c1 = (2-tension)*t3 + (tension-3)*t2 + 1;
            const c2 = (tension-2)*t3 + (3-2*tension)*t2 + tension*t;
            const c3 = tension*t3 - tension*t2;
            return [c0*p0[0]+c1*p1[0]+c2*p2[0]+c3*p3[0], c0*p0[1]+c1*p1[1]+c2*p2[1]+c3*p3[1]];
        }}
        let d = `M ${{points[0][0].toFixed(2)}},${{points[0][1].toFixed(2)}}`;
        const seg = 8;
        for (let i = 0; i < points.length - 1; i++) {{
            const p0 = points[Math.max(0,i-1)], p1 = points[i], p2 = points[i+1], p3 = points[Math.min(points.length-1,i+2)];
            for (let j = 1; j <= seg; j++) {{
                const t = j/seg;
                const [x,y] = cardinal(p0,p1,p2,p3,t);
                d += ` L ${{x.toFixed(2)}},${{y.toFixed(2)}}`;
            }}
        }}
        return d;
    }}

    function trendWord(s) {{
        if (s > 0.5) return 'Thriving';
        if (s > 0)   return 'Growing';
        if (s > -0.5) return 'Stable';
        return 'Needs';
    }}

    function renderControls() {{
        const c = document.getElementById('q-controls');
        c.innerHTML = QUARTERS.map((q, i) => `<button class="q-btn${{i === currentIndex ? ' active' : ''}}" data-i="${{i}}">${{q}}</button>`).join('');
        c.querySelectorAll('.q-btn').forEach((b) => {{
            b.addEventListener('click', () => {{
                currentIndex = parseInt(b.getAttribute('data-i'), 10);
                renderControls();
                renderStats();
                renderMap();
                renderRiverFlow();
            }});
        }});
    }}

    function renderStats() {{
        const q = QUARTERS[currentIndex];
        const d = PER_Q[q];

        // Growth vs previous quarter
        let growth = q;
        if (currentIndex > 0) {{
            const prev = PER_Q[QUARTERS[currentIndex - 1]];
            if (prev.total_volume > 0) {{
                const pct = ((d.total_volume - prev.total_volume) / prev.total_volume) * 100;
                growth = (pct >= 0 ? '+' : '') + pct.toFixed(0) + '% QoQ';
            }}
        }}

        const path = sparklinePath(SENTIMENTS, 65, 22, 0.4);
        const minS = Math.min(...SENTIMENTS), maxS = Math.max(...SENTIMENTS);
        const yNorm = maxS > minS ? (SENTIMENTS[currentIndex] - minS) / (maxS - minS) : 0.5;
        const cx = (currentIndex / (SENTIMENTS.length - 1)) * 65;
        const cy = 22 - yNorm * 22;

        document.getElementById('stats-bar').innerHTML = `
            <div class="stat-card">
                <div class="stat-row h37"><div class="stat-big">${{d.total_volume.toLocaleString()}}</div></div>
                <div class="stat-row h21"><div class="stat-mid">Discussions</div></div>
                <div class="stat-row h16"><div class="stat-small">${{growth}}</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-row h37"><div class="stat-big">${{d.unique_topics}}</div></div>
                <div class="stat-row h21"><div class="stat-mid">Regions</div></div>
                <div class="stat-row h16"><div class="stat-small">Main Topics</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-row h37"><div class="stat-big">${{d.sunny}}</div></div>
                <div class="stat-row h21"><div class="stat-mid">Sunny</div></div>
                <div class="stat-row h16"><div class="stat-small">vs ${{d.cloudy}} cloudy</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-row h37"><div class="stat-big small">${{d.climate_label}}</div></div>
                <div class="stat-row h21"><div class="stat-mid">Climate</div></div>
                <div class="stat-row h16"><div class="stat-small color" style="color: ${{d.sentiment_color}}">${{(d.avg_sentiment >= 0 ? '+' : '') + d.avg_sentiment.toFixed(2)}}</div></div>
            </div>
            <div class="stat-card">
                <div class="stat-row h37">
                    <svg width="65" height="22" style="overflow: visible;">
                        <path d="${{path}}" stroke="rgba(255,255,255,0.9)" stroke-width="1.8" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
                        <circle cx="${{cx}}" cy="${{cy}}" r="3" fill="rgba(255,255,255,1)" stroke="rgba(255,255,255,0.3)" stroke-width="5"/>
                    </svg>
                </div>
                <div class="stat-row h21"><div class="stat-mid">Trend</div></div>
                <div class="stat-row h16"><div class="stat-small">Sentiment</div></div>
            </div>`;
    }}

    function renderMap() {{
        const q = QUARTERS[currentIndex];
        const d = PER_Q[q];
        const totalV = d.total_volume || 1;
        document.getElementById('legend-q').textContent = q;

        const html = d.regions.map((r) => {{
            const pos = POSITIONS[r.cluster_name] || {{ left: '50%', top: '50%' }};
            const colors = TOPIC_COLORS[r.cluster_name] || {{ primary: '#87CEEB', secondary: '#4682B4', border: '#4682B4' }};
            // Meditation & Mindfulness consistently has the highest volume and renders
            // big enough to crowd / overlap neighbors. Scale it to 85% so the satellites
            // around it have breathing room without losing the volume hierarchy.
            const meditationFactor = r.cluster_name === 'Meditation & Mindfulness' ? 0.85 : 1.0;
            const sizePx = Math.round(r.region_size * 1.2 * meditationFactor);
            const volPct = ((r.volume / totalV) * 100).toFixed(1);

            // Format multi-word names onto two lines
            const words = r.cluster_name.split(' ');
            let formatted = r.cluster_name;
            if (words.length > 2) {{
                const mid = Math.floor(words.length / 2);
                formatted = words.slice(0, mid).join(' ') + '<br>' + words.slice(mid).join(' ');
            }}

            // Smart tooltip positioning (bottom-aligned for Practice/Meta, right-aligned for far-right regions)
            let tooltipStyle = '';
            if (r.cluster_name.includes('Practice') && r.cluster_name.includes('Meta')) {{
                tooltipStyle = 'top: auto; bottom: 100%; left: 20px; transform: translateY(-8px);';
            }} else if (parseFloat(pos.left.replace('%', '')) > 70) {{
                tooltipStyle = 'left: auto; right: -10px;';
            }}

            const sentColor = (PAYLOAD.weather_tiers.find(t => r.sentiment >= t.min) || {{color: 'orange'}}).color;

            return `
                <div class="weather-region ${{r.weather_type}}"
                     style="left: ${{pos.left}}; top: ${{pos.top}};
                            width: ${{sizePx}}px; height: ${{Math.round(sizePx * 0.7)}}px;
                            background: linear-gradient(135deg, ${{colors.primary}}, ${{colors.secondary}});
                            border-color: ${{colors.border}};">
                    <div class="weather-emoji" style="font-size: ${{Math.min(24, Math.floor(sizePx/8))}}px;">${{r.weather_emoji}}</div>
                    <div class="region-title" style="font-size: ${{Math.min(14, Math.floor(sizePx/12))}}px;">${{formatted}}</div>
                    <div class="weather-desc" style="font-size: ${{Math.min(9, Math.floor(sizePx/18))}}px;">${{r.weather_desc}}</div>
                    <div class="region-tooltip" style="${{tooltipStyle}}">
                        <div class="t-title">${{r.weather_emoji}} ${{r.cluster_name}}</div>
                        <div class="t-row">Sentiment: <strong style="color: ${{sentColor}};">${{r.sentiment.toFixed(2)}}</strong></div>
                        <div class="t-row">Volume: <strong>${{volPct}}%</strong></div>
                        <div class="t-row">Trend: <strong>${{trendWord(r.sentiment)}}</strong></div>
                    </div>
                </div>`;
        }}).join('');

        document.getElementById('weather-regions').innerHTML = html;
    }}

    function renderRiverFlow() {{
        const q = QUARTERS[currentIndex];
        const d = PER_Q[q];
        const prev = currentIndex > 0 ? PER_Q[QUARTERS[currentIndex - 1]] : null;
        const isFirst = currentIndex === 0;

        // Header: trend summary against the previous quarter (or baseline for Q1).
        // Trend badge — slim white-on-glass pill. The CSS class .trend-summary
        // owns the styling now; only a small accent dot inside the pill carries
        // the up/steady/down color signal so the text stays consistently white.
        let trendBadge;
        if (isFirst) {{
            trendBadge = `<span class="trend-summary">
                <span class="trend-dot" style="background: rgba(255,255,255,0.55);"></span>
                Establishing baseline · QoQ trends start next quarter
            </span>`;
        }} else {{
            const curBy = Object.fromEntries(d.regions.map(r => [r.cluster_name, r]));
            const prevBy = Object.fromEntries(prev.regions.map(r => [r.cluster_name, r]));
            const allClusters = new Set([...Object.keys(curBy), ...Object.keys(prevBy)]);
            let totalChange = 0, n = 0;
            allClusters.forEach((c) => {{
                const a = (curBy[c] && curBy[c].sentiment) || 0;
                const b = (prevBy[c] && prevBy[c].sentiment) || 0;
                totalChange += (a - b);
                n++;
            }});
            const avg = n > 0 ? totalChange / n : 0;
            let label, dotColor;
            if (avg > 0.02)        {{ label = `Rising ${{avg >= 0 ? '+' : ''}}${{avg.toFixed(2)}}`; dotColor = '#5BE7A9'; }}
            else if (avg < -0.02)  {{ label = `Declining ${{avg.toFixed(2)}}`; dotColor = '#FFB07A'; }}
            else                   {{ label = `Steady ${{avg >= 0 ? '+' : ''}}${{avg.toFixed(2)}}`; dotColor = 'rgba(255,255,255,0.55)'; }}
            trendBadge = `<span class="trend-summary">
                <span class="trend-dot" style="background: ${{dotColor}};"></span>
                ${{label}} vs ${{QUARTERS[currentIndex - 1]}}
            </span>`;
        }}

        // One card per topic.
        const prevByName = prev ? Object.fromEntries(prev.regions.map(r => [r.cluster_name, r])) : {{}};
        const cardsHtml = d.regions
            .slice()
            .sort((a, b) => b.volume - a.volume)
            .map((r) => {{
                const prevR = prevByName[r.cluster_name];
                let changeBadge = '<span class="topic-change change-flat">baseline</span>';
                if (prevR) {{
                    const delta = r.sentiment - prevR.sentiment;
                    if (delta > 0.02) changeBadge = `<span class="topic-change change-up">↑ +${{delta.toFixed(2)}}</span>`;
                    else if (delta < -0.02) changeBadge = `<span class="topic-change change-down">↓ ${{delta.toFixed(2)}}</span>`;
                    else changeBadge = `<span class="topic-change change-flat">→ ${{delta >= 0 ? '+' : ''}}${{delta.toFixed(2)}}</span>`;
                }}

                const challenges = (d.challenges && d.challenges[r.cluster_name]) || [];
                const challengesHtml = challenges.length === 0
                    ? `<div class="challenge-empty">No significant challenges detected</div>`
                    : challenges.map((c) => `
                        <div class="challenge">
                            <span class="severity-dot ${{c.severity}}"></span>
                            <div class="challenge-text">
                                ${{c.text}}
                                <div class="challenge-stats">${{c.pct.toFixed(1)}}% of discussions · ${{c.severity}} intensity</div>
                            </div>
                        </div>`).join('');

                // Use the weather map's topic color (saturated palette, see WEATHER_TOPIC_COLORS
                // in the build script) so the card top-bar matches the region color visitors
                // just saw on the map above. This is within-page coherence.
                const tc = TOPIC_COLORS[r.cluster_name] || {{ primary: '#475569', border: '#475569' }};
                const clusterColor = tc.primary;
                const clusterTint = hexToRgba(clusterColor, 0.14);
                const sentimentLabel = (r.sentiment >= 0 ? '+' : '') + r.sentiment.toFixed(2);
                const totalQV = d.total_volume || 1;
                const volPct = ((r.volume / totalQV) * 100).toFixed(1);

                return `
                    <div class="topic-card" style="--cluster-color: ${{clusterColor}}; --cluster-tint: ${{clusterTint}};">
                        <div class="topic-row">
                            <span class="topic-emoji">${{r.weather_emoji}}</span>
                            <span class="topic-name">${{r.cluster_name}}</span>
                            ${{changeBadge}}
                        </div>
                        <div class="topic-meta">
                            <span class="meta-sentiment">${{sentimentLabel}}</span>
                            <span class="meta-volume">vol<strong>${{volPct}}%</strong></span>
                            <span class="meta-weather-pill">${{r.weather_desc}}</span>
                        </div>
                        <div class="challenge-list">
                            <div class="challenge-list-title">Active challenges</div>
                            ${{challengesHtml}}
                        </div>
                    </div>`;
            }}).join('');

        document.getElementById('river-flow').innerHTML = `
            <div class="river-header">
                <h3 class="river-title">Regional Topic Trends and Active Challenges – ${{q}}</h3>
                <div>${{trendBadge}}</div>
            </div>
            <div class="topic-grid-scroll"><div class="topic-grid">${{cardsHtml}}</div></div>`;
    }}

    renderControls();
    renderStats();
    renderMap();
    renderRiverFlow();
    </script>
</body>
</html>"""


# ----------------------------------------------------------------------------
# Build entry point
# ----------------------------------------------------------------------------

def main() -> None:
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)

    # Phase 3a: emotion-pulse split into shell HTML + data JSON. Shell
    # paints a skeleton instantly; the JSON loads in parallel and hydrates
    # via init(). Cuts first-paint LCP from ~2s to ~400ms.
    emotion_pulse_payload = build_emotion_pulse_payload()
    (CHARTS_DIR / "emotion-pulse-data.json").write_text(json.dumps(emotion_pulse_payload))
    data_kb = (CHARTS_DIR / "emotion-pulse-data.json").stat().st_size / 1024
    print(f"  ✓ {CHARTS_DIR / 'emotion-pulse-data.json'}  ({data_kb:.0f} KB)")

    emotion_pulse_html = build_emotion_pulse_shell()
    (CHARTS_DIR / "emotion-pulse.html").write_text(emotion_pulse_html)
    size_kb = len(emotion_pulse_html.encode()) / 1024
    print(f"  ✓ {CHARTS_DIR / 'emotion-pulse.html'}  ({size_kb:.0f} KB shell)")

    community_dynamics_html = build_community_dynamics_html()
    (CHARTS_DIR / "community-dynamics.html").write_text(community_dynamics_html)
    size_kb = len(community_dynamics_html.encode()) / 1024
    print(f"  ✓ {CHARTS_DIR / 'community-dynamics.html'}  ({size_kb:.0f} KB)")

    inner_life_currents_html = build_inner_life_currents_html()
    (CHARTS_DIR / "inner-life-currents.html").write_text(inner_life_currents_html)
    size_kb = len(inner_life_currents_html.encode()) / 1024
    print(f"  ✓ {CHARTS_DIR / 'inner-life-currents.html'}  ({size_kb:.0f} KB)")

    weather_report_html = build_weather_report_html()
    (CHARTS_DIR / "community-weather-report.html").write_text(weather_report_html)
    size_kb = len(weather_report_html.encode()) / 1024
    print(f"  ✓ {CHARTS_DIR / 'community-weather-report.html'}  ({size_kb:.0f} KB)")

    print("\nCharts built. These pages no longer rely on Streamlit at runtime.")
    print("Re-run on data changes (same cadence as scripts/build_precomputed.py).")


if __name__ == "__main__":
    main()
