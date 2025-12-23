"""
Process Network Intelligence Page

Visualize how GNN analysis discovers root cause patterns in manufacturing data.
Provides interactive visualizations for defect pattern discovery, risk prioritization,
root cause traceability, and algorithm transparency.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import networkx as nx
import json
import traceback

st.set_page_config(page_title="Process Network", page_icon="🔗", layout="wide")

from utils.database import (
    get_session,
    get_defects,
    get_root_cause_analysis,
    get_risk_scores,
    get_suppliers,
    get_stations,
    get_work_orders,
    get_process_steps,
    get_defect_type_supplier_batch,
    get_defect_type_station,
    get_defect_type_paths,
)
from utils.visualizations import (
    COLORS,
    apply_dark_theme,
    create_correlation_heatmap,
    create_risk_distribution,
    create_risk_bar_chart,
    create_sankey_diagram,
    get_risk_color_gradient,
)


def render_kpi_metrics(session):
    """Render the 4-column KPI header row."""
    col1, col2, col3, col4 = st.columns(4)
    
    # Load data for metrics
    try:
        defects_df = get_defects(session)
        total_defects = len(defects_df) if defects_df is not None else 0
    except Exception:
        total_defects = 0
    
    try:
        root_causes_df = get_root_cause_analysis(session)
        discovered_patterns = len(root_causes_df) if root_causes_df is not None else 0
    except Exception:
        discovered_patterns = 0
    
    try:
        risk_df = get_risk_scores(session)
        high_risk = len(risk_df[risk_df['RISK_SCORE'] > 0.7]) if risk_df is not None and not risk_df.empty else 0
    except Exception:
        high_risk = 0
    
    try:
        suppliers_df = get_suppliers(session)
        stations_df = get_stations(session)
        work_orders_df = get_work_orders(session)
        network_nodes = (
            (len(suppliers_df) if suppliers_df is not None else 0) +
            (len(stations_df) if stations_df is not None else 0) +
            (len(work_orders_df) if work_orders_df is not None else 0)
        )
    except Exception:
        network_nodes = 0
    
    with col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%);
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.5rem;">
            <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['primary']};">{total_defects}</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 0.05em;">Total Defects</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%);
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.5rem;">
            <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['accent']};">{discovered_patterns}</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 0.05em;">Discovered Patterns</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%);
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.5rem;">
            <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['critical']};">{high_risk}</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 0.05em;">High Risk Entities</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%);
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.5rem;">
            <div style="font-size: 2.5rem; font-weight: bold; color: {COLORS['success']};">{network_nodes}</div>
            <div style="font-size: 0.875rem; color: {COLORS['text_secondary']}; text-transform: uppercase; letter-spacing: 0.05em;">Network Nodes</div>
        </div>
        """, unsafe_allow_html=True)


