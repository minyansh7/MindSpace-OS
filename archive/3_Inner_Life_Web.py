import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
import json

from shared_ui import PLOTLY_CDN_URL, inject_inner_life_css, render_footer, render_hero

st.set_page_config(page_title="Inner Life Web", layout="wide")


def run():
    inject_inner_life_css()

    render_hero(
        eyebrow="WEB",
        title="Inner Life Web",
        subtitle="Which meditation topics appear together across the full archive",
        description="Explore meditation topics and their interconnections through engagement-weighted, sentiment-infused narratives, drawn from 2,977 Reddit posts and comments shared between January 2024 and June 2025.",
    )
    
    # Top-N node cap with opt-out toggle. Default is capped (40 nodes)
    # because the full network hairballs in narrow windows. Toggle state
    # persists via st.session_state under key "web_show_all_nodes".
    show_all_nodes = st.toggle(
        "Show all nodes (uncheck for top-40 by engagement)",
        value=False,
        key="web_show_all_nodes",
        help="Default view shows the 40 most-engaged theme nodes. Toggle on to see the full network.",
    )

    @st.cache_data
    def load_edges_clusters():
        return pd.read_parquet("precomputed/timeseries/df_edges.parquet")

    @st.cache_data
    def load_nodes_clusters():
        return pd.read_parquet("precomputed/timeseries/df_nodes.parquet")

    edges = load_edges_clusters()
    nodes = load_nodes_clusters()

    # Cached pure function: produces all JS-ready payloads for the iframe.
    # Keyed on the `show_all_nodes` toggle; the underlying parquets are
    # already load-cached so we can use `id(...)` to spot a replaced frame.
    # Replaces the previous per-rerun work (~4 iterrows loops + one nested
    # iterrows over edges × nodes, which is O(E*N)).
    @st.cache_data(show_spinner=False)
    def build_web_payload(show_all: bool, _edges_df_id: int, _nodes_df_id: int):
        df_edges = edges.copy()
        df_nodes = nodes.copy()

        # Back-compat: older parquets lack the `sentiment` column. Silent
        # fallback to 0.0 matches Inner Life Trees' behavior.
        if 'sentiment' not in df_nodes.columns:
            df_nodes['sentiment'] = 0.0
        if 'sentiment' not in df_edges.columns:
            df_edges['sentiment'] = 0.0

        # Apply coordinate rotation (vectorized)
        df_nodes['x_rotated'] = -df_nodes['y']
        df_nodes['y_rotated'] = df_nodes['x']
        df_edges['x0_rotated'] = -df_edges['y0']
        df_edges['y0_rotated'] = df_edges['x0']
        df_edges['x1_rotated'] = -df_edges['y1']
        df_edges['y1_rotated'] = df_edges['x1']

        # Identify connected nodes (vectorized via isin). Zip of numpy arrays
        # is O(E) once; previous implementation iterrows'd over every edge.
        node_coords = set(zip(df_edges['x0_rotated'].to_numpy(),
                              df_edges['y0_rotated'].to_numpy()))
        node_coords.update(zip(df_edges['x1_rotated'].to_numpy(),
                               df_edges['y1_rotated'].to_numpy()))

        node_coord_tuples = list(zip(df_nodes['x_rotated'].to_numpy(),
                                     df_nodes['y_rotated'].to_numpy()))
        connected_mask = [c in node_coords for c in node_coord_tuples]
        df_nodes_connected = df_nodes[pd.Series(connected_mask, index=df_nodes.index)].copy()

        # Apply the top-N cap unless the user has toggled "Show all".
        if not show_all and len(df_nodes_connected) > 40:
            df_nodes_connected = df_nodes_connected.nlargest(40, "scaled_size").copy()

        total_nodes_n = len(df_nodes)
        connected_nodes_n = len(df_nodes_connected)

        # Color mapping for clusters
        custom_cmap = ['#1f77b4', '#808000', '#ff7f0e', '#d62728', '#9467bd', '#8c564b', '#17becf']
        unique_clusters = sorted(df_nodes_connected['cluster_name'].unique())
        cluster_color_map = {name: custom_cmap[i % len(custom_cmap)] for i, name in enumerate(unique_clusters)}

        # Build a single coord→cluster lookup once (O(N)), then an O(E) pass
        # over edges to find both endpoints' cluster names. Previous impl
        # was O(E*N) with a nested iterrows loop.
        coord_to_cluster = dict(zip(
            zip(df_nodes_connected['x_rotated'].to_numpy(),
                df_nodes_connected['y_rotated'].to_numpy()),
            df_nodes_connected['cluster_name'].to_numpy(),
        ))

        edge_data = []
        for rec in df_edges.to_dict('records'):
            start_cluster = coord_to_cluster.get((rec['x0_rotated'], rec['y0_rotated']), "Unknown")
            end_cluster = coord_to_cluster.get((rec['x1_rotated'], rec['y1_rotated']), "Unknown")
            edge_data.append({
                'x0': float(rec['x0_rotated']),
                'y0': float(rec['y0_rotated']),
                'x1': float(rec['x1_rotated']),
                'y1': float(rec['y1_rotated']),
                'weight': float(rec['weight']),
                'color': rec['color'],
                'hover_text': f"<b>Topics:</b> {start_cluster} ↔ {end_cluster}<br><b>Themes:</b> {rec['theme_1']} ↔ {rec['theme_2']}<br><b>Engagement Score:</b> {int(rec['weight'])}<br><b>Sentiment:</b> {rec['sentiment']:.2f}"
            })

        # Node data — single pass over connected nodes, preserving cluster
        # ordering (iterate clusters → records) for downstream JS grouping.
        node_data = []
        for cluster in unique_clusters:
            cluster_slice = df_nodes_connected[df_nodes_connected['cluster_name'] == cluster]
            color = cluster_color_map[cluster]
            for rec in cluster_slice.to_dict('records'):
                raw_score = rec['avg_score']
                if isinstance(raw_score, set):
                    avg_score_display = int(next(iter(raw_score)))
                else:
                    avg_score_display = int(float(raw_score))
                sentiment_value = float(rec['sentiment'])
                node_data.append({
                    'x': float(rec['x_rotated']),
                    'y': float(rec['y_rotated']),
                    'size': float(rec['scaled_size']) / 2.5,
                    'color': color,
                    'cluster': cluster,
                    'hover_text': f"<b>Topic:</b> {rec['cluster_name']}<br><b>Theme:</b> {rec['theme']}<br><b>Engagement Score:</b> {avg_score_display}<br><b>Sentiment:</b> {sentiment_value:.2f}"
                })

        # Calculate centroids for labels
        centroids = df_nodes_connected.groupby('cluster_name').apply(
            lambda g: pd.Series({
                'x': np.average(g['x_rotated'], weights=g['scaled_size']),
                'y': np.average(g['y_rotated'], weights=g['scaled_size']),
                'size_sum': g['scaled_size'].sum()
            })
        ).reset_index()

        # Full 2π spread. The previous 2.2π compressed 7 labels into an
        # arc that wrapped back on itself — the last label landed ~20°
        # from the first, causing Buddhism/Awareness/Self-Regulation
        # overlap at the top of the plot.
        angle_offset = np.linspace(0, 2 * np.pi, len(centroids), endpoint=False)
        angle_offset += np.pi / len(centroids)
        radius_offset = 0.4

        centroids['x'] += radius_offset * np.cos(angle_offset)
        centroids['y'] += radius_offset * np.sin(angle_offset)
        # Anchor text toward the centroid so side labels (Concentration &
        # Flow, Anxiety & Mental Health) render inward instead of clipping.
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
            'total_nodes': total_nodes_n,
            'connected_nodes': connected_nodes_n,
        }

    with st.spinner("Weaving the web..."):
        payload = build_web_payload(show_all_nodes, id(edges), id(nodes))

    edge_data = payload['edge_data']
    node_data = payload['node_data']
    label_data = payload['label_data']
    cluster_color_map = payload['cluster_color_map']
    total_nodes = payload['total_nodes']
    connected_nodes = payload['connected_nodes']

    st.info(f"Showing {connected_nodes} co-current themes out of total {total_nodes} themes ({connected_nodes/total_nodes*100:.1f}%), among high-engagement, strong-sentiment posts or comments (engagement > 30, intensity > 0.3). One post may link to multiple themes.")

    # Create the HTML with WORKING EDGE HOVER using scatter points
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
                min-height: 434px;
            }}
            
            #plotDiv {{
                width: 100%;
                height: 100%;
            }}

        </style>
    </head>
    <body>
        <div class="container">
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
            
            // Function to determine if a color is light or dark
            function isLightColor(color) {{
                // Handle hex colors
                if (color.startsWith('#')) {{
                    const hex = color.slice(1);
                    const r = parseInt(hex.slice(0, 2), 16);
                    const g = parseInt(hex.slice(2, 4), 16);
                    const b = parseInt(hex.slice(4, 6), 16);
                    
                    // Calculate relative luminance
                    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                    return luminance > 0.5;
                }}
                
                // Handle rgba colors
                if (color.startsWith('rgba')) {{
                    const values = color.match(/rgba?\(([^)]+)\)/)[1].split(',');
                    const r = parseInt(values[0].trim());
                    const g = parseInt(values[1].trim());
                    const b = parseInt(values[2].trim());
                    
                    const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255;
                    return luminance > 0.5;
                }}
                
                // Default to light if can't determine
                return true;
            }}
            
            // Function to get contrasting text color
            function getContrastingTextColor(backgroundColor) {{
                return isLightColor(backgroundColor) ? '#000000' : '#ffffff';
            }}
            
            function getResponsiveLayout() {{
                const containerWidth = window.innerWidth;
                const containerHeight = window.innerHeight;
                
                let leftMargin, rightMargin, topMargin, bottomMargin;
                
                if (containerWidth <= 480) {{
                    leftMargin = rightMargin = 10;
                    topMargin = 0;
                    bottomMargin = 0;
                }} else if (containerWidth <= 768) {{
                    leftMargin = rightMargin = 30;
                    topMargin = 0;
                    bottomMargin = 0;
                }} else if (containerWidth <= 1024) {{
                    leftMargin = rightMargin = 50;
                    topMargin = 5;
                    bottomMargin = 0;
                }} else {{
                    leftMargin = rightMargin = 50;
                    topMargin = 5;
                    bottomMargin = 0;
                }}
                
                let plotHeight;
                if (containerWidth <= 480) {{
                    plotHeight = Math.max(252, containerHeight * 0.403);
                }} else if (containerWidth <= 768) {{
                    plotHeight = Math.max(286, containerHeight * 0.432);
                }} else {{
                    plotHeight = Math.max(384, containerHeight * 0.518);
                }}
                
                const labelFontSize = containerWidth <= 768 ? 12 : 14;
                
                // Responsive hover font size
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
            
            // Function to create responsive traces - WORKING SOLUTION with error handling
            function getResponsiveTraces(layout) {{
                const traces = [];
                
                try {{
                    // STEP 1: Add visual edge lines (hover is handled by
                    // invisible scatter points below so the lines themselves
                    // skip hover — Plotly line-trace hover is unreliable).
                    edgeData.forEach((edge) => {{
                        traces.push({{
                            x: [edge.x0, edge.x1],
                            y: [edge.y0, edge.y1],
                            mode: 'lines',
                            line: {{
                                width: edge.weight * 0.005,
                                color: edge.color
                            }},
                            opacity: 0.6,
                            hoverinfo: 'skip',
                            showlegend: false,
                            name: 'edge_lines'
                        }});
                    }});
                    
                    // STEP 2: Create scatter points along edges for hover
                    const edgeHoverX = [];
                    const edgeHoverY = [];
                    const edgeHoverTexts = [];

                    edgeData.forEach((edge) => {{
                        const dx = edge.x1 - edge.x0;
                        const dy = edge.y1 - edge.y0;
                        const edgeLength = Math.sqrt(dx * dx + dy * dy);
                        // More points per unit length = easier hover detection
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
                    
                    // Add invisible hover points
                    if (edgeHoverX.length > 0) {{
                        traces.push({{
                            x: edgeHoverX,
                            y: edgeHoverY,
                            mode: 'markers',
                            marker: {{
                                size: 12,  // Large for easy hover
                                color: 'rgba(0,0,0,0)',  // Completely invisible
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

                // Add nodes by cluster with individual hover colors
                const clusters = [...new Set(nodeData.map(n => n.cluster))];

                clusters.forEach(cluster => {{
                    const clusterNodes = nodeData.filter(n => n.cluster === cluster);
                    if (clusterNodes.length === 0) return;
                    
                    const sizes = clusterNodes.map(n => window.innerWidth <= 768 ? n.size * 0.8 : n.size);
                    
                    // Create individual hover background colors with transparency and contrasting text
                    const hoverBgColors = clusterNodes.map(n => {{
                        try {{
                            // Convert hex to rgba with transparency
                            const hex = n.color || '#1f77b4';
                            const r = parseInt(hex.slice(1, 3), 16);
                            const g = parseInt(hex.slice(3, 5), 16);
                            const b = parseInt(hex.slice(5, 7), 16);
                            return `rgba(${{r}}, ${{g}}, ${{b}}, 0.9)`;  // 90% opacity
                        }} catch (e) {{
                            console.warn('Color conversion error for node:', n, e);
                            return 'rgba(31, 119, 180, 0.9)';  // Default blue
                        }}
                    }});
                    
                    // Create contrasting text colors based on background
                    const hoverTextColors = clusterNodes.map(n => {{
                        const bgColor = n.color || '#1f77b4';
                        return getContrastingTextColor(bgColor);
                    }});
                    
                    traces.push({{
                        x: clusterNodes.map(n => n.x),
                        y: clusterNodes.map(n => n.y),
                        mode: 'markers',
                        marker: {{
                            size: sizes,
                            color: clusterNodes[0].color,
                            opacity: 0.7,
                            line: {{ width: 0.5, color: 'white' }}
                        }},
                        hoverinfo: 'text',
                        hovertext: clusterNodes.map(n => n.hover_text),
                        hoverlabel: {{
                            bgcolor: hoverBgColors,
                            bordercolor: clusterNodes.map(n => n.color || '#1f77b4'),
                            font: {{
                                family: "DM Sans, sans-serif",
                                color: hoverTextColors,
                                size: layout.hoverFontSize
                            }}
                        }},
                        showlegend: false,
                        name: `cluster_${{cluster}}`
                    }});
                }});

                // Add cluster labels. textposition is per-label (computed
                // from centroid angle) so side labels render inward rather
                // than clipping off the canvas edge.
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
                    console.error('Error creating traces:', error);
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
                        filename: 'narrative_web',
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

    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    components.html(html_code, height=744, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="background: #f8fafc; border-left: 3px solid #6366f1;
                padding: 12px 16px; margin: 12px 0;
                border-radius: 0 6px 6px 0; font-size: 0.9rem; color: #334155;">
        <div style="font-size: 10px; color: #64748b; letter-spacing: 0.12em;
                    text-transform: uppercase; font-weight: 700;
                    margin-bottom: 6px;">How to read</div>
        Dots = posts; lines = shared topics; size and thickness = engagement;
        green/red lines = positive/negative sentiment. <b>Hover to discover</b>.
    </div>
    """, unsafe_allow_html=True)

    render_footer()

run()