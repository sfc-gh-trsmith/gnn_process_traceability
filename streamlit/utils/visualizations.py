"""
Plotly visualization utilities with Snowflake dark theme.

All visualizations use consistent styling aligned with Snowflake brand colors
and dark mode best practices for reduced eye strain.
"""

import plotly.graph_objects as go
import plotly.io as pio
import networkx as nx
import pandas as pd

# Snowflake Color Palette
COLORS = {
    'primary': '#29B5E8',      # Snowflake Blue
    'secondary': '#11567F',    # Mid Blue
    'accent': '#FF9F0A',       # Orange accent
    'purple': '#8B5CF6',       # Purple accent
    'background': '#0f172a',   # Dark background
    'card': '#1e293b',         # Card background
    'text': '#e2e8f0',         # Primary text
    'text_secondary': '#94a3b8',  # Secondary text
    'border': '#334155',       # Borders
    'critical': '#ef4444',     # Critical/error
    'warning': '#f59e0b',      # Warning
    'success': '#22c55e',      # Success
}

# Chart color sequence
CHART_COLORS = [COLORS['primary'], COLORS['accent'], COLORS['purple'], COLORS['secondary'], COLORS['success']]


def apply_dark_theme(fig):
    """Apply consistent dark theme to a Plotly figure."""
    fig.update_layout(
        paper_bgcolor=COLORS['background'],
        plot_bgcolor=COLORS['background'],
        font=dict(color=COLORS['text'], family='Helvetica Neue, Arial, sans-serif'),
        title=dict(font=dict(size=16, color=COLORS['text'])),
        xaxis=dict(
            gridcolor=COLORS['border'],
            linecolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        yaxis=dict(
            gridcolor=COLORS['border'],
            linecolor=COLORS['border'],
            tickfont=dict(color=COLORS['text_secondary'])
        ),
        hoverlabel=dict(
            bgcolor=COLORS['card'],
            bordercolor=COLORS['border'],
            font=dict(color=COLORS['text'])
        ),
        legend=dict(
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor=COLORS['border'],
            font=dict(color=COLORS['text'])
        )
    )
    return fig


def create_network_graph(nodes_df, edges_df, highlight_defects=True):
    """
    Create interactive network visualization using NetworkX layout.
    
    Args:
        nodes_df: DataFrame with node_id, node_type, name columns
        edges_df: DataFrame with source, target, edge_type columns
        highlight_defects: Whether to highlight defect paths in red
    
    Returns:
        Plotly Figure
    """
    # Create NetworkX graph for layout
    G = nx.DiGraph()
    
    for _, row in nodes_df.iterrows():
        G.add_node(row['node_id'], **row.to_dict())
    
    for _, row in edges_df.iterrows():
        G.add_edge(row['source'], row['target'], **row.to_dict())
    
    # Compute layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Node colors by type
    node_colors = {
        'supplier': COLORS['primary'],
        'material': COLORS['secondary'],
        'work_order': COLORS['success'],
        'process_step': COLORS['accent'],
        'station': COLORS['purple'],
        'defect': COLORS['critical']
    }
    
    # Create edge traces - convert to native Python types for SiS compatibility
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([float(x0), float(x1), None])
        edge_y.extend([float(y0), float(y1), None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color=COLORS['border']),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create node traces by type
    node_traces = []
    for node_type, color in node_colors.items():
        type_nodes = [n for n, d in G.nodes(data=True) if d.get('node_type') == node_type]
        if not type_nodes:
            continue
        
        # Convert to native Python types for SiS compatibility
        node_x = [float(pos[n][0]) for n in type_nodes]
        node_y = [float(pos[n][1]) for n in type_nodes]
        node_text = [str(G.nodes[n].get('name', n)) for n in type_nodes]
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=node_text,
            name=node_type.replace('_', ' ').title(),
            marker=dict(
                size=10 if node_type != 'defect' else 15,
                color=color,
                line=dict(width=1, color=COLORS['background'])
            )
        )
        node_traces.append(node_trace)
    
    # Create figure
    fig = go.Figure(data=[edge_trace] + node_traces)
    
    fig.update_layout(
        showlegend=True,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    return apply_dark_theme(fig)


def create_sankey_diagram(trace_data, title="Defect Trace"):
    """
    Create Sankey diagram for defect flow visualization.
    
    Args:
        trace_data: Dict with nodes and links for Sankey
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    # Convert to native Python types for SiS compatibility
    labels = [str(l) for l in trace_data.get('labels', [])]
    colors = trace_data.get('colors', [COLORS['primary']] * len(labels))
    source = [int(s) for s in trace_data.get('source', [])]
    target = [int(t) for t in trace_data.get('target', [])]
    value = [float(v) for v in trace_data.get('value', [])]
    
    fig = go.Figure(go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color=COLORS['border'], width=0.5),
            label=labels,
            color=colors
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color='rgba(41, 181, 232, 0.4)'  # Semi-transparent primary
        )
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return apply_dark_theme(fig)


def create_risk_bar_chart(risk_df, category_col, value_col, title, top_n=10):
    """
    Create horizontal bar chart for risk scores.
    
    Args:
        risk_df: DataFrame with risk data
        category_col: Column name for categories (y-axis)
        value_col: Column name for values (x-axis)
        title: Chart title
        top_n: Number of items to show
    
    Returns:
        Plotly Figure
    """
    df = risk_df.head(top_n).sort_values(value_col, ascending=True)
    
    # Convert to native Python types for SiS compatibility
    x_values = [float(v) for v in df[value_col].tolist()]
    y_values = [str(c) for c in df[category_col].tolist()]
    
    # Color bars based on risk level
    colors = []
    for val in x_values:
        if val > 0.7:
            colors.append(COLORS['critical'])
        elif val > 0.4:
            colors.append(COLORS['warning'])
        else:
            colors.append(COLORS['primary'])
    
    fig = go.Figure(go.Bar(
        x=x_values,
        y=y_values,
        orientation='h',
        marker=dict(color=colors),
        text=[f'{v:.2f}' for v in x_values],
        textposition='outside'
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(title='Risk Score', range=[0, 1.1]),
        yaxis=dict(title=''),
        margin=dict(l=150, r=50, t=60, b=40)
    )
    
    return apply_dark_theme(fig)


def create_defect_distribution_chart(defects_df):
    """Create bar chart showing defect distribution by type."""
    counts = defects_df['DEFECT_TYPE'].value_counts()
    
    # Convert to native Python types for SiS compatibility
    x_values = [int(v) for v in counts.values.tolist()]
    y_values = [str(idx) for idx in counts.index.tolist()]
    
    fig = go.Figure(go.Bar(
        x=x_values,
        y=y_values,
        orientation='h',
        marker=dict(color=COLORS['primary'])
    ))
    
    fig.update_layout(
        title='Defects by Type',
        xaxis=dict(title='Count'),
        yaxis=dict(title=''),
        margin=dict(l=200, r=20, t=60, b=40)
    )
    
    return apply_dark_theme(fig)


def create_correlation_heatmap(df, x_col, y_col, value_col, title, annotations=None):
    """
    Create heatmap showing defect concentration across two dimensions.
    
    Args:
        df: DataFrame with the data
        x_col: Column for x-axis categories
        y_col: Column for y-axis categories  
        value_col: Column with values for color intensity
        title: Chart title
        annotations: Optional list of dicts with {'x': x_val, 'y': y_val, 'text': label}
                     to highlight specific cells
    
    Returns:
        Plotly Figure
    """
    # Pivot the data for heatmap
    pivot = df.pivot_table(
        index=y_col, 
        columns=x_col, 
        values=value_col, 
        aggfunc='sum',
        fill_value=0
    )
    
    # Explicitly convert to Python native types for SiS compatibility
    z_values = [[int(val) for val in row] for row in pivot.values.tolist()]
    x_labels = [str(x) for x in pivot.columns.tolist()]
    y_labels = [str(y) for y in pivot.index.tolist()]
    
    # Custom colorscale with visible colors on dark background
    colorscale = [
        [0.0, '#1e3a5f'],                 # Low: visible dark blue (lighter than background)
        [0.25, COLORS['primary']],        # Medium-low: snowflake blue
        [0.5, COLORS['warning']],         # Medium-high: orange
        [1.0, COLORS['critical']]         # High: red
    ]
    
    # Calculate z range for proper color scaling
    z_min = 0
    z_max = max(max(row) for row in z_values) if z_values else 1
    if z_max == 0:
        z_max = 1  # Avoid division by zero in colorscale
    
    fig = go.Figure(go.Heatmap(
        z=z_values,
        x=x_labels,
        y=y_labels,
        zmin=z_min,
        zmax=z_max,
        colorscale=colorscale,
        hovertemplate='%{x}<br>%{y}<br>Defects: %{z}<extra></extra>',
        colorbar=dict(
            title=dict(text='Defect Count', font=dict(color=COLORS['text'])),
            tickfont=dict(color=COLORS['text_secondary'])
        )
    ))
    
    # Add annotations for discovered patterns
    if annotations:
        for ann in annotations:
            if ann['x'] in pivot.columns.tolist() and ann['y'] in pivot.index.tolist():
                x_idx = pivot.columns.tolist().index(ann['x'])
                y_idx = pivot.index.tolist().index(ann['y'])
                fig.add_annotation(
                    x=ann['x'],
                    y=ann['y'],
                    text=ann.get('text', '⚠'),
                    showarrow=True,
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=COLORS['accent'],
                    font=dict(size=12, color=COLORS['accent']),
                    ax=40,
                    ay=-40
                )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(title='', tickangle=45, tickfont=dict(size=10)),
        yaxis=dict(title='', tickfont=dict(size=10)),
        margin=dict(l=150, r=40, t=80, b=120),
        height=500
    )
    
    return apply_dark_theme(fig)


def create_risk_distribution(risk_df, value_col='RISK_SCORE', title='Risk Score Distribution'):
    """
    Create histogram showing risk score distribution with threshold markers.
    
    Args:
        risk_df: DataFrame with risk scores
        value_col: Column name containing risk scores
        title: Chart title
    
    Returns:
        Plotly Figure
    """
    import numpy as np
    
    scores = risk_df[value_col].dropna().values
    
    # Create histogram using numpy to compute bins manually
    fig = go.Figure()
    
    # Define bin edges from 0 to 1
    bin_edges = np.linspace(0, 1, 21)  # 20 bins
    counts, _ = np.histogram(scores, bins=bin_edges)
    
    # Calculate bin centers for bar chart
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    bin_width = bin_edges[1] - bin_edges[0]
    
    # Assign colors based on bin center position
    colors = []
    for center in bin_centers:
        if center <= 0.4:
            colors.append(COLORS['success'])
        elif center <= 0.7:
            colors.append(COLORS['warning'])
        else:
            colors.append(COLORS['critical'])
    
    # Convert to native Python types for SiS compatibility
    bin_centers_list = [float(c) for c in bin_centers.tolist()]
    counts_list = [int(c) for c in counts.tolist()]
    
    # Create bar chart (more reliable than histogram for this use case)
    fig.add_trace(go.Bar(
        x=bin_centers_list,
        y=counts_list,
        width=float(bin_width * 0.9),
        marker=dict(
            color=colors,
            line=dict(width=1, color=COLORS['background'])
        ),
        hovertemplate='Score: %{x:.2f}<br>Count: %{y}<extra></extra>',
        showlegend=False
    ))
    
    # Add legend entries manually
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=10, color=COLORS['success']),
        name='Normal (≤0.4)'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=10, color=COLORS['warning']),
        name='Elevated (0.4-0.7)'
    ))
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(size=10, color=COLORS['critical']),
        name='Critical (>0.7)'
    ))
    
    # Add threshold lines
    fig.add_vline(
        x=0.4, 
        line=dict(color=COLORS['warning'], width=2, dash='dash'),
        annotation_text='Elevated',
        annotation_position='top',
        annotation_font=dict(color=COLORS['warning'], size=10)
    )
    
    fig.add_vline(
        x=0.7, 
        line=dict(color=COLORS['critical'], width=2, dash='dash'),
        annotation_text='Critical',
        annotation_position='top',
        annotation_font=dict(color=COLORS['critical'], size=10)
    )
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis=dict(title='Risk Score', range=[0, 1.05]),
        yaxis=dict(title='Number of Components'),
        showlegend=True,
        legend=dict(orientation='h', y=-0.15),
        margin=dict(l=60, r=40, t=80, b=80),
        height=400
    )
    
    return apply_dark_theme(fig)


def get_risk_color_gradient(risk_score):
    """
    Get color for a risk score on a green-yellow-red gradient.
    
    Args:
        risk_score: Float between 0 and 1
    
    Returns:
        Hex color string
    """
    if risk_score <= 0.4:
        return COLORS['success']
    elif risk_score <= 0.7:
        return COLORS['warning']
    else:
        return COLORS['critical']


def create_network_graph_with_risk_overlay(nodes_df, edges_df, risk_lookup, defect_counts=None):
    """
    Create network graph with nodes colored by risk score.
    
    Args:
        nodes_df: DataFrame with node_id, node_type, name columns
        edges_df: DataFrame with source, target, edge_type columns
        risk_lookup: Dict mapping entity_id -> risk_score
        defect_counts: Optional dict mapping entity_id -> defect count for sizing
    
    Returns:
        Plotly Figure
    """
    # Create NetworkX graph for layout
    G = nx.DiGraph()
    
    for _, row in nodes_df.iterrows():
        G.add_node(row['node_id'], **row.to_dict())
    
    for _, row in edges_df.iterrows():
        G.add_edge(row['source'], row['target'], **row.to_dict())
    
    # Compute layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Create edge trace - convert to native Python types for SiS compatibility
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([float(x0), float(x1), None])
        edge_y.extend([float(y0), float(y1), None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color=COLORS['border']),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    )
    
    # Create node traces - group by risk level for legend
    node_traces = []
    risk_groups = {
        'normal': {'nodes': [], 'color': COLORS['success'], 'name': 'Normal Risk (≤0.4)'},
        'elevated': {'nodes': [], 'color': COLORS['warning'], 'name': 'Elevated Risk (0.4-0.7)'},
        'critical': {'nodes': [], 'color': COLORS['critical'], 'name': 'Critical Risk (>0.7)'},
        'defect': {'nodes': [], 'color': COLORS['critical'], 'name': 'Defect'}
    }
    
    for node in G.nodes():
        node_data = G.nodes[node]
        node_type = node_data.get('node_type', '')
        
        if node_type == 'defect':
            risk_groups['defect']['nodes'].append(node)
        else:
            # Extract entity ID for risk lookup
            entity_id = node.split(':')[1] if ':' in node else node
            risk = risk_lookup.get(entity_id, 0)
            
            if risk > 0.7:
                risk_groups['critical']['nodes'].append(node)
            elif risk > 0.4:
                risk_groups['elevated']['nodes'].append(node)
            else:
                risk_groups['normal']['nodes'].append(node)
    
    for group_key, group_data in risk_groups.items():
        if not group_data['nodes']:
            continue
        
        # Convert to native Python types for SiS compatibility
        node_x = [float(pos[n][0]) for n in group_data['nodes']]
        node_y = [float(pos[n][1]) for n in group_data['nodes']]
        
        # Build hover text
        texts = []
        sizes = []
        for n in group_data['nodes']:
            node_info = G.nodes[n]
            name = str(node_info.get('name', n))
            ntype = str(node_info.get('node_type', 'unknown'))
            entity_id = n.split(':')[1] if ':' in n else n
            risk = float(risk_lookup.get(entity_id, 0))
            defect_ct = int(defect_counts.get(entity_id, 0)) if defect_counts else 0
            
            texts.append(f"{name}<br>Type: {ntype}<br>Risk: {risk:.2f}<br>Defects: {defect_ct}")
            
            # Size based on defect count
            base_size = 15 if group_key == 'defect' else 10
            if defect_counts and entity_id in defect_counts:
                size_boost = min(defect_counts[entity_id] / 5, 10)
                sizes.append(float(base_size + size_boost))
            else:
                sizes.append(float(base_size))
        
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            hoverinfo='text',
            text=texts,
            name=group_data['name'],
            marker=dict(
                size=sizes,
                color=group_data['color'],
                line=dict(width=1, color=COLORS['background'])
            )
        )
        node_traces.append(node_trace)
    
    fig = go.Figure(data=[edge_trace] + node_traces)
    
    fig.update_layout(
        showlegend=True,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(orientation='h', y=-0.05)
    )
    
    return apply_dark_theme(fig)