def render_discovery_heatmaps(session):
    """Render Tab 1: Discovery Heatmaps."""
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem;">
        <p style="color: {COLORS['text']}; margin: 0;">
            These heatmaps show defect concentration across different dimensions. 
            High-intensity cells (red) indicate potential root cause patterns that warrant investigation.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Heatmap 1: Supplier/Batch vs Defect Type
    st.markdown("### Supplier/Batch vs Defect Type")
    try:
        supplier_batch_df = get_defect_type_supplier_batch(session)
        
        if supplier_batch_df is not None and not supplier_batch_df.empty:
            # Create combined label for y-axis
            supplier_batch_df = supplier_batch_df.copy()
            supplier_batch_df['SUPPLIER_BATCH'] = (
                supplier_batch_df['SUPPLIER_NAME'].fillna('Unknown').astype(str) + 
                ' - Batch ' + 
                supplier_batch_df['BATCH_NUMBER'].fillna('N/A').astype(str)
            )
            
            # Get top 15 by total defect count
            top_combos = (
                supplier_batch_df.groupby('SUPPLIER_BATCH')['DEFECT_COUNT']
                .sum()
                .nlargest(15)
                .index.tolist()
            )
            filtered_df = supplier_batch_df[supplier_batch_df['SUPPLIER_BATCH'].isin(top_combos)]
            
            if not filtered_df.empty:
                fig1 = create_correlation_heatmap(
                    filtered_df,
                    x_col='DEFECT_TYPE',
                    y_col='SUPPLIER_BATCH',
                    value_col='DEFECT_COUNT',
                    title='Defect Concentration: Supplier/Batch vs Defect Type'
                )
                fig1.update_layout(height=450)
                st.plotly_chart(fig1, use_container_width=True)
                st.caption("How to read: Each cell shows defect count for a specific supplier/batch and defect type combination.")
            else:
                st.info("No supplier/batch data available after filtering.")
        else:
            st.warning("No supplier/batch data available. Run the GNN notebook first.")
    except Exception as e:
        if "does not exist" in str(e).lower():
            st.warning("No supplier/batch data available. Run the GNN notebook first.")
        else:
            st.error(f"Error loading supplier/batch data: {e}")
            st.code(traceback.format_exc())
    
    st.markdown("---")
    
    # Heatmap 2: Station/Line vs Product Series
    st.markdown("### Station/Line vs Product Series")
    try:
        station_df = get_defect_type_station(session)
        
        if station_df is not None and not station_df.empty:
            # Create combined label for y-axis
            station_df = station_df.copy()
            station_df['STATION_LINE'] = (
                station_df['STATION_NAME'].fillna('Unknown').astype(str) + 
                ' (' + 
                station_df['LINE'].fillna('N/A').astype(str) + ')'
            )
            
            # Get top 15 by total defect count
            top_stations = (
                station_df.groupby('STATION_LINE')['DEFECT_COUNT']
                .sum()
                .nlargest(15)
                .index.tolist()
            )
            filtered_df = station_df[station_df['STATION_LINE'].isin(top_stations)]
            
            if not filtered_df.empty:
                fig2 = create_correlation_heatmap(
                    filtered_df,
                    x_col='PRODUCT_SERIES',
                    y_col='STATION_LINE',
                    value_col='DEFECT_COUNT',
                    title='Defect Concentration: Station/Line vs Product Series'
                )
                fig2.update_layout(height=450)
                st.plotly_chart(fig2, use_container_width=True)
                st.caption("How to read: Each cell shows defect count for a specific station/line and product series combination.")
            else:
                st.info("No station data available after filtering.")
        else:
            st.warning("No station data available. Run the GNN notebook first.")
    except Exception as e:
        if "does not exist" in str(e).lower():
            st.warning("No station data available. Run the GNN notebook first.")
        else:
            st.error(f"Error loading station data: {e}")
            st.code(traceback.format_exc())


