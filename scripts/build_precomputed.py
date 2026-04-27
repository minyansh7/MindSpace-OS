"""Build-time precomputation for MindSpace OS.

Produces artifacts under ``precomputed/`` that pages load directly, so the
runtime code doesn't rebuild figures or reformat hover text on every cold
start. Rerun this any time the source parquets under ``precomputed/``
change (or the wrap rules below, or the Sankey palette).

    python3 scripts/build_precomputed.py

Outputs:
- ``precomputed/emotion_clusters_slim.parquet`` — the 4 columns the
  Emotion Pulse page actually reads, with ``hover_text`` already wrapped.
- ``precomputed/figures/community_dynamics_sankey.json`` — full Plotly figure
  JSON for the Community Dynamics Sankey (poster → commenter emotional flow),
  ready for ``plotly.io.from_json``.
"""
from __future__ import annotations

import pathlib
import re

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import hex_to_rgb

from _canonical import ARCHETYPE_COLORS

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
# GoEmotions categories that carry no editorial signal in the Top Emotions
# tooltip. "neutral" is the model's catch-all and frequently dominates the
# top-N at scores like 71-76% on points whose actual emotional character
# the user is trying to read; suppressing it keeps the tooltip focused
# on the discriminating emotions both desktop and mobile show.
_HIDDEN_EMOTIONS = {"neutral"}


def _wrap_emotions_line(line: str) -> list[str]:
    line = " ".join(line.split())
    emotions = _EMOTION_PERCENT_RE.findall(line)
    emotions = [em for em in emotions if em.split(":", 1)[0].strip().lower() not in _HIDDEN_EMOTIONS]
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
    # Drop the "Emotion Pulse:" label on the title line so the hover
    # tooltip leads with just the archetype name (e.g. "<b>Reflective
    # Caring</b>"). Source shape: "<b>Emotion Pulse:</b> Reflective
    # Caring</b>" — the trailing </b> has no opener and would dangle if
    # we only stripped the label, so re-wrap the captured archetype text
    # in a fresh <b>...</b>. Both desktop (Streamlit) and mobile (static
    # chart) render this column verbatim, so the strip lives here as the
    # single source of truth.
    text = re.sub(
        r"<b>\s*Emotion Pulse:\s*</b>\s*([^<]+?)\s*</b>",
        lambda m: f"<b>{m.group(1).strip()}</b>",
        text,
    )
    wrapped: list[str] = []
    for line in text.split("<br>"):
        line = line.strip()
        if not line:
            continue
        # Drop hidden emotions (e.g. "neutral: 76%") in-place on the line
        # before the existing wrap path runs. Source line shape is
        # "<b>Top Emotions:</b> caring: 92% neutral: 76% ..."; the original
        # wrap path preserves the <b> tags via _wrap_text_content, so we
        # only mutate the emotion pairs and let it run unchanged.
        if "Top Emotions:" in line:
            for em in _EMOTION_PERCENT_RE.findall(line):
                if em.split(":", 1)[0].strip().lower() in _HIDDEN_EMOTIONS:
                    line = line.replace(em, "").replace("  ", " ")
            line = line.strip()
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
# Community Dynamics (Sankey) figure JSON
# --------------------------------------------------------------------------
# Poster archetype -> Commenter archetype flow, joined via the shared post_id
# that Reddit encodes in the comment URL. Palette imported from _canonical so
# Emotion Pulse, Community Dynamics, and the Astro shell share one source.

_POST_ID_RE = re.compile(r"/comments/([a-z0-9]+)/")

# Hand-picked flows rendered at full opacity. Everything else is faded.
# Matches the source screenshot's emphasis. Colored by the commenter
# (target), so the bright ribbon picks up the right-side node's color.
EMPHASIZED_FLOWS: set[tuple[str, str]] = {
    ("Tender Uncertainty", "Reflective Caring"),
    ("Reflective Caring", "Reflective Caring"),
    ("Anxious Concern", "Reflective Caring"),
    ("Anxious Concern", "Soothing Empathy"),
    ("Melancholic Confusion", "Melancholic Confusion"),
}
EMPHASIZED_ALPHA = 0.85
FADED_ALPHA = 0.15


def _format_number(n: float) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))


def _extract_post_id(url: object) -> str | None:
    m = _POST_ID_RE.search(str(url))
    return m.group(1) if m else None


