"""
GNN Process Traceability - Main Streamlit Application

Snowflake-native dashboard for exploring GNN-based root cause analysis
of manufacturing defects.
"""

import streamlit as st

# Page configuration
st.set_page_config(
    page_title="GNN Process Traceability",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    /* Dark theme background */
    .stApp {
        background-color: #0f172a;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    
    /* Card styling */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        color: #29B5E8;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    
    /* Pattern card styling */
    .pattern-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-left: 4px solid #ef4444;
        border-radius: 0 12px 12px 0;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    
    .pattern-card.warning {
        border-left-color: #f59e0b;
    }
    
    .pattern-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    .pattern-subtitle {
        font-size: 0.875rem;
        color: #94a3b8;
        margin-bottom: 1rem;
    }
    
    /* AI insight card */
    .ai-card {
        background: rgba(59, 130, 246, 0.08);
        border-left: 3px solid #3b82f6;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin-top: 0.5rem;
    }
    
    .ai-label {
        color: #60a5fa;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.25rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


def main():
    # Sidebar branding (navigation is automatic via pages/ directory)
    with st.sidebar:
        st.title("GNN Process Traceability")
        st.markdown("---")
        st.markdown(
            "<p style='color: #64748b; font-size: 0.75rem;'>Powered by Snowflake</p>",
            unsafe_allow_html=True
        )
    
    # Main content - Home/Overview page
    st.title("Manufacturing Quality Intelligence")
    st.markdown("### Graph-based root cause analysis for defect traceability")
    
    # Get session and load summary data
    try:
        from snowflake.snowpark.context import get_active_session
        session = get_active_session()
        
        # Load key metrics
        from utils.data_loader import run_queries_parallel
        from utils.visualizations import create_sankey_diagram, COLORS
        
        queries = {
            'defects': "SELECT COUNT(*) as count FROM DEFECTS",
            'work_orders': "SELECT COUNT(*) as count FROM WORK_ORDERS",
            'suppliers': "SELECT COUNT(*) as count FROM SUPPLIERS",
            'root_causes': "SELECT COUNT(*) as count FROM ROOT_CAUSE_ANALYSIS",
            'patterns': "SELECT * FROM ROOT_CAUSE_ANALYSIS ORDER BY CORRELATION_SCORE DESC LIMIT 2",
            # Manufacturing flow data for Sankey diagram (5 stages)
            # Only include materials that are actually used in process steps
            'supplier_to_material': """
                SELECT 
                    s.NAME as source,
                    m.MATERIAL_TYPE as target,
                    COUNT(*) as flow_count
                FROM MATERIALS m
                JOIN SUPPLIERS s ON m.SUPPLIER_ID = s.SUPPLIER_ID
                WHERE m.MATERIAL_ID IN (SELECT DISTINCT MATERIAL_ID FROM PROCESS_STEPS WHERE MATERIAL_ID IS NOT NULL)
                GROUP BY s.NAME, m.MATERIAL_TYPE
            """,
            'material_to_process': """
                SELECT 
                    m.MATERIAL_TYPE as source,
                    ps.STEP_TYPE as target,
                    COUNT(*) as flow_count
                FROM PROCESS_STEPS ps
                JOIN MATERIALS m ON ps.MATERIAL_ID = m.MATERIAL_ID
                WHERE ps.MATERIAL_ID IS NOT NULL
                GROUP BY m.MATERIAL_TYPE, ps.STEP_TYPE
            """,
            'process_to_product': """
                SELECT 
                    ps.STEP_TYPE as source,
                    wo.PRODUCT_FAMILY as target,
                    COUNT(DISTINCT wo.WORK_ORDER_ID) as flow_count
                FROM PROCESS_STEPS ps
                JOIN WORK_ORDERS wo ON ps.WORK_ORDER_ID = wo.WORK_ORDER_ID
                WHERE ps.MATERIAL_ID IS NOT NULL
                GROUP BY ps.STEP_TYPE, wo.PRODUCT_FAMILY
            """,
            'product_to_defect': """
                SELECT 
                    wo.PRODUCT_FAMILY as source,
                    d.DEFECT_TYPE as target,
                    COUNT(*) as flow_count
                FROM DEFECTS d
                JOIN WORK_ORDERS wo ON d.WORK_ORDER_ID = wo.WORK_ORDER_ID
                GROUP BY wo.PRODUCT_FAMILY, d.DEFECT_TYPE
            """
        }
        
        data = run_queries_parallel(session, queries)
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            count = data.get('work_orders', {}).get('COUNT', [0])
            if hasattr(count, 'iloc'):
                count = count.iloc[0] if len(count) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{count}</div>
                <div class="metric-label">Work Orders</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            count = data.get('defects', {}).get('COUNT', [0])
            if hasattr(count, 'iloc'):
                count = count.iloc[0] if len(count) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{count}</div>
                <div class="metric-label">Defects</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            count = data.get('suppliers', {}).get('COUNT', [0])
            if hasattr(count, 'iloc'):
                count = count.iloc[0] if len(count) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{count}</div>
                <div class="metric-label">Suppliers</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            count = data.get('root_causes', {}).get('COUNT', [0])
            if hasattr(count, 'iloc'):
                count = count.iloc[0] if len(count) > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{count}</div>
                <div class="metric-label">Patterns Found</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Manufacturing Flow Sankey Diagram
        st.markdown("### Manufacturing Supply Chain Flow")
        st.markdown(
            "<p style='color: #94a3b8; margin-bottom: 1rem;'>"
            "End-to-end traceability from suppliers through production to defects"
            "</p>",
            unsafe_allow_html=True
        )
        
        # Build Sankey diagram data from query results
        try:
            supplier_material = data.get('supplier_to_material')
            material_process = data.get('material_to_process')
            process_product = data.get('process_to_product')
            product_defect = data.get('product_to_defect')
            
            if supplier_material is not None and not supplier_material.empty:
                # Collect all unique labels across all 5 stages
                all_labels = []
                label_index = {}
                
                # Stage 1: Supplier names (prefix to distinguish stages)
                supplier_names = supplier_material['SOURCE'].unique().tolist()
                for name in supplier_names:
                    label = f"🏭 {name}"
                    label_index[('supplier', name)] = len(all_labels)
                    all_labels.append(label)
                
                # Stage 2: Material types
                material_types = supplier_material['TARGET'].unique().tolist()
                if material_process is not None and not material_process.empty:
                    material_types = list(set(material_types) | set(material_process['SOURCE'].unique().tolist()))
                for mat in material_types:
                    label = f"📦 {mat.replace('_', ' ').title()}"
                    label_index[('material', mat)] = len(all_labels)
                    all_labels.append(label)
                
                # Stage 3: Process step types
                process_types = []
                if material_process is not None and not material_process.empty:
                    process_types = material_process['TARGET'].unique().tolist()
                if process_product is not None and not process_product.empty:
                    process_types = list(set(process_types) | set(process_product['SOURCE'].unique().tolist()))
                for proc in process_types:
                    label = f"⚙️ {proc.replace('_', ' ').title()}"
                    label_index[('process', proc)] = len(all_labels)
                    all_labels.append(label)
                
                # Stage 4: Product families
                product_families = []
                if process_product is not None and not process_product.empty:
                    product_families = process_product['TARGET'].unique().tolist()
                if product_defect is not None and not product_defect.empty:
                    product_families = list(set(product_families) | set(product_defect['SOURCE'].unique().tolist()))
                for prod in product_families:
                    label = f"🚜 {prod}"
                    label_index[('product', prod)] = len(all_labels)
                    all_labels.append(label)
                
                # Stage 5: Defect types
                defect_types = []
                if product_defect is not None and not product_defect.empty:
                    defect_types = product_defect['TARGET'].unique().tolist()
                for defect in defect_types:
                    label = f"⚠️ {defect.replace('_', ' ').title()}"
                    label_index[('defect', defect)] = len(all_labels)
                    all_labels.append(label)
                
                # Build links
                sources = []
                targets = []
                values = []
                link_colors = []
                
                # Supplier → Material links
                for _, row in supplier_material.iterrows():
                    src_key = ('supplier', row['SOURCE'])
                    tgt_key = ('material', row['TARGET'])
                    if src_key in label_index and tgt_key in label_index:
                        sources.append(label_index[src_key])
                        targets.append(label_index[tgt_key])
                        values.append(int(row['FLOW_COUNT']))
                        link_colors.append('rgba(41, 181, 232, 0.3)')  # Primary blue
                
                # Material → Process links
                if material_process is not None and not material_process.empty:
                    for _, row in material_process.iterrows():
                        src_key = ('material', row['SOURCE'])
                        tgt_key = ('process', row['TARGET'])
                        if src_key in label_index and tgt_key in label_index:
                            sources.append(label_index[src_key])
                            targets.append(label_index[tgt_key])
                            values.append(int(row['FLOW_COUNT']))
                            link_colors.append('rgba(255, 159, 10, 0.3)')  # Orange
                
                # Process → Product links
                if process_product is not None and not process_product.empty:
                    for _, row in process_product.iterrows():
                        src_key = ('process', row['SOURCE'])
                        tgt_key = ('product', row['TARGET'])
                        if src_key in label_index and tgt_key in label_index:
                            sources.append(label_index[src_key])
                            targets.append(label_index[tgt_key])
                            values.append(int(row['FLOW_COUNT']))
                            link_colors.append('rgba(34, 197, 94, 0.3)')  # Green
                
                # Product → Defect links
                if product_defect is not None and not product_defect.empty:
                    for _, row in product_defect.iterrows():
                        src_key = ('product', row['SOURCE'])
                        tgt_key = ('defect', row['TARGET'])
                        if src_key in label_index and tgt_key in label_index:
                            sources.append(label_index[src_key])
                            targets.append(label_index[tgt_key])
                            values.append(int(row['FLOW_COUNT']))
                            link_colors.append('rgba(239, 68, 68, 0.3)')  # Red/critical
                
                # Node colors by stage
                node_colors = []
                for label in all_labels:
                    if label.startswith('🏭'):
                        node_colors.append(COLORS['primary'])
                    elif label.startswith('📦'):
                        node_colors.append(COLORS['secondary'])
                    elif label.startswith('⚙️'):
                        node_colors.append(COLORS['accent'])
                    elif label.startswith('🚜'):
                        node_colors.append(COLORS['success'])
                    else:  # Defects
                        node_colors.append(COLORS['critical'])
                
                # Create Sankey trace data - convert to native Python types for SiS compatibility
                sankey_labels = [str(l) for l in all_labels]
                sankey_sources = [int(s) for s in sources]
                sankey_targets = [int(t) for t in targets]
                sankey_values = [float(v) for v in values]
                
                # Create the Sankey figure with custom link colors
                import plotly.graph_objects as go
                fig = go.Figure(go.Sankey(
                    node=dict(
                        pad=20,
                        thickness=25,
                        line=dict(color=COLORS['border'], width=0.5),
                        label=sankey_labels,
                        color=node_colors
                    ),
                    link=dict(
                        source=sankey_sources,
                        target=sankey_targets,
                        value=sankey_values,
                        color=link_colors
                    )
                ))
                
                fig.update_layout(
                    paper_bgcolor=COLORS['background'],
                    plot_bgcolor=COLORS['background'],
                    font=dict(color=COLORS['text'], family='Helvetica Neue, Arial, sans-serif', size=12),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=450
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Legend for the stages
                legend_cols = st.columns(5)
                with legend_cols[0]:
                    st.markdown(
                        f"<span style='color: {COLORS['primary']};'>●</span> "
                        "<span style='color: #94a3b8; font-size: 0.875rem;'>Suppliers</span>",
                        unsafe_allow_html=True
                    )
                with legend_cols[1]:
                    st.markdown(
                        f"<span style='color: {COLORS['secondary']};'>●</span> "
                        "<span style='color: #94a3b8; font-size: 0.875rem;'>Materials</span>",
                        unsafe_allow_html=True
                    )
                with legend_cols[2]:
                    st.markdown(
                        f"<span style='color: {COLORS['accent']};'>●</span> "
                        "<span style='color: #94a3b8; font-size: 0.875rem;'>Process Steps</span>",
                        unsafe_allow_html=True
                    )
                with legend_cols[3]:
                    st.markdown(
                        f"<span style='color: {COLORS['success']};'>●</span> "
                        "<span style='color: #94a3b8; font-size: 0.875rem;'>Products</span>",
                        unsafe_allow_html=True
                    )
                with legend_cols[4]:
                    st.markdown(
                        f"<span style='color: {COLORS['critical']};'>●</span> "
                        "<span style='color: #94a3b8; font-size: 0.875rem;'>Defects</span>",
                        unsafe_allow_html=True
                    )
            else:
                st.info("📊 Manufacturing flow data not yet available. Run the data loading process first.")
        except Exception as e:
            st.error(f"Failed to load manufacturing flow diagram: {e}")
        
        st.markdown("---")
        
        # Discovered Patterns Section
        st.markdown("### Discovered Root Cause Patterns")
        
        patterns_df = data.get('patterns')
        if patterns_df is not None and not patterns_df.empty:
            col1, col2 = st.columns(2)
            
            for idx, (col, (_, pattern)) in enumerate(zip([col1, col2], patterns_df.iterrows())):
                with col:
                    pattern_type = pattern.get('PATTERN_TYPE', 'Unknown')
                    entity_name = pattern.get('ENTITY_NAME', 'Unknown')
                    score = pattern.get('CORRELATION_SCORE', 0)
                    defect_count = pattern.get('DEFECT_COUNT', 0)
                    description = pattern.get('DESCRIPTION', '')
                    
                    card_class = 'pattern-card' if score > 0.8 else 'pattern-card warning'
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div class="pattern-title">{pattern_type.replace('_', ' ').title()}</div>
                        <div class="pattern-subtitle">{entity_name}</div>
                        <p style="color: #e2e8f0; margin-bottom: 0.5rem;">
                            Correlation: <strong>{score:.0%}</strong> | 
                            Defects: <strong>{defect_count}</strong>
                        </p>
                        <p style="color: #94a3b8; font-size: 0.875rem;">{description[:150]}...</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No patterns discovered yet. Run the GNN analysis notebook first.")
        
        st.markdown("---")
        
        # Quick Actions
        st.markdown("### Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("View Process Network", use_container_width=True):
                st.switch_page("pages/1_Process_Network.py")
        
        with col2:
            if st.button("Trace a Defect", use_container_width=True):
                st.switch_page("pages/2_Defect_Tracing.py")
        
        with col3:
            if st.button("Analyze Risks", use_container_width=True):
                st.switch_page("pages/3_Risk_Analysis.py")
    
    except Exception as e:
        st.error(f"Error connecting to Snowflake: {e}")
        st.info("Make sure you have deployed the application and run the GNN notebook.")


if __name__ == "__main__":
    main()

