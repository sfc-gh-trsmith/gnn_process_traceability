"""
About Page - Comprehensive solution documentation for dual audience.

Serves both business stakeholders (Executive Overview) and data science
practitioners (Technical Deep-Dive) with tabbed content.
"""

import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

from utils.visualizations import COLORS

# ==============================================================================
# 1. HEADER
# ==============================================================================
st.title("About GNN Process Traceability")
st.markdown("*Graph-based root cause analysis for manufacturing quality intelligence*")

st.divider()

# ==============================================================================
# 2. OVERVIEW (Problem + Solution)
# ==============================================================================
st.header("Overview")

col_problem, col_solution = st.columns([2, 1])

with col_problem:
    st.subheader("The Problem")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']};">
        <p style="color: {COLORS['text']}; line-height: 1.7; margin-bottom: 1rem;">
            When a quality defect emerges in heavy industrial equipment, quality engineers face 
            <strong>2-4 weeks of investigation</strong> to trace it back through thousands of components, 
            hundreds of suppliers, and dozens of process steps—often <strong>without finding the true root cause</strong>.
        </p>
        <p style="color: {COLORS['text']}; line-height: 1.7; margin-bottom: 1rem;">
            Traditional analysis examines each defect in isolation, looking for single-variable correlations. 
            But real root causes are often <strong>paths through the manufacturing network</strong>—a specific 
            material batch from a specific supplier, processed on a specific station with specific parameters.
        </p>
        <p style="color: {COLORS['text_secondary']}; line-height: 1.7; margin: 0; font-size: 0.9rem;">
            <strong>The cost:</strong> $1.2M annual warranty claims per plant, repeat defects that could have been 
            predicted, and quality engineers spending weeks on investigations that end inconclusively.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_solution:
    st.subheader("The Solution")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']};">
        <ul style="color: {COLORS['text']}; line-height: 1.8; padding-left: 1.25rem; margin: 0;">
            <li><strong>Root cause discovery in minutes</strong> instead of weeks</li>
            <li><strong>Multi-hop pattern detection</strong> across suppliers, materials, and stations</li>
            <li><strong>Proactive risk scoring</strong> for all components</li>
            <li><strong>AI-powered explanations</strong> via Cortex AI</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 3. DATA ARCHITECTURE
# ==============================================================================
st.header("Data Architecture")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; min-height: 280px;">
        <span style="background: #1e40af; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">BRONZE LAYER</span>
        <h4 style="color: {COLORS['text']}; margin: 1rem 0 0.75rem 0;">Source Data</h4>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">SUPPLIERS</strong> — Vendor master data with quality ratings</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">MATERIALS</strong> — Material inventory with batch tracking</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">WORK_ORDERS</strong> — Production orders by product family</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">PROCESS_STEPS</strong> — Manufacturing operations</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">PROCESS_PARAMETERS</strong> — Temperature, pressure, duration</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">STATIONS</strong> — Manufacturing equipment</p>
            <p style="margin-bottom: 0;"><strong style="color: {COLORS['text']};">DEFECTS</strong> — Quality issues with severity</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; min-height: 280px;">
        <span style="background: #b45309; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">SILVER LAYER</span>
        <h4 style="color: {COLORS['text']}; margin: 1rem 0 0.75rem 0;">GNN Processing</h4>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">Graph Construction</strong> — Build heterogeneous manufacturing network</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">Defect Tracing</strong> — Traverse paths from defects to root causes</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">Pattern Discovery</strong> — Identify correlated supplier/station patterns</p>
            <p style="margin-bottom: 0;"><strong style="color: {COLORS['text']};">Risk Scoring</strong> — Compute normalized risk scores for all components</p>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin-top: 1rem; margin-bottom: 0; border-top: 1px solid {COLORS['border']}; padding-top: 0.75rem;">
            Runs in <strong>Snowflake Notebook</strong> with NetworkX graph analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; min-height: 280px;">
        <span style="background: #166534; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">GOLD LAYER</span>
        <h4 style="color: {COLORS['text']}; margin: 1rem 0 0.75rem 0;">Analysis Outputs</h4>
        <div style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">ROOT_CAUSE_ANALYSIS</strong> — Identified patterns with correlation scores</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">COMPONENT_RISK_SCORES</strong> — Risk scores for suppliers and stations</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">DEFECT_TYPE_SUPPLIER_BATCH</strong> — Supplier/batch correlations</p>
            <p style="margin-bottom: 0.5rem;"><strong style="color: {COLORS['text']};">DEFECT_TYPE_STATION</strong> — Station hot spots</p>
            <p style="margin-bottom: 0;"><strong style="color: {COLORS['text']};">DEFECT_TYPE_PATH_EDGES</strong> — Sankey flow data</p>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin-top: 1rem; margin-bottom: 0; border-top: 1px solid {COLORS['border']}; padding-top: 0.75rem;">
            Refreshed on each notebook execution
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 4. HOW IT WORKS (Tabbed)
# ==============================================================================
st.header("How It Works")