def build_community_dynamics_sankey(df: pd.DataFrame) -> go.Figure:
    df = df[["type", "url", "archetype_label"]].copy()
    df["post_id"] = df["url"].map(_extract_post_id)

    posts = (
        df[df["type"] == "post"][["post_id", "archetype_label"]]
        .rename(columns={"archetype_label": "poster"})
        .dropna(subset=["post_id"])
    )
    comments = (
        df[df["type"] == "comment"][["post_id", "archetype_label"]]
        .rename(columns={"archetype_label": "commenter"})
        .dropna(subset=["post_id"])
    )
    pairs = comments.merge(posts, on="post_id", how="inner")
    if pairs.empty:
        return go.Figure().add_annotation(text="No data to display")

    total = len(pairs)
    poster_vol = pairs["poster"].value_counts()
    commenter_vol = pairs["commenter"].value_counts()

    # Order each side by descending volume — matches screenshot (Tender
    # Uncertainty top-left, Reflective Caring top-right).
    posters = poster_vol.index.tolist()
    commenters = commenter_vol.index.tolist()
    node_labels = posters + commenters
    poster_index = {a: i for i, a in enumerate(posters)}
    commenter_index = {a: i + len(posters) for i, a in enumerate(commenters)}

    flow = (
        pairs.groupby(["poster", "commenter"]).size().reset_index(name="count")
    )

    # Per-poster "top reply" archetype for node hover.
    poster_top_reply = (
        flow.loc[flow.groupby("poster")["count"].idxmax()]
        .set_index("poster")[["commenter", "count"]]
    )
    commenter_top_poster = (
        flow.loc[flow.groupby("commenter")["count"].idxmax()]
        .set_index("commenter")[["poster", "count"]]
    )
    poster_connected = flow.groupby("poster")["commenter"].nunique()
    commenter_connected = flow.groupby("commenter")["poster"].nunique()

    poster_hover = [
        (
            f"<b style='font-size: 16px; color: #2c3e50'>{a}</b><br>"
            f"Posts: <b>{_format_number(poster_vol[a])}</b><br>"
            f"Global Share: <b>{poster_vol[a]/total*100:.1f}%</b><br>"
            f"Connected comments: <b>{int(poster_connected.loc[a])}</b><br>"
            f"Top reply: <b>{poster_top_reply.loc[a, 'commenter']}</b> "
            f"(<b>{poster_top_reply.loc[a, 'count']/poster_vol[a]*100:.1f}%</b>)"
        )
        for a in posters
    ]
    commenter_hover = [
        (
            f"<b style='font-size: 16px; color: #2c3e50'>{a}</b><br>"
            f"Replies: <b>{_format_number(commenter_vol[a])}</b><br>"
            f"Global Share: <b>{commenter_vol[a]/total*100:.1f}%</b><br>"
            f"Responding to: <b>{int(commenter_connected.loc[a])}</b> archetypes<br>"
            f"Top poster: <b>{commenter_top_poster.loc[a, 'poster']}</b> "
            f"(<b>{commenter_top_poster.loc[a, 'count']/commenter_vol[a]*100:.1f}%</b>)"
        )
        for a in commenters
    ]

    # Color each link by the commenter (target). Hand-picked flows render at
    # full opacity; the rest are faded but still visible.
    src, tgt, val, link_hover, link_colors = [], [], [], [], []
    for r in flow.to_dict("records"):
        src.append(poster_index[r["poster"]])
        tgt.append(commenter_index[r["commenter"]])
        val.append(r["count"])
        link_hover.append(
            f"<b style='font-size: 15px; color: #2c3e50'>{r['poster']} → {r['commenter']}</b><br>"
            f"Count: <b>{_format_number(r['count'])}</b><br>"
            f"Global Share: <b>{r['count']/total*100:.1f}%</b><br>"
            f"Post Share: <b>{r['count']/poster_vol[r['poster']]*100:.1f}%</b><br>"
            f"Comment Share: <b>{r['count']/commenter_vol[r['commenter']]*100:.1f}%</b>"
        )
        target_rgb = hex_to_rgb(ARCHETYPE_COLORS[r["commenter"]])
        alpha = (
            EMPHASIZED_ALPHA
            if (r["poster"], r["commenter"]) in EMPHASIZED_FLOWS
            else FADED_ALPHA
        )
        link_colors.append(f"rgba{(*target_rgb, alpha)}")

    node_colors = [ARCHETYPE_COLORS[a] for a in posters] + [
        ARCHETYPE_COLORS[a] for a in commenters
    ]

    fig = go.Figure(
        data=[
            go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=30,
                    thickness=35,
                    label=node_labels,
                    color=node_colors,
                    line=dict(color="rgba(0,0,0,0)", width=0),
                    hovertemplate="%{customdata}<extra></extra>",
                    customdata=poster_hover + commenter_hover,
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
        height=670,
        # Tight top margin — the POSTER/COMMENTER column eyebrows are
        # rendered in the page just above this chart and already provide
        # visual separation. Bottom margin stays generous so the bottom
        # Melancholic Confusion node and its label clear the chart edge.
        margin=dict(l=10, r=10, t=20, b=50),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def build_community_dynamics_sankey_json() -> None:
    src = PRECOMPUTED / "emotion_clusters.parquet"
    dst = FIGURES / "community_dynamics_sankey.json"
    df = pd.read_parquet(src, columns=["type", "url", "archetype_label"])
    fig = build_community_dynamics_sankey(df)
    dst.write_text(pio.to_json(fig))
    print(f"  wrote {dst.relative_to(REPO)}  size={dst.stat().st_size/1024:.1f} KB")


if __name__ == "__main__":
    print("Building precomputed artifacts...")
    build_emotion_slim()
    build_community_dynamics_sankey_json()
    print("Done.")
