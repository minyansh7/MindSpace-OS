import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import json

from shared_ui import PLOTLY_CDN_URL, inject_inner_life_css, render_footer, render_hero

st.set_page_config(page_title="Inner Life Currents", layout="wide")

def run():
    inject_inner_life_css()
    # Page-specific control styling (buttons + selectbox) layered on top
    # of the shared Inner Life CSS above.
    st.markdown("""
    <style>
    .stSelectbox > label {
        font-family: "Inter", sans-serif !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        color: #4A5568 !important;
        letter-spacing: 0.5px !important;
    }
    
    .stSelectbox > div > div {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 15px !important;
        backdrop-filter: blur(5px) !important;
        transition: all 0.3s ease !important;
    }
    
    .stSelectbox > div > div:hover {
        border-color: rgba(102, 126, 234, 0.5) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stButton > button {
        font-family: "Inter", sans-serif !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 25px !important;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
        color: #4A5568 !important;
        font-weight: 500 !important;
        letter-spacing: 0.5px !important;
        transition: all 0.3s ease !important;
        backdrop-filter: blur(5px) !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1) !important;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
        border-color: rgba(102, 126, 234, 0.5) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.2) !important;
        color: #667eea !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stButton > button:disabled {
        opacity: 0.5 !important;
        cursor: not-allowed !important;
        transform: none !important;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.1) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    render_hero(
        eyebrow="CURRENTS",
        title="Inner Life Currents",
        subtitle="Where Narratives Converge — And How They Evolve",
        description="A dynamic view of how narratives intersect — and how their connections evolve over time, drawn from 2,977 Reddit posts and comments shared between January 2024 and June 2025.",
    )
    
    # Load data
    @st.cache_data
    def load_edges_clusters():
        return pd.read_parquet("precomputed/timeseries/df_edges.parquet")

    @st.cache_data
    def load_nodes_clusters():
        return pd.read_parquet("precomputed/timeseries/df_nodes.parquet")

    df_edges = load_edges_clusters()
    df_nodes = load_nodes_clusters()

    quarters = sorted(df_nodes['quarter'].unique())
    quarter_labels = [f"{q[:4]}Q{q[-1]}" for q in quarters]
    reverse_label_map = {f"{q[:4]}Q{q[-1]}": q for q in quarters}

    if 'slider_index' not in st.session_state:
        # Default to the latest quarter (2025Q2) for consistency across time-trend pages
        st.session_state.slider_index = len(quarter_labels) - 1

    # ===== UPDATED MEDITATIVE TIME CONTROLS =====
    # Clean time controls with meditative styling - NO RED COLORS!
    col1, col2, col3 = st.columns([2, 4, 2])

    with col2:
        # Meditative time period display
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 1rem;">
            <div style="
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                border-radius: 20px;
                padding: 1rem;
                border: 1px solid rgba(102, 126, 234, 0.2);
                backdrop-filter: blur(5px);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.1);
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 60px;
            ">
                <div style="
                    font-size: 20px;
                    font-weight: 600;
                    color: #4A5568;
                ">Time Travel</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col1:
        # Add spacing to center the button with the label
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("← Previous Quarter", 
                     disabled=st.session_state.slider_index == 0,
                     key="prev_btn", 
                     use_container_width=True):
            st.session_state.slider_index = max(0, st.session_state.slider_index - 1)
            st.rerun()

    with col3:
        # Add spacing to center the button with the label
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        if st.button("Next Quarter →", 
                     disabled=st.session_state.slider_index == len(quarter_labels) - 1,
                     key="next_btn", 
                     use_container_width=True):
            st.session_state.slider_index = min(len(quarter_labels) - 1, st.session_state.slider_index + 1)
            st.rerun()


    selected_quarter = reverse_label_map[quarter_labels[st.session_state.slider_index]]

    # Topic mapping — colors synced with the Inner Life Trees page chart
    # (its script_custom_cmap indexed by alphabetical cluster order).
    # Icons intentionally left empty — color alone is the category anchor,
    # matching the Inner Life Trees page.
    topic_mapping = {
        'Anxiety & Mental Health':   {'color': '#1f77b4', 'icon': ''},
        'Awareness':                 {'color': '#808000', 'icon': ''},
        'Buddhism & Spirituality':   {'color': '#ff7f0e', 'icon': ''},
        'Concentration & Flow':      {'color': '#d62728', 'icon': ''},
        'Meditation & Mindfulness':  {'color': '#9467bd', 'icon': ''},
        'Practice, Retreat, & Meta': {'color': '#8c564b', 'icon': ''},
        'Self-Regulation':           {'color': '#17becf', 'icon': ''},
    }

    # Cached per-quarter prep. Previously the code did O(E) iterrows for
    # connected-node flagging, then an O(E*N) nested iterrows to resolve
    # each edge's endpoints' cluster names. With ~7 quarters cached once,
    # slider scrubbing back/forth is effectively instant after first pass.
    @st.cache_data(show_spinner=False)
    def build_currents_payload(quarter: str, _edges_id: int, _nodes_id: int):
        nodes_q = df_nodes[df_nodes['quarter'] == quarter].copy()
        edges_q = df_edges[df_edges['quarter'] == quarter].copy()

        total_nodes_q = len(nodes_q)
        total_edges_q = len(edges_q)

        # Connected-node flag (vectorized).
        edge_coord_set = set(zip(edges_q['x0'].to_numpy(), edges_q['y0'].to_numpy()))
        edge_coord_set.update(zip(edges_q['x1'].to_numpy(), edges_q['y1'].to_numpy()))
        node_coord_tuples = list(zip(nodes_q['x'].to_numpy(), nodes_q['y'].to_numpy()))
        connected_mask = [c in edge_coord_set for c in node_coord_tuples]
        connected_count = int(sum(connected_mask))

        # Rotate coordinates (vectorized)
        nodes_q['x_rot'] = -nodes_q['y']
        nodes_q['y_rot'] = nodes_q['x']
        edges_q['x0_rot'] = -edges_q['y0']
        edges_q['y0_rot'] = edges_q['x0']
        edges_q['x1_rot'] = -edges_q['y1']
        edges_q['y1_rot'] = edges_q['x1']

        unique_clusters = sorted(nodes_q['cluster_name'].dropna().unique())
        cluster_color_map = {
            c: topic_mapping.get(c, {'color': '#808080'})['color']
            for c in unique_clusters
        }

        # Build coord→cluster lookup once (O(N)); then one O(E) pass over
        # edges. Replaces the previous O(E*N) nested iterrows.
        coord_to_cluster = dict(zip(
            zip(nodes_q['x_rot'].to_numpy(), nodes_q['y_rot'].to_numpy()),
            nodes_q['cluster_name'].to_numpy(),
        ))

        # Flag top-10 edges by weight. Only these get full opacity and hover;
        # the rest fade back as visual texture. Keeps the "backbone" legible
        # instead of ~200 edges competing at the same contrast level.
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

        # Centroids for labels
        centroids = nodes_q.groupby('cluster_name').apply(
            lambda g: pd.Series({
                'x': np.average(g['x_rot'], weights=g['scaled_size']),
                'y': np.average(g['y_rot'], weights=g['scaled_size'])
            })
        ).reset_index()
        angle_offset = np.linspace(0, 1.2 * np.pi, len(centroids), endpoint=False)
        angle_offset += np.pi / len(centroids)
        radius_offset = 0.27
        centroids['x'] += radius_offset * np.cos(angle_offset)
        centroids['y'] += radius_offset * np.sin(angle_offset)
        # Anchor text toward the centroid so long labels on the left side
        # ("Practice, Retreat, & Meta") don't render past the canvas edge.
        # cos < 0 → anchor on left side of plot → draw text rightward (into canvas).
        centroids['cos'] = np.cos(angle_offset)
        label_data = [
            {
                'x': float(row['x']),
                'y': float(row['y']),
                'text': row['cluster_name'],
                'color': cluster_color_map[row['cluster_name']],
                'textposition': 'middle right' if row['cos'] < -0.15 else ('middle left' if row['cos'] > 0.15 else 'middle center'),
            }
            for row in centroids.to_dict('records')
        ]

        return {
            'edge_data': edge_data,
            'node_data': node_data,
            'label_data': label_data,
            'cluster_color_map': cluster_color_map,
            'total_nodes_q': total_nodes_q,
            'total_edges_q': total_edges_q,
            'connected_count': connected_count,
        }

    with st.spinner("Computing quarter..."):
        payload = build_currents_payload(selected_quarter, id(df_edges), id(df_nodes))

    edge_data = payload['edge_data']
    node_data = payload['node_data']
    label_data = payload['label_data']
    cluster_color_map = payload['cluster_color_map']
    total_nodes_q = payload['total_nodes_q']
    connected_count = payload['connected_count']
    connected_percentage = (connected_count / total_nodes_q * 100) if total_nodes_q > 0 else 0

    # Dynamic statistics display
    st.markdown(f"""
    <div style="margin: 0.5rem 0; padding: 0;">
        <div style="background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
                    border-left: 4px solid #667eea;
                    padding: 0.75rem 1rem;
                    border-radius: 0.5rem;
                    margin: 0;
                    backdrop-filter: blur(5px);">
            <div style="font-size: 0.9rem; color: #4A5568; margin: 0; line-height: 1.4; letter-spacing: 0.3px;">
                <strong>{connected_count} meditation topics</strong> are connected to each other out of <strong>{total_nodes_q} total topics</strong>
                (<strong>{connected_percentage:.1f}%</strong>). These come from popular Reddit posts with lots of discussion.<br>
                <span style="color: #4A5568; border-bottom: 4px solid #FFD700; padding-bottom: 1px;"><strong>Hover over</strong></span> for more details.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Create HTML with embedded plot
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="{PLOTLY_CDN_URL}"></script>
        <style>
            body {{ 
                margin: 0; 
                padding: 0; 
                font-family: Arial, sans-serif; 
                background: white;
                overflow-x: hidden;
            }}
            
            .container {{
                position: relative;
                width: 100%;
                height: 100vh;
                min-height: 723px;
            }}
            
            #plotDiv {{ 
                width: 100%; 
                height: 100%; 
            }}
            
            .quarter-overlay {{
                position: absolute;
                top: 15px;
                left: 15px;
                z-index: 1000;
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-family: "Inter", sans-serif;
                font-size: 14px;
                font-weight: 500;
                letter-spacing: 0.5px;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.2);
                backdrop-filter: blur(10px);
            }}
            
        </style>
    </head>
    <body>
        <div class="container">
            <div class="quarter-overlay">
                {quarter_labels[st.session_state.slider_index]}
            </div>
            <div id="plotDiv"></div>
        </div>
        
        <script>
            const edgeData = {json.dumps(edge_data)};
            const nodeData = {json.dumps(node_data)};
            const labelData = {json.dumps(label_data)};
            const clusterColorMap = {json.dumps(cluster_color_map)};
            
            let plotDiv = document.getElementById('plotDiv');
            let currentLayout = null;
            let currentTraces = null;
            
            function isLightColor(color) {{
                if (color.startsWith('#')) {{
                    const hex = color.slice(1);
                    const r = parseInt(hex.slice(0, 2), 16);
                    const g = parseInt(hex.slice(2, 4), 16);
                    const b = parseInt(hex.slice(4, 6), 16);
                    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                    return luminance > 0.5;
                }}
                if (color.startsWith('rgba')) {{
                    const values = color.match(/rgba?\(([^)]+)\)/)[1].split(',');
                    const r = parseInt(values[0].trim());
                    const g = parseInt(values[1].trim());
                    const b = parseInt(values[2].trim());
                    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                    return luminance > 0.5;
                }}
                return true;
            }}
            
            function getContrastingTextColor(backgroundColor) {{
                return isLightColor(backgroundColor) ? '#000000' : '#ffffff';
            }}
            
            function getResponsiveLayout() {{
                const containerWidth = window.innerWidth;
                const containerHeight = window.innerHeight;
                
                let leftMargin, rightMargin, topMargin, bottomMargin;
                
                if (containerWidth <= 480) {{
                    leftMargin = rightMargin = 20;
                    topMargin = 0;
                    bottomMargin = 0;
                }} else if (containerWidth <= 768) {{
                    leftMargin = rightMargin = 50;
                    topMargin = 0;
                    bottomMargin = 0;
                }} else if (containerWidth <= 1024) {{
                    leftMargin = rightMargin = 100;
                    topMargin = 0;
                    bottomMargin = 0;
                }} else {{
                    leftMargin = rightMargin = 200;
                    topMargin = 0;
                    bottomMargin = 0;
                }}
                
                let plotHeight;
                if (containerWidth <= 480) {{
                    plotHeight = Math.max(380, containerHeight * 0.8664);
                }} else if (containerWidth <= 768) {{
                    plotHeight = Math.max(455, containerHeight * 0.8664);
                }} else {{
                    plotHeight = Math.max(524, containerHeight * 0.8664);
                }}
                
                const labelFontSize = containerWidth <= 768 ? 10 : 14;
                let hoverFontSize;
                if (containerWidth <= 480) {{
                    hoverFontSize = 10;
                }} else if (containerWidth <= 768) {{
                    hoverFontSize = 11;
                }} else if (containerWidth <= 1024) {{
                    hoverFontSize = 12;
                }} else {{
                    hoverFontSize = 12;
                }}
                
                return {{
                    plot_bgcolor: 'white',
                    paper_bgcolor: 'white',
                    font: {{ color: 'black' }},
                    xaxis: {{
                        showgrid: false,
                        zeroline: false,
                        showticklabels: false,
                        scaleanchor: 'y',
                        scaleratio: 1,
                        fixedrange: true
                    }},
                    yaxis: {{
                        showgrid: false,
                        zeroline: false,
                        showticklabels: false,
                        fixedrange: true
                    }},
                    hovermode: 'closest',
                    hoverdistance: 25,
                    hoverlabel: {{
                        bgcolor: "rgba(255,255,255,0.96)",
                        bordercolor: "rgba(160,160,160,0.4)",
                        font: {{
                            family: "DM Sans, sans-serif",
                            color: "#2c3e50",
                            size: hoverFontSize
                        }}
                    }},
                    autosize: true,
                    height: plotHeight,
                    margin: {{ 
                        t: topMargin, 
                        b: bottomMargin, 
                        l: leftMargin, 
                        r: rightMargin 
                    }},
                    showlegend: false,
                    labelFontSize: labelFontSize,
                    hoverFontSize: hoverFontSize,
                    dragmode: false
                }};
            }}
            
            function getResponsiveTraces(layout) {{
                const traces = [];
                
                try {{
                    // Add visual edge lines. Top-weight edges stay bold;
                    // the rest fade back to visual texture only.
                    edgeData.forEach((edge, index) => {{
                        const isTop = edge.is_top;
                        traces.push({{
                            x: [edge.x0, edge.x1],
                            y: [edge.y0, edge.y1],
                            mode: 'lines',
                            line: {{
                                width: isTop ? Math.min(8, edge.weight * 0.02) : Math.min(2, edge.weight * 0.015),
                                color: edge.color
                            }},
                            opacity: isTop ? 0.75 : 0.12,
                            hoverinfo: 'skip',
                            showlegend: false,
                            name: 'edge_lines'
                        }});
                    }});

                    // Hover points only on top edges. Restricts hover surface
                    // to the backbone so the viewer isn't swarmed by tooltips.
                    const edgeHoverX = [];
                    const edgeHoverY = [];
                    const edgeHoverTexts = [];

                    edgeData.forEach((edge) => {{
                        if (!edge.is_top) return;
                        const dx = edge.x1 - edge.x0;
                        const dy = edge.y1 - edge.y0;
                        const edgeLength = Math.sqrt(dx * dx + dy * dy);
                        const numPoints = Math.max(5, Math.floor(edgeLength * 20));

                        for (let i = 0; i < numPoints; i++) {{
                            const t = i / (numPoints - 1);
                            const x = edge.x0 + t * dx;
                            const y = edge.y0 + t * dy;

                            edgeHoverX.push(x);
                            edgeHoverY.push(y);
                            edgeHoverTexts.push(edge.hover_text);
                        }}
                    }});
                    
                    // Add invisible hover points with white background
                    if (edgeHoverX.length > 0) {{
                        traces.push({{
                            x: edgeHoverX,
                            y: edgeHoverY,
                            mode: 'markers',
                            marker: {{
                                size: 12,
                                color: 'rgba(0,0,0,0)',
                                line: {{ width: 0 }}
                            }},
                            hoverinfo: 'text',
                            hovertext: edgeHoverTexts,
                            hoverlabel: {{
                                bgcolor: "rgba(255,255,255,0.96)",
                                bordercolor: "rgba(160,160,160,0.4)",
                                font: {{
                                    family: "DM Sans, sans-serif",
                                    color: "#2c3e50",
                                    size: layout.hoverFontSize
                                }}
                            }},
                            showlegend: false,
                            name: 'edge_hover_points'
                        }});
                    }}

                    // Add nodes by cluster with cluster-colored hover backgrounds
                    const clusters = [...new Set(nodeData.map(n => n.cluster))];
                    
                    clusters.forEach(cluster => {{
                        const clusterNodes = nodeData.filter(n => n.cluster === cluster);
                        
                        if (clusterNodes.length === 0) return;
                        
                        const sizes = clusterNodes.map(n => window.innerWidth <= 768 ? n.size * 0.8 : n.size);

                        // Node dots are visual texture only — no hover.
                        // Keeps the hover surface limited to the top edges
                        // so tooltips feel curated instead of overwhelming.
                        traces.push({{
                            x: clusterNodes.map(n => n.x),
                            y: clusterNodes.map(n => n.y),
                            mode: 'markers',
                            marker: {{
                                size: sizes,
                                color: clusterNodes[0].color,
                                opacity: 0.55,
                                line: {{ width: 0.5, color: 'white' }}
                            }},
                            hoverinfo: 'skip',
                            showlegend: false,
                            name: `cluster_${{cluster}}`
                        }});
                    }});
                
                    // Add cluster labels. textposition is set per-label
                    // (computed from centroid angle) so left-side labels
                    // like "Practice, Retreat, & Meta" render rightward
                    // into the canvas instead of clipping off the edge.
                    labelData.forEach((label, index) => {{
                        traces.push({{
                            x: [label.x],
                            y: [label.y],
                            mode: 'text',
                            text: [`<b>${{label.text}}</b>`],
                            textposition: label.textposition || 'middle center',
                            textfont: {{
                                size: layout.labelFontSize,
                                color: label.color,
                                family: 'sans-serif'
                            }},
                            showlegend: false,
                            hoverinfo: 'none',
                            name: `label_${{index}}`
                        }});
                    }});

                    return traces;
                    
                }} catch (error) {{
                    console.error('❌ Error creating traces:', error);
                    return [];
                }}
            }}
            
            function createPlot() {{
                currentLayout = getResponsiveLayout();
                currentTraces = getResponsiveTraces(currentLayout);
                
                const config = {{
                    displayModeBar: true,
                    toImageButtonOptions: {{
                        format: 'png',
                        filename: 'living_narrative',
                        height: currentLayout.height,
                        width: Math.min(1200, window.innerWidth),
                        scale: 2
                    }},
                    modeBarButtonsToRemove: [
                        'pan2d', 
                        'lasso2d', 
                        'select2d',
                        'zoom2d',
                        'zoomIn2d',
                        'zoomOut2d',
                        'autoScale2d',
                        'resetScale2d'
                    ],
                    scrollZoom: false,
                    doubleClick: false,
                    staticPlot: false,
                    responsive: true
                }};
                
                try {{
                    Plotly.newPlot('plotDiv', currentTraces, currentLayout, config)
                        .catch(function(error) {{
                            console.error('Plot creation failed:', error);
                        }});
                }} catch (error) {{
                    console.error('Plot creation error:', error);
                }}
            }}

            function resizePlot() {{
                if (plotDiv && plotDiv._fullLayout) {{
                    const newLayout = getResponsiveLayout();
                    const newTraces = getResponsiveTraces(newLayout);
                    Plotly.react('plotDiv', newTraces, newLayout);
                }}
            }}

            let resizeTimeout;
            function debouncedResize() {{
                clearTimeout(resizeTimeout);
                resizeTimeout = setTimeout(resizePlot, 300);
            }}
            
            window.addEventListener('resize', debouncedResize);
            window.addEventListener('orientationchange', function() {{
                setTimeout(debouncedResize, 500);
            }});
            
            createPlot();
            
            setTimeout(() => {{
                if (plotDiv) {{
                    Plotly.Plots.resize('plotDiv');
                }}
            }}, 100);
        </script>
    </body>
    </html>
    """

    st.markdown('<div class="plot-container" style="margin: 0; padding: 0;">', unsafe_allow_html=True)
    components.html(html_code, height=824, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #f8fafc; border-left: 3px solid #6366f1;
                padding: 12px 16px; margin: 12px 0;
                border-radius: 0 6px 6px 0; font-size: 0.9rem; color: #334155;">
        <div style="font-size: 10px; color: #64748b; letter-spacing: 0.12em;
                    text-transform: uppercase; font-weight: 700;
                    margin-bottom: 6px;">How to read</div>
        Bolder lines = more-engaged discussions; green = positive sentiment,
        red = negative.<br>
        <b>Scrub the Time Travel slider</b> to watch connections shift.
    </div>
    """, unsafe_allow_html=True)

    render_footer()

run()