"""Build-time precomputation for MindSpace OS.

Produces artifacts under ``precomputed/`` that pages load directly, so the
runtime code doesn't rebuild figures or reformat hover text on every cold
start. Rerun this any time the source parquets under ``precomputed/``
change (or the wrap rules below, or the Sankey palette).

    python3 scripts/build_precomputed.py

Outputs:
- ``precomputed/emotion_clusters_slim.parquet`` — the 4 columns the
  Emotion Pulse page actually reads, with ``hover_text`` already wrapped.
- ``precomputed/figures/themes_sankey.json`` — full Plotly figure JSON
  for the Inner Life Themes Sankey, ready for ``plotly.io.from_json``.
"""
from __future__ import annotations

import json
import pathlib
import re

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import hex_to_rgb

REPO = pathlib.Path(__file__).resolve().parent.parent
PRECOMPUTED = REPO / "precomputed"
FIGURES = PRECOMPUTED / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------------------------------
# Emotion Pulse slim parquet
# --------------------------------------------------------------------------

USER_RADAR_EMOTIONS = [
    "gratitude", "joy", "caring", "love",
    "confusion", "fear", "sadness", "grief",
]
EMOTION_COLUMNS = (
    ["umap_x", "umap_y", "hover_text", "archetype_label"] + USER_RADAR_EMOTIONS
)
WRAP_WIDTH = 75


def _wrap_text_content(text: str, max_length: int = WRAP_WIDTH) -> list[str]:
    text = " ".join(text.split())
    if len(text) <= max_length:
        return [text]
    words = text.split()
    lines, current, cur_len = [], [], 0
    for word in words:
        space = 1 if current else 0
        if cur_len + space + len(word) > max_length:
            if current:
                lines.append(" ".join(current))
                current = [word]
                cur_len = len(word)
            else:
                lines.append(word)
                cur_len = 0
        else:
            current.append(word)
            cur_len += space + len(word)
    if current:
        lines.append(" ".join(current))
    # Opportunistically combine very-short adjacent lines.
    combined: list[str] = []
    i = 0
    while i < len(lines):
        cur = lines[i]
        if i + 1 < len(lines):
            nxt = lines[i + 1]
            merged = cur + " " + nxt
            if (
                len(merged) <= max_length
                and len(cur.split()) <= 4
                and len(nxt.split()) <= 4
            ):
                combined.append(merged)
                i += 2
                continue
        combined.append(cur)
        i += 1
    return combined


_EMOTION_PERCENT_RE = re.compile(r"(\w+:\s*\d+%)")


def _wrap_emotions_line(line: str) -> list[str]:
    line = " ".join(line.split())
    emotions = _EMOTION_PERCENT_RE.findall(line)
    if not emotions:
        return _wrap_text_content(line)
    out: list[str] = []
    cur = "Top Emotions: "
    for em in emotions:
        if len(cur + em + " ") > WRAP_WIDTH:
            if cur.strip() != "Top Emotions:":
                out.append(cur.strip())
                cur = em + " "
            else:
                cur += em + " "
        else:
            cur += em + " "
    if cur.strip():
        out.append(cur.strip())
    return out


def wrap_hover_text(text: object) -> str:
    """Same wrap rules as the former runtime code in pages/0_Emotion_Pulse.py."""
    if pd.isna(text):
        return ""
    text = str(text).strip()
    text = (
        text.replace("\n", " ")
        .replace("\r", " ")
        .replace("\t", " ")
        .replace(" ", " ")
        .replace(" ", " ")
        .replace("​", "")
    )
    text = " ".join(text.split())
    wrapped: list[str] = []
    for line in text.split("<br>"):
        line = line.strip()
        if not line:
            continue
        if line.startswith("Top Emotions:"):
            if len(line) <= WRAP_WIDTH:
                wrapped.append(line)
            else:
                wrapped.extend(_wrap_emotions_line(line))
        else:
            wrapped.extend(_wrap_text_content(line))
    return "<br>".join(wrapped)