exec_tab, tech_tab = st.tabs(["Executive Overview", "Technical Deep-Dive"])

with exec_tab:
    # The Iceberg Problem
    st.markdown("### The Iceberg Problem")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; margin-bottom: 1.5rem;">
        <p style="color: {COLORS['text']}; line-height: 1.7; margin-bottom: 1rem;">
            Think of your manufacturing data as an <strong>iceberg</strong>. Traditional analysis shows you the 
            <strong>10% above the waterline</strong>—individual defects examined one at a time. But <strong>90% of 
            your insight</strong> lies below: the interconnected relationships between suppliers, material batches, 
            process parameters, and equipment configurations.
        </p>
        <p style="color: {COLORS['text']}; line-height: 1.7; margin: 0;">
            GNN Process Traceability dives beneath the surface, modeling your entire manufacturing process as a 
            connected network where patterns emerge from <strong>paths</strong>, not just individual data points.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Approach Comparison
    st.markdown("### Why Traditional Approaches Fall Short")
    
    comp_col1, comp_col2, comp_col3 = st.columns(3)
    
    with comp_col1:
        st.markdown(f"""
        <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; min-height: 200px;">
            <h5 style="color: {COLORS['critical']}; margin-bottom: 0.75rem;">❌ Traditional Analysis</h5>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; line-height: 1.6; margin: 0;">
                Score each supplier independently based on financial health, location risk, and delivery history. 
                Examine each defect in isolation.
            </p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin-top: 1rem; margin-bottom: 0; border-top: 1px solid {COLORS['border']}; padding-top: 0.75rem;">
                <strong>Limitation:</strong> Completely misses network effects where multiple factors combine.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with comp_col2:
        st.markdown(f"""
        <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; min-height: 200px;">
            <h5 style="color: {COLORS['warning']}; margin-bottom: 0.75rem;">⚠️ Manual Investigation</h5>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; line-height: 1.6; margin: 0;">
                Quality engineers manually trace each defect through spreadsheets and ERP queries. 
                Survey suppliers about their sources.
            </p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin-top: 1rem; margin-bottom: 0; border-top: 1px solid {COLORS['border']}; padding-top: 0.75rem;">
                <strong>Limitation:</strong> Expensive, slow (2-4 weeks), incomplete. Data is outdated by investigation time.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with comp_col3:
        st.markdown(f"""
        <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; min-height: 200px;">
            <h5 style="color: {COLORS['success']}; margin-bottom: 0.75rem;">✓ GNN Approach</h5>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; line-height: 1.6; margin: 0;">
                Model manufacturing as a connected graph. Trace defects back through the network automatically. 
                Discover hidden patterns across dimensions.
            </p>
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin-top: 1rem; margin-bottom: 0; border-top: 1px solid {COLORS['border']}; padding-top: 0.75rem;">
                <strong>Advantage:</strong> Automated, scalable, finds multi-hop patterns in minutes.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Business Value Cards
    st.markdown("### Business Value")
    
    val_col1, val_col2, val_col3, val_col4 = st.columns(4)
    
    with val_col1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%); 
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.25rem; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚡</div>
            <div style="color: {COLORS['primary']}; font-weight: 600; margin-bottom: 0.25rem;">Early Warning</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Identify risks before they cascade</div>
        </div>
        """, unsafe_allow_html=True)
    
    with val_col2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%); 
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.25rem; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔗</div>
            <div style="color: {COLORS['accent']}; font-weight: 600; margin-bottom: 0.25rem;">Multi-Hop Visibility</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Discover hidden dependencies</div>
        </div>
        """, unsafe_allow_html=True)
    
    with val_col3:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%); 
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.25rem; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
            <div style="color: {COLORS['purple']}; font-weight: 600; margin-bottom: 0.25rem;">Quantified Risk</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">Data-driven prioritization</div>
        </div>
        """, unsafe_allow_html=True)
    
    with val_col4:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, {COLORS['card']} 0%, {COLORS['background']} 100%); 
                    border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 1.25rem; text-align: center;">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🤖</div>
            <div style="color: {COLORS['success']}; font-weight: 600; margin-bottom: 0.25rem;">Automated Discovery</div>
            <div style="color: {COLORS['text_secondary']}; font-size: 0.8rem;">AI finds patterns humans miss</div>
        </div>
        """, unsafe_allow_html=True)

with tech_tab:
    # Graph Definition
    st.markdown("### Heterogeneous Graph Structure")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; margin-bottom: 1.5rem;">
        <p style="color: {COLORS['text']}; line-height: 1.7; margin-bottom: 1rem;">
            The manufacturing process is modeled as a <strong>heterogeneous directed graph</strong>:
        </p>
        <div style="background: {COLORS['background']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 1rem; font-family: monospace; margin-bottom: 1rem;">
            <span style="color: {COLORS['primary']};">G = (V, E, τ, φ)</span>
        </div>
        <ul style="color: {COLORS['text_secondary']}; line-height: 1.8; padding-left: 1.25rem; margin: 0;">
            <li><strong style="color: {COLORS['text']};">V</strong> = Set of all nodes (suppliers, materials, work orders, steps, stations, defects)</li>
            <li><strong style="color: {COLORS['text']};">E ⊆ V × V</strong> = Set of directed edges representing relationships</li>
            <li><strong style="color: {COLORS['text']};">τ: V → T</strong> = Node type function mapping to {{supplier, material, work_order, process_step, station, defect}}</li>
            <li><strong style="color: {COLORS['text']};">φ: E → R</strong> = Edge type function mapping to {{supplies, used_in, has_step, executed_at, resulted_in}}</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Node and Edge Types
    node_col, edge_col = st.columns(2)
    
    with node_col:
        st.markdown("#### Node Types")
        st.markdown(f"""
        <div style="background: {COLORS['card']}; border-radius: 8px; padding: 1rem; border: 1px solid {COLORS['border']};">
            <table style="width: 100%; color: {COLORS['text']}; font-size: 0.875rem;">
                <tr style="border-bottom: 1px solid {COLORS['border']};">
                    <th style="text-align: left; padding: 0.5rem; color: {COLORS['text_secondary']};">Type</th>
                    <th style="text-align: left; padding: 0.5rem; color: {COLORS['text_secondary']};">Description</th>
                </tr>
                <tr><td style="padding: 0.5rem;"><strong>Supplier</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Vendor master with quality ratings</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>Material</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Parts with batch tracking</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>Work Order</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Production orders by product</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>Process Step</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Manufacturing operations</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>Station</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Equipment by line</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>Defect</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Quality issues with severity</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    with edge_col:
        st.markdown("#### Edge Types")
        st.markdown(f"""
        <div style="background: {COLORS['card']}; border-radius: 8px; padding: 1rem; border: 1px solid {COLORS['border']};">
            <table style="width: 100%; color: {COLORS['text']}; font-size: 0.875rem;">
                <tr style="border-bottom: 1px solid {COLORS['border']};">
                    <th style="text-align: left; padding: 0.5rem; color: {COLORS['text_secondary']};">Type</th>
                    <th style="text-align: left; padding: 0.5rem; color: {COLORS['text_secondary']};">Relationship</th>
                </tr>
                <tr><td style="padding: 0.5rem;"><strong>SUPPLIES</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Supplier → Material</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>USED_IN</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Material → Process Step</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>HAS_STEP</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Work Order → Process Step</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>EXECUTED_AT</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Process Step → Station</td></tr>
                <tr><td style="padding: 0.5rem;"><strong>RESULTED_IN</strong></td><td style="padding: 0.5rem; color: {COLORS['text_secondary']};">Work Order → Defect</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("")
    
    # Graph Architecture
    st.markdown("#### Graph Architecture")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; margin-bottom: 1.5rem;">
        <pre style="color: {COLORS['primary']}; background: {COLORS['background']}; padding: 1rem; border-radius: 8px; overflow-x: auto; margin: 0; font-size: 0.875rem;">
Supplier ──supplies──► Material ──used_in──► Process Step ──executed_at──► Station
                                                   ▲
                                                   │ has_step
                                                   │
                               Work Order ─────────┴──resulted_in──► Defect
        </pre>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-top: 1rem; margin-bottom: 0;">
            The graph enables multi-hop path analysis to discover patterns like:<br>
            • <strong>Supplier → Material → Step → Defect</strong> (material quality issues)<br>
            • <strong>Work Order → Step → Station → Defect</strong> (equipment configuration issues)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Risk Score Formula
    st.markdown("#### Risk Score Computation")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; margin-bottom: 1.5rem;">
        <div style="background: {COLORS['background']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 1rem; font-family: monospace; text-align: center; margin-bottom: 1rem;">
            <span style="color: {COLORS['primary']}; font-size: 1.1rem;">RiskScore(c) = min(1.0, (DefectCount(c) / UsageCount(c)) × 5)</span>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-bottom: 0.75rem;">
            Where <strong style="color: {COLORS['text']};">c</strong> = component (supplier or station), 
            <strong style="color: {COLORS['text']};">DefectCount(c)</strong> = number of defects traced to this component, 
            <strong style="color: {COLORS['text']};">UsageCount(c)</strong> = number of work orders using this component.
        </p>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-bottom: 0;">
            <strong>Interpretation Thresholds:</strong><br>
            • <span style="color: {COLORS['critical']};">▸ &gt;0.7 Critical</span> — Immediate investigation required<br>
            • <span style="color: {COLORS['warning']};">▸ 0.4-0.7 Elevated</span> — Schedule audit<br>
            • <span style="color: {COLORS['success']};">▸ &lt;0.4 Normal</span> — Continue monitoring
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Defect Tracing Algorithm
    st.markdown("#### Defect Tracing Algorithm")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']};">
        <p style="color: {COLORS['text']}; line-height: 1.7; margin-bottom: 1rem;">
            For each defect, the algorithm performs a <strong>backward graph traversal</strong> to identify all upstream entities:
        </p>
        <ol style="color: {COLORS['text_secondary']}; line-height: 1.8; padding-left: 1.5rem; margin-bottom: 1rem;">
            <li>Find the <strong>work order</strong> that resulted in this defect (predecessor node)</li>
            <li>From work order, traverse to all <strong>process steps</strong> (successors via has_step edge)</li>
            <li>For each step, find the <strong>station</strong> where it was executed (successor via executed_at)</li>
            <li>For each step, find <strong>materials</strong> used (predecessors via used_in)</li>
            <li>For each material, find the <strong>supplier</strong> and batch (predecessor via supplies)</li>
        </ol>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin: 0;">
            Defect counts are then aggregated by (Supplier, Batch) and (Station, Product Series) combinations 
            to identify statistically significant patterns with correlation scores.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 5. KEY DISCOVERIES
# ==============================================================================
st.header("Key Discoveries")

st.markdown(f"""
<p style="color: {COLORS['text_secondary']}; margin-bottom: 1.5rem;">
    The GNN analysis has identified the following root cause patterns in the manufacturing data:
</p>
""", unsafe_allow_html=True)

disc_col1, disc_col2 = st.columns(2)

with disc_col1:
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-left: 4px solid {COLORS['critical']}; 
                border-radius: 0 12px 12px 0; padding: 1.5rem;">
        <h4 style="color: {COLORS['text']}; margin: 0 0 0.5rem 0;">Pattern 1: Supplier Batch Issue</h4>
        <p style="color: {COLORS['primary']}; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
            Vulcan Steel Works — Batch #2847
        </p>
        <div style="display: flex; gap: 1.5rem; margin-bottom: 1rem;">
            <div>
                <span style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Correlation</span>
                <p style="color: {COLORS['text']}; font-size: 1.5rem; font-weight: bold; margin: 0;">87%</p>
            </div>
            <div>
                <span style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Defect Types</span>
                <p style="color: {COLORS['text']}; font-size: 0.9rem; margin: 0;">Hydraulic seal failure, cylinder scoring</p>
            </div>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-bottom: 0.75rem;">
            <strong>Root Cause:</strong> Elevated sulfur content in steel batch causing seal failures.
        </p>
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid {COLORS['critical']}; 
                    border-radius: 8px; padding: 0.75rem; margin-top: 0.75rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">
                <strong style="color: {COLORS['text']};">Why traditional analysis missed it:</strong> 
                The sulfur content was within specification limits. Defects appeared across multiple product 
                families and stations. Only graph traversal revealed the common material batch.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

with disc_col2:
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-left: 4px solid {COLORS['warning']}; 
                border-radius: 0 12px 12px 0; padding: 1.5rem;">
        <h4 style="color: {COLORS['text']}; margin: 0 0 0.5rem 0;">Pattern 2: Process Configuration</h4>
        <p style="color: {COLORS['accent']}; font-size: 1.1rem; font-weight: 600; margin-bottom: 1rem;">
            Heat Treatment Line 3 + HD-Series Products
        </p>
        <div style="display: flex; gap: 1.5rem; margin-bottom: 1rem;">
            <div>
                <span style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Correlation</span>
                <p style="color: {COLORS['text']}; font-size: 1.5rem; font-weight: bold; margin: 0;">92%</p>
            </div>
            <div>
                <span style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Defect Types</span>
                <p style="color: {COLORS['text']}; font-size: 0.9rem; margin: 0;">Premature wear, stress fractures</p>
            </div>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-bottom: 0.75rem;">
            <strong>Root Cause:</strong> Temperature/duration parameters incorrect for HD-Series (820°C/45min vs required 870°C/60min).
        </p>
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid {COLORS['warning']}; 
                    border-radius: 8px; padding: 0.75rem; margin-top: 0.75rem;">
            <p style="color: {COLORS['text_secondary']}; font-size: 0.8rem; margin: 0;">
                <strong style="color: {COLORS['text']};">Why traditional analysis missed it:</strong> 
                Heat Treatment Line 3 performs well for Standard series products. The defect pattern only 
                appears for the HD-Series × Line 3 combination—a multi-hop pattern.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 6. BUSINESS IMPACT
# ==============================================================================
st.header("Business Impact")

st.markdown(f"""
<div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']}; margin-bottom: 1.5rem;">
    <table style="width: 100%; color: {COLORS['text']}; border-collapse: collapse;">
        <tr style="border-bottom: 2px solid {COLORS['border']};">
            <th style="text-align: left; padding: 1rem; color: {COLORS['text_secondary']};">Metric</th>
            <th style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">Before</th>
            <th style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">After</th>
            <th style="text-align: center; padding: 1rem; color: {COLORS['success']};">Improvement</th>
        </tr>
        <tr style="border-bottom: 1px solid {COLORS['border']};">
            <td style="padding: 1rem;"><strong>Root Cause Investigation</strong></td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">2-4 weeks</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">Minutes</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['success']}; font-weight: bold;">-80%</td>
        </tr>
        <tr style="border-bottom: 1px solid {COLORS['border']};">
            <td style="padding: 1rem;"><strong>Repeat Defects</strong></td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">Baseline</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">Predicted & prevented</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['success']}; font-weight: bold;">-40%</td>
        </tr>
        <tr style="border-bottom: 1px solid {COLORS['border']};">
            <td style="padding: 1rem;"><strong>Warranty Claim Costs</strong></td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">$1.2M/plant/year</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">Reduced via early detection</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['success']}; font-weight: bold;">-25%</td>
        </tr>
        <tr>
            <td style="padding: 1rem;"><strong>Quality Engineer Productivity</strong></td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">Manual correlation</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['text_secondary']};">Automated discovery</td>
            <td style="text-align: center; padding: 1rem; color: {COLORS['success']}; font-weight: bold;">+50%</td>
        </tr>
    </table>
    <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin-top: 1rem; margin-bottom: 0; text-align: center;">
        For a manufacturer with 5 plants, this represents <strong style="color: {COLORS['success']};">$1.5M+ in annual savings</strong> 
        from reduced warranty costs alone.
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 7. APPLICATION PAGES
# ==============================================================================
st.header("Application Pages")

