import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import hex_to_rgb

from shared_ui import inject_inner_life_css, render_footer, render_hero

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

# --- Load Data ---
@st.cache_data
def load_main_topics():
    return pd.read_parquet("precomputed/main_topics.parquet")
def format_number(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return str(int(n))

@st.cache_resource(show_spinner=False)
def create_sankey_custom(df):
    filtered = df[df['count'] > 0].copy()
    if filtered.empty:
        return go.Figure().add_annotation(text="No data to display")

    theme_vol = filtered.groupby('theme')['count'].sum().sort_values(ascending=False)
    topic_vol = filtered.groupby('cluster_name')['count'].sum().sort_values(ascending=False)
    themes = theme_vol.index.tolist()
    topics = topic_vol.index.tolist()
    node_labels = themes + topics
    theme_index = {t: i for i, t in enumerate(themes)}
    topic_index = {t: i + len(themes) for i, t in enumerate(topics)}

    total_discussions = filtered['count'].sum()

    theme_hover_text = []
    for theme in themes:
        theme_count = theme_vol[theme]
        percentage = (theme_count / total_discussions) * 100
        theme_hover_text.append(
            f"<b style='font-size: 16px; color: #2c3e50'>{theme}</b><br>"
            f"Total: <b>{format_number(theme_count)}</b><br>"
            f"Global Share: <b>{percentage:.1f}%</b><br>"
        )

    # One groupby per topic metric (vectorized) rather than filtering the
    # DF per topic inside a Python loop.
    topic_grouped = filtered.groupby('cluster_name')
    topic_primary_idx = topic_grouped['count'].idxmax()
    topic_primary_theme = filtered.loc[topic_primary_idx, ['cluster_name', 'theme', 'count']].set_index('cluster_name')
    topic_connected = topic_grouped['theme'].nunique()

    topic_hover_text = []
    for topic in topics:
        topic_count = topic_vol[topic]
        primary_theme = topic_primary_theme.loc[topic, 'theme']
        primary_count = topic_primary_theme.loc[topic, 'count']
        connected_themes = int(topic_connected.loc[topic])
        percentage = (topic_count / total_discussions) * 100
        topic_hover_text.append(
            f"<b style='font-size: 16px; color: #2c3e50'>{topic}</b><br>"
            f"Mentions: <b>{format_number(topic_count)}</b><br>"
            f"Global Share: <b>{percentage:.1f}%</b><br>"
            f"Primary Theme: <b>{primary_theme}</b><br>"
            f"Top Count: <b>{format_number(primary_count)}</b><br>"
            f"Themes: <b>{connected_themes}</b>"
        )

    node_hover_text = theme_hover_text + topic_hover_text

    # Replace iterrows() with to_dict('records'), and pre-index theme/topic
    # positions so we don't pay a linear .index() per row.
    src, tgt, val, link_hover_text = [], [], [], []
    for r in filtered.to_dict('records'):
        src.append(theme_index[r['theme']])
        tgt.append(topic_index[r['cluster_name']])
        val.append(r['count'])
        flow_percentage = (r['count'] / total_discussions) * 100
        topic_contribution = (r['count'] / topic_vol[r['cluster_name']]) * 100
        link_hover_text.append(
            f"<b style='font-size: 15px; color: #2c3e50'>{r['theme']} → {r['cluster_name']}</b><br>"
            f"Count: <b>{format_number(r['count'])}</b><br>"
            f"Global Share: <b>{flow_percentage:.1f}%</b><br>"
            f"Topic Share: <b>{topic_contribution:.1f}%</b>"
        )

    color_families = {
        "Meditation & Mindfulness": ["#00FFFF", "#87FDFC"],
        "Self-Regulation": ["#0091EA", "#2196F3"],
        "Anxiety & Mental Health": ["#00E676", "#4CAF50"],
        "Awareness": ["#CDDC39", "#D4E157"],
        "Buddhism & Spirituality": ["#FFD600", "#FFD700"],
        "Concentration & Flow": ["#FF6D00", "#FF8C00"],
        "Practice, Retreat & Meta": ["#F50057", "#F50057"]
    }

    topic_color_order = [
        "#00E5FF", "#0091EA", "#00E676", "#CDDC39", "#FFD600", "#FF6D00", "#F50057"
    ]

    theme_assignments = {
        "self-awareness": "Awareness",
        "jhanas": "Buddhism & Spirituality",
        "metta": "Buddhism & Spirituality",
        "practice updates": "Practice, Retreat & Meta"
    }

    vivid_palette = [
        "#00BFFF", "#42A5F5", "#66BB6A", "#81C784", "#ADFF2F",
        "#FFEB3B", "#FFA500", "#FF9800", "#FF80AB", "#FFB6C1",
        "#40E0D0", "#00CED1", "#87CEFA", "#B0E0E6", "#98FB98",
        "#FFE4B5", "#FFDAB9", "#FFC0CB", "#DA70D6", "#9370DB"
    ]

    node_colors = []
    theme_map = {}
    vivid_idx = 0

    for t in themes:
        t_lower = t.lower()
        if t_lower == "mindfulness":
            node_colors.append(color_families["Meditation & Mindfulness"][1])
            theme_map[t] = color_families["Meditation & Mindfulness"][1]
            continue

        family_override = theme_assignments.get(t_lower)
        if family_override:
            color = color_families[family_override][vivid_idx % 2]
            node_colors.append(color)
            theme_map[t] = color
            vivid_idx += 1
            continue

        matched = False
        for fam, col in color_families.items():
            if t_lower in fam.lower():
                node_colors.append(col[0])
                theme_map[t] = col[0]
                matched = True
                break

        if not matched:
            c = vivid_palette[vivid_idx % len(vivid_palette)]
            node_colors.append(c)
            theme_map[t] = c
            vivid_idx += 1

    for i, t in enumerate(topics):
        node_colors.append(topic_color_order[i % len(topic_color_order)])

    link_colors = [f'rgba{(*hex_to_rgb(theme_map[themes[s]]), 0.4)}' for s in src]

    # Create enhanced Sankey with world-class hover
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=30,
            thickness=35,
            label=node_labels,
            color=node_colors,
            line=dict(color="rgba(0,0,0,0)", width=0),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=node_hover_text
        ),
        link=dict(
            source=src,
            target=tgt,
            value=val,
            color=link_colors,
            hovertemplate='%{customdata}<extra></extra>',
            customdata=link_hover_text
        )
    )])

    fig.update_layout(
        height=900,
        margin=dict(t=60, b=20, l=30, r=30),
        title="Themes → Topics Flow",
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="DM Sans, sans-serif", size=16, color="#333"),
        hoverlabel=dict(
            bgcolor="rgba(255,255,255,0.96)",
            bordercolor="rgba(160,160,160,0.4)",
            font=dict(
                family="DM Sans, sans-serif",
                size=13,
                color="#2c3e50"
            ),
            align="left",
            namelength=-1
        )
    )
    
    return fig

# --- Main Function ---
def run():
    try:
        main_topics = load_main_topics()
    except Exception:
        main_topics = pd.DataFrame()

    inject_inner_life_css()
    render_hero(
        eyebrow="THEMES",
        title="Inner Life Themes",
        subtitle="Topic Flow: How Themes Connect",
        description="Hover over to discover theme details.",
    )
    
    # Enhanced chart display with export configuration
    fig = create_sankey_custom(main_topics)
    
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