def render_risk_analysis(session):
    """Render Tab 2: Risk Analysis."""
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem;">
        <p style="color: {COLORS['text']}; margin: 0;">
            Risk scores quantify how often a component (supplier, station) is associated with defects 
            relative to its usage. The algorithm flags components exceeding risk thresholds.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        risk_df = get_risk_scores(session)
        
        if risk_df is None or risk_df.empty:
            st.warning("No risk score data available. Run the GNN notebook first.")
            return
        
        left_col, right_col = st.columns(2)
        
        with left_col:
            st.markdown("#### Risk Score Distribution")
            
            # Histogram using create_risk_distribution
            fig_hist = create_risk_distribution(risk_df, 'RISK_SCORE', 'Component Risk Score Distribution')
            fig_hist.update_layout(height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Summary cards
            critical_count = len(risk_df[risk_df['RISK_SCORE'] > 0.7])
            elevated_count = len(risk_df[(risk_df['RISK_SCORE'] > 0.4) & (risk_df['RISK_SCORE'] <= 0.7)])
            normal_count = len(risk_df[risk_df['RISK_SCORE'] <= 0.4])
            
            card_cols = st.columns(3)
            with card_cols[0]:
                st.markdown(f"""
                <div style="background: {COLORS['card']}; border-left: 4px solid {COLORS['critical']}; 
                            border-radius: 0 8px 8px 0; padding: 1rem;">
                    <div style="color: {COLORS['text']}; font-weight: bold;">Critical: {critical_count} components</div>
                </div>
                """, unsafe_allow_html=True)
            with card_cols[1]:
                st.markdown(f"""
                <div style="background: {COLORS['card']}; border-left: 4px solid {COLORS['warning']}; 
                            border-radius: 0 8px 8px 0; padding: 1rem;">
                    <div style="color: {COLORS['text']}; font-weight: bold;">Elevated: {elevated_count} components</div>
                </div>
                """, unsafe_allow_html=True)
            with card_cols[2]:
                st.markdown(f"""
                <div style="background: {COLORS['card']}; border-left: 4px solid {COLORS['success']}; 
                            border-radius: 0 8px 8px 0; padding: 1rem;">
                    <div style="color: {COLORS['text']}; font-weight: bold;">Normal: {normal_count} components</div>
                </div>
                """, unsafe_allow_html=True)
        
        with right_col:
            st.markdown("#### Highest Risk Components")
            
            # Top 10 bar chart
            fig_bar = create_risk_bar_chart(
                risk_df,
                'COMPONENT_NAME',
                'RISK_SCORE',
                'Top 10 Components by Risk Score',
                top_n=10
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # Formula explanation
            st.markdown(f"""
            <div style="background: {COLORS['card']}; border: 1px solid {COLORS['border']}; 
                        border-radius: 8px; padding: 1rem; margin-top: 1rem;">
                <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-bottom: 0.5rem;">
                    <strong>Risk Score Formula:</strong>
                </div>
                <code style="color: {COLORS['primary']};">RiskScore = min(1.0, (DefectCount / UsageCount) × 5)</code>
                <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin-top: 0.75rem;">
                    <strong>Thresholds:</strong><br>
                    • >0.7 Critical: Immediate investigation required<br>
                    • 0.4-0.7 Elevated: Schedule audit<br>
                    • ≤0.4 Normal: Continue monitoring
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        if "does not exist" in str(e).lower():
            st.warning("No risk score data available. Run the GNN notebook first.")
        else:
            st.error(f"Error loading risk data: {e}")


def render_network_graph(session):
    """Render Tab 3: Network Graph."""
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem;">
        <p style="color: {COLORS['text']}; margin: 0;">
            The network graph shows how manufacturing entities connect. Nodes are colored by risk level:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Color legend
    legend_cols = st.columns(4)
    with legend_cols[0]:
        st.markdown(f"🟢 **Green:** Normal Risk (≤0.4)")
    with legend_cols[1]:
        st.markdown(f"🟡 **Yellow/Orange:** Elevated Risk (0.4-0.7)")
    with legend_cols[2]:
        st.markdown(f"🔴 **Red:** Critical Risk (>0.7)")
    with legend_cols[3]:
        st.markdown(f"🔴 **Red (large):** Defect nodes")
    
    st.markdown("")
    
    # Slider for work order sample size
    sample_size = st.slider(
        "Work Orders to Display",
        min_value=10,
        max_value=100,
        value=50,
        step=10,
        help="Control graph complexity by sampling work orders"
    )
    
    try:
        # Load data
        suppliers_df = get_suppliers(session)
        stations_df = get_stations(session)
        work_orders_df = get_work_orders(session)
        defects_df = get_defects(session)
        process_steps_df = get_process_steps(session)
        
        try:
            risk_df = get_risk_scores(session)
            risk_lookup = dict(zip(risk_df['COMPONENT_ID'].astype(str), risk_df['RISK_SCORE'])) if risk_df is not None and not risk_df.empty else {}
        except Exception:
            risk_lookup = {}
        
        if work_orders_df is None or work_orders_df.empty:
            st.warning("No work order data available.")
            return
        
        # Sample work orders
        sampled_wos = work_orders_df.sample(n=min(sample_size, len(work_orders_df)), random_state=42)
        wo_ids = set(sampled_wos['WORK_ORDER_ID'].astype(str).tolist())
        
        # Build graph
        G = nx.DiGraph()
        
        # Track which entities are actually used
        used_suppliers = set()
        used_stations = set()
        
        # Add work order nodes
        for _, wo in sampled_wos.iterrows():
            wo_id = str(wo['WORK_ORDER_ID'])
            G.add_node(f"wo:{wo_id}", node_type='work_order', name=f"WO-{wo_id[:8]}", layer=2)
        
        # Add defect nodes and edges from work orders
        if defects_df is not None and not defects_df.empty:
            for _, defect in defects_df.iterrows():
                wo_id = str(defect['WORK_ORDER_ID'])
                if wo_id in wo_ids:
                    defect_id = str(defect['DEFECT_ID'])
                    G.add_node(f"defect:{defect_id}", node_type='defect', name=defect['DEFECT_TYPE'], layer=3)
                    G.add_edge(f"wo:{wo_id}", f"defect:{defect_id}", edge_type='resulted_in')
        
        # Add process steps to connect suppliers and stations
        if process_steps_df is not None and not process_steps_df.empty:
            for _, step in process_steps_df.iterrows():
                wo_id = str(step['WORK_ORDER_ID'])
                if wo_id in wo_ids:
                    station_id = str(step['STATION_ID']) if pd.notna(step.get('STATION_ID')) else None
                    if station_id:
                        used_stations.add(station_id)
                        G.add_edge(f"station:{station_id}", f"wo:{wo_id}", edge_type='processed_at')
        
        # Add station nodes
        if stations_df is not None and not stations_df.empty:
            for _, station in stations_df.iterrows():
                station_id = str(station['STATION_ID'])
                if station_id in used_stations:
                    G.add_node(f"station:{station_id}", node_type='station', name=station['NAME'], layer=1)
        
        # Add supplier connections via materials (simplified - connect suppliers to work orders)
        if suppliers_df is not None and not suppliers_df.empty:
            # For simplicity, connect each supplier to a subset of work orders based on existing relationships
            for _, supplier in suppliers_df.iterrows():
                supplier_id = str(supplier['SUPPLIER_ID'])
                supplier_name = supplier['NAME']
                # Check if this supplier is used
                if supplier_id in used_suppliers or len(used_suppliers) < 5:
                    used_suppliers.add(supplier_id)
                    G.add_node(f"supplier:{supplier_id}", node_type='supplier', name=supplier_name, layer=0)
                    # Connect to some work orders (simplified relationship)
                    for wo_id in list(wo_ids)[:3]:  # Connect to first 3 sampled WOs
                        G.add_edge(f"supplier:{supplier_id}", f"wo:{wo_id}", edge_type='supplied_material')
        
        if len(G.nodes()) == 0:
            st.warning("Unable to build network graph. Check data availability.")
            return
        
        # Compute multipartite layout
        pos = nx.multipartite_layout(G, subset_key='layer', align='horizontal')
        
        # Create edge traces
        edge_x = []
        edge_y = []
        defect_edge_x = []
        defect_edge_y = []
        
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            # Convert to native Python types for SiS compatibility
            if edge[2].get('edge_type') == 'resulted_in':
                defect_edge_x.extend([float(x0), float(x1), None])
                defect_edge_y.extend([float(y0), float(y1), None])
            else:
                edge_x.extend([float(x0), float(x1), None])
                edge_y.extend([float(y0), float(y1), None])
        
        # Create figure
        fig = go.Figure()
        
        # Normal edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color=COLORS['border']),
            hoverinfo='none',
            mode='lines',
            showlegend=False
        ))
        
        # Defect path edges (thicker, red-tinted)
        if defect_edge_x:
            fig.add_trace(go.Scatter(
                x=defect_edge_x, y=defect_edge_y,
                line=dict(width=1.5, color='rgba(239, 68, 68, 0.5)'),
                hoverinfo='none',
                mode='lines',
                showlegend=False
            ))
        
        # Create node traces by type and risk level
        node_groups = {
            'supplier': {'nodes': [], 'color': COLORS['primary'], 'name': 'Suppliers', 'size': 10},
            'station': {'nodes': [], 'color': COLORS['purple'], 'name': 'Stations', 'size': 10},
            'work_order': {'nodes': [], 'color': COLORS['success'], 'name': 'Work Orders', 'size': 8},
            'defect': {'nodes': [], 'color': COLORS['critical'], 'name': 'Defects', 'size': 15},
        }
        
        for node, data in G.nodes(data=True):
            node_type = data.get('node_type', 'unknown')
            if node_type in node_groups:
                # Get risk score for coloring (except defects which are always red)
                if node_type != 'defect' and node_type != 'work_order':
                    entity_id = node.split(':')[1] if ':' in node else node
                    risk_score = risk_lookup.get(entity_id, 0)
                    color = get_risk_color_gradient(risk_score)
                else:
                    color = node_groups[node_type]['color']
                    risk_score = 1.0 if node_type == 'defect' else 0
                
                node_groups[node_type]['nodes'].append({
                    'node': node,
                    'pos': pos[node],
                    'name': data.get('name', node),
                    'color': color,
                    'risk': risk_score
                })
        
        # Add node traces
        for node_type, group in node_groups.items():
            if not group['nodes']:
                continue
            
            # Convert to native Python types for SiS compatibility
            node_x = [float(n['pos'][0]) for n in group['nodes']]
            node_y = [float(n['pos'][1]) for n in group['nodes']]
            colors = [str(n['color']) for n in group['nodes']]
            texts = [f"{str(n['name'])}<br>Type: {node_type.replace('_', ' ').title()}<br>Risk: {float(n['risk']):.2f}" for n in group['nodes']]
            
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=texts,
                name=group['name'],
                marker=dict(
                    size=group['size'],
                    color=colors,
                    line=dict(width=1, color=COLORS['background'])
                )
            ))
        
        fig.update_layout(
            showlegend=True,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=20, r=20, t=40, b=60),
            height=600,
            legend=dict(orientation='h', y=-0.05)
        )
        
        apply_dark_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        st.caption("Graph Structure: Supplier → Work Order → Defect | Station → Work Order. Node size reflects entity type. Hover for details.")
    
    except Exception as e:
        st.error(f"Unable to render graph: {e}")
        st.info("Check data availability.")


def render_algorithm_trace(session):
    """Render Tab 4: Algorithm Trace - shows step-by-step how patterns are discovered."""
    st.markdown("### How Patterns Are Discovered")
    
    st.markdown(f"""
    <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid {COLORS['primary']}; 
                padding: 1rem; border-radius: 0 8px 8px 0; margin-bottom: 1.5rem;">
        <p style="color: {COLORS['text']}; margin: 0;">
            The GNN algorithm traces defects backwards through the manufacturing graph to identify 
            correlated root causes. Here's the step-by-step process for each discovered pattern:
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        root_causes_df = get_root_cause_analysis(session)
        
        if root_causes_df is None or root_causes_df.empty:
            st.warning("No root cause patterns discovered yet. Run the GNN notebook to generate analysis.")
            return
        
        # Load path data for Sankey diagrams
        try:
            paths_df = get_defect_type_paths(session)
        except Exception:
            paths_df = None
        
        # Display each pattern
        for idx, (_, pattern) in enumerate(root_causes_df.iterrows()):
            entity_name = pattern.get('ENTITY_NAME', 'Unknown')
            entity_type = pattern.get('ENTITY_TYPE', 'unknown')
            correlation_score = pattern.get('CORRELATION_SCORE', 0)
            defect_count = pattern.get('DEFECT_COUNT', 0)
            affected_wo = pattern.get('AFFECTED_WORK_ORDERS', 0)
            defect_type = pattern.get('DEFECT_TYPE', 'Unknown')
            description = pattern.get('DESCRIPTION', '')
            
            # Determine border color based on correlation score
            border_color = COLORS['critical'] if correlation_score > 0.8 else COLORS['warning']
            
            # Pattern Header Card (self-contained)
            st.markdown(f"""
            <div style="background: {COLORS['card']}; border-left: 4px solid {border_color}; 
                        border-radius: 0 12px 12px 0; padding: 1.5rem; margin-bottom: 1rem;">
                <h4 style="color: {COLORS['text']}; margin: 0;">
                    🎯 Pattern: {entity_name}
                </h4>
            </div>
            """, unsafe_allow_html=True)
            
            # Step 1: Identify Defect Cluster
            st.markdown(f"""
            <div style="color: {COLORS['primary']}; font-weight: bold; margin-bottom: 0.5rem;">
                Step 1: Identify Defect Cluster
            </div>
            """, unsafe_allow_html=True)
            
            metric_cols = st.columns(3)
            with metric_cols[0]:
                st.metric("Defects Found", defect_count)
            with metric_cols[1]:
                st.metric("Affected Work Orders", affected_wo)
            with metric_cols[2]:
                st.metric("Primary Defect Type", defect_type)
            
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid {COLORS['secondary']}; 
                        padding: 0.75rem; border-radius: 0 8px 8px 0; margin-top: 0.5rem; margin-bottom: 1.5rem;">
                <strong>Algorithm Action:</strong> Scan all defects and group by work order. 
                Identified {defect_count} defects affecting {affected_wo} work orders.
            </div>
            """, unsafe_allow_html=True)
            
            # Step 2: Trace Back Through Graph
            st.markdown(f"""
            <div style="color: {COLORS['primary']}; font-weight: bold; margin-bottom: 0.5rem;">
                Step 2: Trace Back Through Graph
            </div>
            """, unsafe_allow_html=True)
            
            if entity_type == 'material_batch':
                path_text = "Defect → Work Order → Process Step → Material → Supplier"
                action_steps = [
                    "Find all process steps in the work order",
                    "Identify materials used in each step",
                    "Look up supplier and batch for each material",
                    "Aggregate counts by (Supplier, Batch) combinations"
                ]
            else:  # station
                path_text = "Defect → Work Order → Process Step → Station"
                action_steps = [
                    "Find all process steps in the work order",
                    "Identify the station for each step",
                    "Also capture product series from work order",
                    "Aggregate counts by (Station, Product Series) combinations"
                ]
            
            # Path visualization box (self-contained)
            st.markdown(f"""
            <div style="background: {COLORS['background']}; border: 1px solid {COLORS['border']}; 
                        border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem; text-align: center;">
                <code style="color: {COLORS['accent']}; font-size: 1rem;">{path_text}</code>
            </div>
            """, unsafe_allow_html=True)
            
            # Algorithm action list (self-contained)
            action_html = "".join([f"<li>{step}</li>" for step in action_steps])
            st.markdown(f"""
            <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-bottom: 1rem;">
                <strong>Algorithm Action:</strong>
                <ol style="margin: 0.5rem 0 0 1.5rem; padding: 0;">{action_html}</ol>
            </div>
            """, unsafe_allow_html=True)
            
            # Sankey Diagram for trace visualization
            if paths_df is not None and not paths_df.empty and defect_type:
                pattern_paths = paths_df[paths_df['DEFECT_TYPE'] == defect_type]
                if not pattern_paths.empty:
                    sankey_data = _build_sankey_data(pattern_paths, entity_type)
                    if sankey_data and sankey_data.get('labels'):
                        fig = create_sankey_diagram(sankey_data, title=f"Trace Path: {defect_type}")
                        fig.update_layout(height=300, margin=dict(l=20, r=20, t=40, b=20))
                        st.plotly_chart(fig, use_container_width=True)
            
            # Step 3: Aggregation & Correlation
            st.markdown(f"""
            <div style="color: {COLORS['primary']}; font-weight: bold; margin-bottom: 0.5rem;">
                Step 3: Aggregation & Correlation
            </div>
            """, unsafe_allow_html=True)
            
            # Discovery box (self-contained)
            st.markdown(f"""
            <div style="background: rgba(255, 159, 10, 0.1); border: 1px solid {COLORS['accent']}; 
                        border-radius: 8px; padding: 1rem; margin-bottom: 0.75rem;">
                <span style="color: {COLORS['accent']};">🔍 Discovery:</span> 
                <span style="color: {COLORS['text']};">{description}</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Correlation score progress bar (self-contained)
            pct = int(correlation_score * 100)
            st.markdown(f"""
            <div style="background: {COLORS['background']}; border-radius: 8px; height: 24px; 
                        border: 1px solid {COLORS['border']}; overflow: hidden; margin-bottom: 0.5rem;">
                <div style="background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent']}); 
                            width: {pct}%; height: 100%;"></div>
            </div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin-bottom: 1.5rem;">
                {pct}% of defects in this category trace back to this entity. (Threshold for pattern detection: &gt;70%)
            </div>
            """, unsafe_allow_html=True)
            
            # Step 4: Generated Recommendations
            st.markdown(f"""
            <div style="color: {COLORS['primary']}; font-weight: bold; margin-bottom: 0.5rem;">
                Step 4: Generated Recommendations
            </div>
            """, unsafe_allow_html=True)
            
            try:
                recs_raw = pattern.get('RECOMMENDATIONS', '[]')
                if isinstance(recs_raw, list):
                    recs = recs_raw
                elif isinstance(recs_raw, str):
                    try:
                        recs = json.loads(recs_raw)
                    except json.JSONDecodeError:
                        recs = []
                else:
                    recs = []
                
                if recs and isinstance(recs, list):
                    recs_html = ""
                    for rec in recs:
                        if isinstance(rec, str) and len(rec) > 1:
                            recs_html += f"<li style='margin-bottom: 0.5rem;'>{rec}</li>"
                    
                    if recs_html:
                        st.markdown(f"""
                        <div style="background: {COLORS['background']}; border: 1px solid {COLORS['border']}; 
                                    border-radius: 8px; padding: 1rem;">
                            <ol style="color: {COLORS['text']}; margin: 0; padding-left: 1.5rem;">
                                {recs_html}
                            </ol>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"<p style='color: {COLORS['text_secondary']};'>No specific recommendations available.</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<p style='color: {COLORS['text_secondary']};'>No specific recommendations available.</p>", unsafe_allow_html=True)
            except Exception:
                st.markdown(f"<p style='color: {COLORS['text_secondary']};'>Unable to parse recommendations.</p>", unsafe_allow_html=True)
            
            # Separator between patterns
            if idx < len(root_causes_df) - 1:
                st.markdown("---")
    
    except Exception as e:
        if "does not exist" in str(e).lower():
            st.warning("No root cause patterns discovered yet. Run the GNN notebook to generate analysis.")
        else:
            st.error(f"Error loading root cause analysis: {e}")


def _build_sankey_data(paths_df, entity_type):
    """Build Sankey diagram data from path edges DataFrame."""
    if paths_df is None or paths_df.empty:
        return None
    
    # Collect unique labels and build index mapping
    labels = []
    label_to_idx = {}
    
    def get_or_add_label(label, node_type):
        """Get index for a label, adding it if needed."""
        key = f"{node_type}:{label}"
        if key not in label_to_idx:
            label_to_idx[key] = len(labels)
            labels.append(str(label))
        return label_to_idx[key]
    
    source_indices = []
    target_indices = []
    values = []
    
    # Define which node types to include based on entity type
    if entity_type == 'material_batch':
        include_types = {'supplier', 'material', 'work_order', 'defect_type'}
    else:
        include_types = {'station', 'work_order', 'defect_type'}
    
    for _, row in paths_df.iterrows():
        src_type = row.get('SOURCE_TYPE', '')
        tgt_type = row.get('TARGET_TYPE', '')
        
        # Filter to relevant node types
        if src_type not in include_types or tgt_type not in include_types:
            continue
        
        src_label = row.get('SOURCE_LABEL', row.get('SOURCE_ID', 'Unknown'))
        tgt_label = row.get('TARGET_LABEL', row.get('TARGET_ID', 'Unknown'))
        val = row.get('VALUE', 1)
        
        src_idx = get_or_add_label(src_label, src_type)
        tgt_idx = get_or_add_label(tgt_label, tgt_type)
        
        source_indices.append(src_idx)
        target_indices.append(tgt_idx)
        values.append(float(val))
    
    if not labels or not source_indices:
        return None
    
    # Assign colors based on node type (heuristic based on label position)
    colors = []
    for label in labels:
        # Simple heuristic: earlier labels are sources (blue), later are targets (orange/red)
        idx = labels.index(label)
        ratio = idx / max(len(labels) - 1, 1)
        if ratio < 0.33:
            colors.append(COLORS['primary'])
        elif ratio < 0.66:
            colors.append(COLORS['accent'])
        else:
            colors.append(COLORS['critical'])
    
    return {
        'labels': labels,
        'colors': colors,
        'source': source_indices,
        'target': target_indices,
        'value': values
    }


# Main page content
try:
    st.title("🔗 Process Network Intelligence")
    st.markdown("Visualize how GNN analysis discovers root cause patterns in manufacturing data.")
    
    session = get_session()
    
    # Render KPI metrics header
    render_kpi_metrics(session)
    
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔥 Discovery Heatmaps",
        "📊 Risk Analysis", 
        "🕸️ Network Graph",
        "🔬 Algorithm Trace"
    ])
    
    with tab1:
        render_discovery_heatmaps(session)
    
    with tab2:
        render_risk_analysis(session)
    
    with tab3:
        render_network_graph(session)
    
    with tab4:
        render_algorithm_trace(session)

except Exception as e:
    st.error(f"Error: {e}")
    st.code(traceback.format_exc())
    st.info("Make sure you have deployed the application and run the GNN notebook.")

