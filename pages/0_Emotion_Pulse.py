import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from shared_ui import inject_inner_life_css, render_hero

st.set_page_config(
    page_title="🌊 The Emotional Pulse of the Meditation Landscape",
    layout="wide"
)

# --- Text color logic for hover popup ---
def ideal_text_color(bg_hex: str) -> str:
    bg_hex = bg_hex.lstrip("#")
    r, g, b = tuple(int(bg_hex[i:i+2], 16) for i in (0, 2, 4))
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return 'black' if luminance > 186 else 'white'

def run():
    # Initialize session state for interaction tracking
    if 'plot_interacted' not in st.session_state:
        st.session_state.plot_interacted = False

    # --- Styled CSS with enhanced initial hover box from first script ---
    # Hover box size configuration (easily adjustable)
    hover_box_config = {
        'max_width': '1000px',  # Increased from 400px to match first script
        'padding': '10px 14px',  # Match first script padding
        'font_size': '12px',
        'line_height': '1.4',
        'border_radius': '8px',
        'top_margin': '15px',  # Match first script positioning
        'side_margin': '15px'
    }
    
    st.markdown(f"""
    <style>
    .footer-text {{
        text-align: center;
        font-size: 1rem;
        font-weight: 600;
        color: #666;
        margin-top: 1.5rem;
        padding: 0.8rem;
        border-top: 1px solid #eee;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    @supports not (-webkit-background-clip: text) {{
        .footer-text {{
            color: #667eea !important;
            background: none !important;
        }}
    }}
    .plot-container {{
        max-width: 500px;
        margin: auto;
        position: relative;
    }}
    
    #initial-hover-box {{
        position: absolute;
        top: {hover_box_config['top_margin']};
        left: {hover_box_config['side_margin']};
        right: {hover_box_config['side_margin']};
        background-color: rgba(106, 90, 205, 0.95);
        color: white;
        padding: {hover_box_config['padding']};
        border-radius: {hover_box_config['border_radius']};
        font-size: {hover_box_config['font_size']};
        font-family: Arial, sans-serif;
        max-width: {hover_box_config['max_width']};
        line-height: {hover_box_config['line_height']};
        word-break: break-word;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.2);
        white-space: normal;
        z-index: 10000;
        opacity: 1;
        transition: opacity 0.3s ease;
        pointer-events: none;
    }}
    
    </style>
    """, unsafe_allow_html=True)

    inject_inner_life_css()
    render_hero(
        eyebrow="PULSE",
        title="Emotion Pulse",
        subtitle="2,977 meditation posts, each colored by its dominant emotion",
        description="This emotional map reveals how people express their emotions through meditation practices, drawn from thousands of Reddit posts and comments shared between January 2024 and June 2025.",
    )
    
    # Info sections with enhanced styling
    st.markdown("""
    <div class="info-section" style="text-align: left; padding: 0.5rem 1rem;">
        <p style="
            font-size: 1rem;
            margin: 0;
            color: #444;
            max-width: 1400px;
            width: 95%;
            line-height: 1.5;
        ">
            Conducted advanced NLP processing using <strong>Google Research's <a href="https://research.google/blog/goemotions-a-dataset-for-fine-grained-emotion-classification/" target="_blank" style="color: #4285f4; text-decoration: none; border-bottom: 1px dotted #4285f4;">GoEmotions</a> Model</strong> with 27-category emotion classification system and the Fine-grained model trained on 58,000 human-annotated texts, to decode emotional contexts among Reddit's post and comments on Meditation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
# Poetic invitation section
    st.markdown("""
    <div class="annotation-container">
        <div style="display: flex; justify-content: center;">
            <div style="max-width: 500px; text-align: center;">
                <p style="font-size: 16px; color: #718096; margin: 0; line-height: 1.8; font-weight: 300; opacity: 0.9;">
                    <strong>Each point</strong> marks a message shared on Reddit about meditation.<br>
                    <strong>Color</strong> reflects the dominant emotional underneath each message.
                       <br> 
                </p>
            </div>
        </div>
</div>
""", unsafe_allow_html=True)

    @st.cache_data
    def load_emotion_clusters():
        return pd.read_parquet("precomputed/emotion_clusters.parquet")

    emotion_df = load_emotion_clusters()

    # Format hover text with different line lengths for different content types
    def wrap_hover_text(text):
        """Smart wrapping with different lengths for different content types"""
        if pd.isna(text):
            return ""
        
        text = str(text).strip()
        
        # Thoroughly clean hidden characters first
        text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        text = text.replace('\u00a0', ' ')  # Non-breaking space
        text = text.replace('\u2009', ' ')  # Thin space
        text = text.replace('\u200b', '')   # Zero-width space
        text = ' '.join(text.split())  # Normalize all whitespace
        
        # Split into lines if already formatted with <br>
        lines = text.split('<br>')
        wrapped_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Different wrapping rules based on content type.
            # 75 chars/line keeps tooltips a reasonable width (Plotly doesn't
            # auto-wrap hover text; it renders pre-formatted <br> breaks as-is).
            if line.startswith("Top Emotions:"):
                # Keep Top Emotions on one line if short; otherwise break at emotion boundaries
                if len(line) <= 75:
                    wrapped_lines.append(line)
                else:
                    wrapped_lines.extend(wrap_emotions_line(line))

            elif line.startswith("Post/Comment:") or line.startswith("Comment:") or line.startswith("Post:"):
                wrapped_lines.extend(wrap_text_content(line, 75))

            else:
                # Other content (metadata, etc.)
                wrapped_lines.extend(wrap_text_content(line, 75))
        
        return '<br>'.join(wrapped_lines)
    
    def wrap_emotions_line(line):
        """Special handling for Top Emotions line"""
        import re
        # Clean the line thoroughly first
        line = ' '.join(line.split())  # Remove extra spaces
        
        # Try to break at emotion boundaries
        emotion_pattern = r'(\w+:\s*\d+%)'
        emotions = re.findall(emotion_pattern, line)
        
        if emotions:
            lines = []
            current_line = "Top Emotions: "
            
            for emotion in emotions:
                if len(current_line + emotion + " ") > 75:
                    if current_line.strip() != "Top Emotions:":
                        lines.append(current_line.strip())
                        current_line = emotion + " "
                    else:
                        current_line += emotion + " "
                else:
                    current_line += emotion + " "

            if current_line.strip():
                lines.append(current_line.strip())

            return lines
        else:
            # Fallback to regular wrapping
            return wrap_text_content(line, 75)
    
    def wrap_text_content(text, max_length):
        """Wrap text at specified length without breaking words, combining short lines"""
        # Clean text first
        text = ' '.join(text.split())
        
        if len(text) <= max_length:
            return [text]
        
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            space_length = 1 if current_line else 0
            
            if current_length + space_length + word_length > max_length:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = word_length
                else:
                    lines.append(word)
                    current_length = 0
            else:
                current_line.append(word)
                current_length += space_length + word_length
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Combine short consecutive lines if they fit together
        combined_lines = []
        i = 0
        while i < len(lines):
            current = lines[i]
            
            # Try to combine with next line if both are short
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                combined = current + ' ' + next_line
                
                # If combined length is within limit and both lines are short, combine them
                if len(combined) <= max_length and len(current.split()) <= 4 and len(next_line.split()) <= 4:
                    combined_lines.append(combined)
                    i += 2  # Skip next line since we combined it
                    continue
            
            combined_lines.append(current)
            i += 1
        
        return combined_lines

    # Wrap all hover strings once per session. The previous implementation
    # ran wrap_hover_text via .apply() on every rerun, which was the
    # dominant cost on this page. We memoize on the source parquet (which
    # is load-cached) by object id via session_state so subsequent reruns
    # skip the Python-loop wrap entirely.
    cache_key = "_emotion_formatted_hover_v1"
    if (
        cache_key not in st.session_state
        or st.session_state[cache_key].get("id") != id(emotion_df)
    ):
        with st.spinner("Rendering 2,977 emotions..."):
            formatted = emotion_df['hover_text'].map(wrap_hover_text)
            st.session_state[cache_key] = {"id": id(emotion_df), "data": formatted}

    df = emotion_df.copy()
    df['formatted_hover_text'] = st.session_state[cache_key]["data"].values

    cluster_colors = {
        'Reflective Caring': '#ff5e78',
        'Soothing Empathy': '#00c49a',
        'Tender Uncertainty': '#6a5acd',
        'Melancholic Confusion': '#9a32cd',
        'Anxious Concern': '#ffc300'
    }

    cluster_styles = {
        'Reflective Caring': dict(symbol='circle', size=8),
        'Soothing Empathy': dict(symbol='diamond', size=8),
        'Tender Uncertainty': dict(symbol='triangle-nw', size=9),
        'Melancholic Confusion': dict(symbol='star-square', size=8),
        'Anxious Concern': dict(symbol='star-triangle-up', size=8)
    }

    # Build the full figure once per session; reruns triggered by widget
    # state (e.g. the hover-once interaction flag) no longer rebuild any of
    # the traces. Cached by the source-df object id via session_state so
    # we don't need to hash every row as a cache key.
    fig_cache_key = "_emotion_fig_v1"
    if (
        fig_cache_key not in st.session_state
        or st.session_state[fig_cache_key].get("id") != id(df)
    ):
        # Calculate the 95% width boundaries for hover detection
        x_min = df['umap_x'].min()
        x_max = df['umap_x'].max()
        x_range = x_max - x_min
        x_center = (x_min + x_max) / 2
        hover_width = x_range * 0.95
        hover_x_min = x_center - hover_width / 2
        hover_x_max = x_center + hover_width / 2

        traces = []
        for label, color in cluster_colors.items():
            text_color = ideal_text_color(color)
            cluster_df = df[df['archetype_label'] == label]

            # Filter points to only include those within the 95% hover area
            in_range = (cluster_df['umap_x'] >= hover_x_min) & (cluster_df['umap_x'] <= hover_x_max)
            hover_cluster_df = cluster_df[in_range]
            no_hover_cluster_df = cluster_df[~in_range]

            # Convert hex color to rgba with 60% opacity for hover background
            color_hex = color.lstrip('#')
            r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
            hover_bg_color = f'rgba({r}, {g}, {b}, 0.9)'

            # Add trace for points with hover
            if not hover_cluster_df.empty:
                traces.append(go.Scatter(
                    x=hover_cluster_df['umap_x'],
                    y=hover_cluster_df['umap_y'],
                    mode='markers',
                    name=label,
                    marker=dict(color=color, opacity=0.7, **cluster_styles[label]),
                    text=hover_cluster_df['formatted_hover_text'],
                    hoverinfo='text',
                    hoverlabel=dict(
                        bgcolor=hover_bg_color,
                        font=dict(color=text_color, size=12),
                        align='left',
                        bordercolor='rgba(0,0,0,0.2)',
                        namelength=-1
                    ),
                    hovertemplate='%{text}<extra></extra>',
                    showlegend=False  # Disabled legend for hover points
                ))

            # Add trace for points without hover
            if not no_hover_cluster_df.empty:
                traces.append(go.Scatter(
                    x=no_hover_cluster_df['umap_x'],
                    y=no_hover_cluster_df['umap_y'],
                    mode='markers',
                    name=label,
                    marker=dict(color=color, opacity=0.7, **cluster_styles[label]),
                    hoverinfo='skip',
                    showlegend=False  # Disabled legend for non-hover points
                ))

        # Cluster centroids + label offsets
        offsets = {
            'Reflective Caring': (3.9, 1.2),
            'Soothing Empathy': (1.5, 4),
            'Tender Uncertainty': (-4.1, -2.5),
            'Melancholic Confusion': (0.5, -1.5),
            'Anxious Concern': (2.4, -0.3)
        }
        centroids = df.groupby('archetype_label')[['umap_x', 'umap_y']].mean()
        for archetype, (x, y) in centroids.iterrows():
            dx, dy = offsets.get(archetype, (0, 0))
            traces.append(go.Scatter(
                x=[x + dx],
                y=[y + dy],
                mode='text',
                text=[f"<b>{archetype}</b>"],
                textfont=dict(size=20, color=cluster_colors[archetype], family='sans-serif'),
                showlegend=False,
                hoverinfo='skip'
            ))

        y_min = df['umap_y'].min()
        y_max = df['umap_y'].max()
        y_buffer_bottom = 0.01 * (y_max - y_min)  # Small padding
        y_buffer_top = 0.13 * (y_max - y_min)     # Keep a bit more top room for labels
        st.session_state[fig_cache_key] = {
            "id": id(df),
            "traces": traces,
            "y_min": y_min,
            "y_max": y_max,
            "y_buffer_bottom": y_buffer_bottom,
            "y_buffer_top": y_buffer_top,
        }

    _cached = st.session_state[fig_cache_key]
    traces = _cached["traces"]
    y_min = _cached["y_min"]
    y_max = _cached["y_max"]
    y_buffer_bottom = _cached["y_buffer_bottom"]
    y_buffer_top = _cached["y_buffer_top"]

    layout = go.Layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color='black'),
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            ticks='',
            scaleanchor="y",
            scaleratio=1,
            fixedrange=True
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False,
            ticks='',
            range=[y_min - y_buffer_bottom, y_max + y_buffer_top],
            fixedrange=True
        ),
        hovermode='closest',
        autosize=True,
        height=1000,
        margin=dict(t=60, b=10, l=40, r=40)  # Match first script margins
    )

    fig = go.Figure(data=traces, layout=layout)
    
    # Configure the plot - keep hover functionality enabled
    config = {
        'displayModeBar': False,
        'displaylogo': False,
        'modeBarButtonsToRemove': [
            'zoom2d', 'pan2d', 'select2d', 'lasso2d',
            'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d',
            'toggleSpikelines'
        ],
        'scrollZoom': False,
        'doubleClick': False,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'emotion_pulse_meditation_map',
            'height': 1000,
            'width': 1200,
            'scale': 2
        }
    }

    # --- Render in centered max-width container ---
    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    
    # Use specific seed text from first script (capped with 3 words fewer)
    seed_text = """<b>Emotional Pulse: Tender Uncertainty</b><br><b>Top Emotions:</b> caring: 75% annoying: 71% desire: 70% disapproval: 62% realization: 60% remorse: 60% curiosity: 59% approval: 56% excitement: 54% confusion: 53%<br><b>Post/Comment:</b> Insight Timer used to be amazing. While the community content is a nice-to-have, I mostly used it for the timer feature. However in the past few months the number of disruptive..."""

    # Show initial hover box only if no interaction detected yet
    if not st.session_state.plot_interacted:
        st.markdown(f"""
        <div id="initial-hover-box">
            {seed_text}<br><br><b><span style="text-decoration: underline; text-decoration-color: #ffc300; text-decoration-thickness: 3px;">Hover over</span></b> to find out 🔍
        </div>
        """, unsafe_allow_html=True)

    # Render the plot.
    st.plotly_chart(fig, use_container_width=True, config=config, key="emotion_plot")

    # Enhanced interaction detection from first script
    if not st.session_state.plot_interacted:
        st.markdown("""
        <script>
        // Relocate hover box into chart container so its width is bound by the
        // chart's rendered width (not the page). Height remains auto, growing
        // with content. Runs as soon as Plotly has mounted.
        (function() {
            let attempts = 0;
            const attach = () => {
                const plotContainer = document.querySelector('[data-testid="stPlotlyChart"]');
                const hoverBox = document.getElementById('initial-hover-box');
                if (plotContainer && hoverBox) {
                    plotContainer.style.position = 'relative';
                    if (hoverBox.parentElement !== plotContainer) {
                        plotContainer.appendChild(hoverBox);
                    }
                    const hideBox = () => {
                        hoverBox.style.opacity = '0';
                        setTimeout(() => hoverBox.remove(), 300);
                    };
                    plotContainer.addEventListener('mouseenter', hideBox, { once: true });
                    plotContainer.addEventListener('mousemove', hideBox, { once: true });
                    return true;
                }
                return false;
            };
            // Poll briefly until Plotly has mounted (max ~3s)
            const poll = setInterval(() => {
                attempts += 1;
                if (attach() || attempts > 30) {
                    clearInterval(poll);
                }
            }, 100);
        })();
        </script>
        """, unsafe_allow_html=True)

        # Auto-hide after 5 seconds from first script
        st.markdown("""
        <style>
        #initial-hover-box {
            animation: fadeOut 1s ease-in-out 5s forwards;
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; pointer-events: none; }
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="footer-text">
            Powered By MinyanLabs ©2026
        </div>
        """, unsafe_allow_html=True)

run()