def build_emotion_slim() -> None:
    src = PRECOMPUTED / "emotion_clusters.parquet"
    dst = PRECOMPUTED / "emotion_clusters_slim.parquet"
    df = pd.read_parquet(src, columns=EMOTION_COLUMNS)
    df = df.copy()
    # Rename carried over from the old page name; the source parquet was
    # generated before the "Emotional Pulse" -> "Emotion Pulse" rename.
    df["hover_text"] = df["hover_text"].str.replace(
        "Emotional Pulse:", "Emotion Pulse:", regex=False
    )
    df["hover_text"] = df["hover_text"].map(wrap_hover_text)
    # 8 GoEmotions probabilities feed the per-point radar inset on the
    # Emotion Pulse page. float32 is ample precision for radial plotting
    # and keeps the parquet ~90 KB lighter than the float64 default.
    for col in USER_RADAR_EMOTIONS:
        df[col] = df[col].astype("float32")
    df.to_parquet(dst, compression="zstd", index=False)
    print(f"  wrote {dst.relative_to(REPO)}  rows={len(df):,}  size={dst.stat().st_size/1024:.1f} KB")


# --------------------------------------------------------------------------
# Inner Life Themes (Sankey) figure JSON
# --------------------------------------------------------------------------

COLOR_FAMILIES = {
    "Meditation & Mindfulness": ["#00FFFF", "#87FDFC"],
    "Self-Regulation": ["#0091EA", "#2196F3"],
    "Anxiety & Mental Health": ["#00E676", "#4CAF50"],
    "Awareness": ["#CDDC39", "#D4E157"],
    "Buddhism & Spirituality": ["#FFD600", "#FFD700"],
    "Concentration & Flow": ["#FF6D00", "#FF8C00"],
    "Practice, Retreat & Meta": ["#F50057", "#F50057"],
}
TOPIC_COLOR_ORDER = [
    "#00E5FF", "#0091EA", "#00E676", "#CDDC39",
    "#FFD600", "#FF6D00", "#F50057",
]
THEME_ASSIGNMENTS = {
    "self-awareness": "Awareness",
    "jhanas": "Buddhism & Spirituality",
    "metta": "Buddhism & Spirituality",
    "practice updates": "Practice, Retreat & Meta",
}
VIVID_PALETTE = [
    "#00BFFF", "#42A5F5", "#66BB6A", "#81C784", "#ADFF2F",
    "#FFEB3B", "#FFA500", "#FF9800", "#FF80AB", "#FFB6C1",
    "#40E0D0", "#00CED1", "#87CEFA", "#B0E0E6", "#98FB98",
    "#FFE4B5", "#FFDAB9", "#FFC0CB", "#DA70D6", "#9370DB",
]