pages_col1, pages_col2 = st.columns(2)

pages = [
    ("🔗 Process Network", "Discovery heatmaps showing defect concentration across suppliers, stations, and products. Interactive network graph visualization. Step-by-step algorithm trace explaining how each pattern was discovered.", pages_col1),
    ("🔍 Defect Tracing", "High-level defect overview with drill-down by defect type. Sankey flow diagram showing supplier → material → work order → defect paths. Correlation charts for suppliers, stations, and process parameters.", pages_col2),
    ("⚠️ Risk Analysis", "Risk scores ranked by supplier and station. AI-generated risk summaries via Cortex AI. Scatter plot correlation and risk level distribution. Prioritized recommended actions.", pages_col1),
    ("ℹ️ About", "This page. Solution overview, data architecture, technical documentation, business impact metrics, and getting started guide.", pages_col2),
]

for title, desc, col in pages:
    with col:
        st.markdown(f"""
        <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; margin-bottom: 0.75rem; border: 1px solid {COLORS['border']};">
            <strong style="color: {COLORS['primary']}; font-size: 1.1rem;">{title}</strong>
            <p style="color: {COLORS['text_secondary']}; margin: 0.5rem 0 0 0; font-size: 0.875rem; line-height: 1.6;">{desc}</p>
        </div>
        """, unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 8. TECHNOLOGY STACK
# ==============================================================================
st.header("Technology Stack")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.markdown("#### Snowflake Platform")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
            <span style="background: {COLORS['primary']}; color: {COLORS['background']}; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">NOTEBOOKS</span>
            <strong style="color: {COLORS['text']};">Snowflake Notebooks</strong>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin: 0;">
            Python execution with Snowpark session for graph construction and analysis. 
            Runs on SPCS compute pools with full access to warehouse data.
        </p>
    </div>
    
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
            <span style="background: {COLORS['accent']}; color: {COLORS['background']}; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">STREAMLIT</span>
            <strong style="color: {COLORS['text']};">Streamlit in Snowflake</strong>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin: 0;">
            Interactive dashboard running entirely within Snowflake's security perimeter. 
            No data leaves the platform.
        </p>
    </div>
    
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']};">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
            <span style="background: {COLORS['purple']}; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">CORTEX</span>
            <strong style="color: {COLORS['text']};">Cortex AI</strong>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin: 0;">
            Natural language risk summaries generated by Cortex Complete. 
            AI translates graph patterns into actionable insights.
        </p>
    </div>
    """, unsafe_allow_html=True)

with tech_col2:
    st.markdown("#### Analysis & Visualization")
    st.markdown(f"""
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
            <span style="background: {COLORS['secondary']}; color: white; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">SNOWPARK</span>
            <strong style="color: {COLORS['text']};">Snowpark Python</strong>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin: 0;">
            DataFrame API for data loading and transformation. 
            Direct integration with pandas for graph construction.
        </p>
    </div>
    
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']}; margin-bottom: 0.75rem;">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
            <span style="background: {COLORS['success']}; color: {COLORS['background']}; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">NETWORKX</span>
            <strong style="color: {COLORS['text']};">NetworkX</strong>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin: 0;">
            Graph construction and traversal for defect path analysis. 
            Heterogeneous directed graph with typed nodes and edges.
        </p>
    </div>
    
    <div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.25rem; border: 1px solid {COLORS['border']};">
        <div style="display: flex; align-items: center; gap: 1rem; margin-bottom: 0.75rem;">
            <span style="background: {COLORS['warning']}; color: {COLORS['background']}; padding: 0.25rem 0.75rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;">PLOTLY</span>
            <strong style="color: {COLORS['text']};">Plotly</strong>
        </div>
        <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem; margin: 0;">
            Interactive visualizations including network graphs, Sankey diagrams, 
            heatmaps, and risk distribution charts.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 9. GETTING STARTED
# ==============================================================================
st.header("Getting Started")

st.markdown(f"""
<div style="background: {COLORS['card']}; border-radius: 12px; padding: 1.5rem; border: 1px solid {COLORS['border']};">
    <ol style="color: {COLORS['text']}; padding-left: 1.5rem; margin: 0; line-height: 2;">
        <li style="margin-bottom: 0.75rem;">
            <strong>Deploy the infrastructure</strong><br>
            <code style="background: {COLORS['background']}; padding: 0.25rem 0.5rem; border-radius: 4px; color: {COLORS['primary']};">./deploy.sh</code>
            <span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;"> — Creates Snowflake resources and loads synthetic data</span>
        </li>
        <li style="margin-bottom: 0.75rem;">
            <strong>Execute the GNN notebook</strong><br>
            <code style="background: {COLORS['background']}; padding: 0.25rem 0.5rem; border-radius: 4px; color: {COLORS['primary']};">./run.sh main</code>
            <span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;"> — Builds the graph, traces defects, and generates risk scores</span>
        </li>
        <li style="margin-bottom: 0.75rem;">
            <strong>Explore the Process Network</strong><br>
            <span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">View discovery heatmaps and network visualization to understand material flow</span>
        </li>
        <li style="margin-bottom: 0.75rem;">
            <strong>Trace specific defects</strong><br>
            <span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">Use Defect Tracing to investigate individual quality issues with Sankey flows</span>
        </li>
        <li>
            <strong>Review Risk Analysis</strong><br>
            <span style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">Prioritize actions based on discovered patterns and AI-generated summaries</span>
        </li>
    </ol>
</div>
""", unsafe_allow_html=True)

st.divider()

# ==============================================================================
# 10. FOOTER
# ==============================================================================
st.markdown(f"""
<div style="text-align: center; color: {COLORS['text_secondary']}; font-size: 0.875rem; padding: 1rem 0;">
    <p style="margin-bottom: 0.5rem;">GNN Process Traceability Demo | Powered by Snowflake</p>
    <p style="margin: 0; font-size: 0.75rem;">
        Graph-based root cause analysis for manufacturing quality intelligence
    </p>
</div>
""", unsafe_allow_html=True)