def _format_number(n: float) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def build_sankey_figure(df: pd.DataFrame) -> go.Figure:
    filtered = df[df["count"] > 0].copy()
    if filtered.empty:
        return go.Figure().add_annotation(text="No data to display")

    theme_vol = filtered.groupby("theme")["count"].sum().sort_values(ascending=False)
    topic_vol = filtered.groupby("cluster_name")["count"].sum().sort_values(ascending=False)
    themes = theme_vol.index.tolist()
    topics = topic_vol.index.tolist()
    node_labels = themes + topics
    theme_index = {t: i for i, t in enumerate(themes)}
    topic_index = {t: i + len(themes) for i, t in enumerate(topics)}

    total = filtered["count"].sum()

    theme_hover = [
        f"<b style='font-size: 16px; color: #2c3e50'>{t}</b><br>"
        f"Total: <b>{_format_number(theme_vol[t])}</b><br>"
        f"Global Share: <b>{theme_vol[t]/total*100:.1f}%</b><br>"
        for t in themes
    ]

    grouped = filtered.groupby("cluster_name")
    primary_idx = grouped["count"].idxmax()
    primary_frame = filtered.loc[primary_idx, ["cluster_name", "theme", "count"]].set_index("cluster_name")
    connected = grouped["theme"].nunique()

    topic_hover = [
        (
            f"<b style='font-size: 16px; color: #2c3e50'>{t}</b><br>"
            f"Mentions: <b>{_format_number(topic_vol[t])}</b><br>"
            f"Global Share: <b>{topic_vol[t]/total*100:.1f}%</b><br>"
            f"Primary Theme: <b>{primary_frame.loc[t, 'theme']}</b><br>"
            f"Top Count: <b>{_format_number(primary_frame.loc[t, 'count'])}</b><br>"
            f"Themes: <b>{int(connected.loc[t])}</b>"
        )
        for t in topics
    ]

    src, tgt, val, link_hover = [], [], [], []
    for r in filtered.to_dict("records"):
        src.append(theme_index[r["theme"]])
        tgt.append(topic_index[r["cluster_name"]])
        val.append(r["count"])
        flow_pct = r["count"] / total * 100
        topic_pct = r["count"] / topic_vol[r["cluster_name"]] * 100
        link_hover.append(
            f"<b style='font-size: 15px; color: #2c3e50'>{r['theme']} → {r['cluster_name']}</b><br>"
            f"Count: <b>{_format_number(r['count'])}</b><br>"
            f"Global Share: <b>{flow_pct:.1f}%</b><br>"
            f"Topic Share: <b>{topic_pct:.1f}%</b>"
        )

    # Node colors — same heuristic as the former page code.
    node_colors: list[str] = []
    theme_map: dict[str, str] = {}
    vivid_idx = 0
    for t in themes:
        tl = t.lower()
        if tl == "mindfulness":
            c = COLOR_FAMILIES["Meditation & Mindfulness"][1]
            node_colors.append(c)
            theme_map[t] = c
            continue
        fam_override = THEME_ASSIGNMENTS.get(tl)
        if fam_override:
            c = COLOR_FAMILIES[fam_override][vivid_idx % 2]
            node_colors.append(c)
            theme_map[t] = c
            vivid_idx += 1
            continue
        matched = False
        for fam, pair in COLOR_FAMILIES.items():
            if tl in fam.lower():
                node_colors.append(pair[0])
                theme_map[t] = pair[0]
                matched = True
                break
        if not matched:
            c = VIVID_PALETTE[vivid_idx % len(VIVID_PALETTE)]
            node_colors.append(c)
            theme_map[t] = c
            vivid_idx += 1

    for i, _ in enumerate(topics):
        node_colors.append(TOPIC_COLOR_ORDER[i % len(TOPIC_COLOR_ORDER)])

    link_colors = [f"rgba{(*hex_to_rgb(theme_map[themes[s]]), 0.4)}" for s in src]

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=30,
                    thickness=35,
                    label=node_labels,
                    color=node_colors,
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    hovertemplate="%{customdata}<extra></extra>",
                    customdata=theme_hover + topic_hover,
                ),
                link=dict(
                    source=src,
                    target=tgt,
                    value=val,
                    color=link_colors,
                    hovertemplate="%{customdata}<extra></extra>",
                    customdata=link_hover,
                ),
            )
        ]
    )
    fig.update_layout(
        font=dict(family="DM Sans, sans-serif", size=13, color="#2c3e50"),
        height=720,
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def build_themes_sankey_json() -> None:
    src = PRECOMPUTED / "main_topics.parquet"
    dst = FIGURES / "themes_sankey.json"
    df = pd.read_parquet(src)
    fig = build_sankey_figure(df)
    dst.write_text(pio.to_json(fig))
    print(f"  wrote {dst.relative_to(REPO)}  size={dst.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    print("Building precomputed artifacts...")
    build_emotion_slim()
    build_themes_sankey_json()
    print("Done.")
