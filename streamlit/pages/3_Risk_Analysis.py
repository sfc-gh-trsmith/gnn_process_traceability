"""
Risk Analysis Page - Risk scores and discovered patterns with AI insights.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Risk Analysis", page_icon="⚠️", layout="wide")

from utils.database import get_session, get_root_cause_analysis, get_risk_scores
from utils.visualizations import COLORS, create_risk_bar_chart, apply_dark_theme
from utils.ai_insights import get_risk_summary

st.title("Risk Analysis")
st.markdown("Risk scores by supplier, station, and product family with AI-powered insights.")

try:
    session = get_session()
    
    # Load data
    root_causes_df = get_root_cause_analysis(session)
    risk_scores_df = get_risk_scores(session)
    
    # Discovered Patterns Section
    st.markdown("### Discovered Root Cause Patterns")
    
    if root_causes_df.empty:
        st.warning("No patterns discovered yet. Run the GNN analysis notebook first.")
    else:
        cols = st.columns(len(root_causes_df))
        
        for idx, (col, (_, pattern)) in enumerate(zip(cols, root_causes_df.iterrows())):
            with col:
                pattern_type = pattern.get('PATTERN_TYPE', 'Unknown')
                entity_name = pattern.get('ENTITY_NAME', 'Unknown')
                score = pattern.get('CORRELATION_SCORE', 0)
                defect_count = pattern.get('DEFECT_COUNT', 0)
                affected_wo = pattern.get('AFFECTED_WORK_ORDERS', 0)
                description = pattern.get('DESCRIPTION', '')
                
                border_color = COLORS['critical'] if score > 0.8 else COLORS['warning']
                
                st.markdown(f"""
                <div style="background: {COLORS['card']}; border-left: 4px solid {border_color}; 
                            border-radius: 0 12px 12px 0; padding: 1.5rem;">
                    <h4 style="color: {COLORS['text']}; margin-bottom: 0.5rem;">
                        {pattern_type.replace('_', ' ').upper()}
                    </h4>
                    <p style="color: {COLORS['primary']}; font-size: 1.1rem; font-weight: 600;">
                        {entity_name}
                    </p>
                    <div style="display: flex; gap: 1rem; margin: 1rem 0;">
                        <div>
                            <span style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Correlation</span>
                            <p style="color: {COLORS['text']}; font-size: 1.5rem; font-weight: bold; margin: 0;">{score:.0%}</p>
                        </div>
                        <div>
                            <span style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Defects</span>
                            <p style="color: {COLORS['text']}; font-size: 1.5rem; font-weight: bold; margin: 0;">{defect_count}</p>
                        </div>
                        <div>
                            <span style="color: {COLORS['text_secondary']}; font-size: 0.75rem;">Work Orders</span>
                            <p style="color: {COLORS['text']}; font-size: 1.5rem; font-weight: bold; margin: 0;">{affected_wo}</p>
                        </div>
                    </div>
                    <p style="color: {COLORS['text_secondary']}; font-size: 0.875rem;">{description[:200]}</p>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Risk Scores Section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Risk by Component")
        
        if risk_scores_df.empty:
            st.warning("No risk scores available. Run the GNN analysis notebook first.")
        else:
            # Tabs for different views
            tab1, tab2 = st.tabs(["Suppliers", "Stations"])
            
            with tab1:
                supplier_risks = risk_scores_df[risk_scores_df['COMPONENT_TYPE'] == 'supplier']
                if not supplier_risks.empty:
                    fig = create_risk_bar_chart(
                        supplier_risks, 
                        'COMPONENT_NAME', 
                        'RISK_SCORE',
                        'Supplier Risk Scores',
                        top_n=10
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No supplier risk data available.")
            
            with tab2:
                station_risks = risk_scores_df[risk_scores_df['COMPONENT_TYPE'] == 'station']
                if not station_risks.empty:
                    fig = create_risk_bar_chart(
                        station_risks, 
                        'COMPONENT_NAME', 
                        'RISK_SCORE',
                        'Station Risk Scores',
                        top_n=10
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No station risk data available.")
    
    with col2:
        st.markdown("### AI Risk Summary")
        
        if not risk_scores_df.empty:
            with st.spinner("Generating summary..."):
                summary = get_risk_summary(session, risk_scores_df)
            
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.08); border-left: 3px solid #3b82f6; 
                        padding: 1rem; border-radius: 0 8px 8px 0;">
                <div style="color: #60a5fa; font-size: 0.75rem; text-transform: uppercase; 
                            letter-spacing: 0.05em; margin-bottom: 0.5rem;">AI Summary</div>
                <p style="color: #e2e8f0; line-height: 1.6; margin: 0;">{summary}</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Run the GNN notebook to generate risk analysis.")
    
    st.markdown("---")
    
    # Correlation Visualizations Section
    st.markdown("### Risk Correlation Analysis")
    st.markdown("Visual analysis showing the relationship between risk scores and defect counts across components.")
    
    if not risk_scores_df.empty:
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            # Scatter plot: Risk Score vs Related Defects
            fig_scatter = go.Figure()
            
            # Add supplier points
            supplier_data = risk_scores_df[risk_scores_df['COMPONENT_TYPE'] == 'supplier']
            if not supplier_data.empty:
                # Convert to native Python types for SiS compatibility
                sup_x = [int(v) for v in supplier_data['RELATED_DEFECTS'].tolist()]
                sup_y = [float(v) for v in supplier_data['RISK_SCORE'].tolist()]
                sup_text = [str(v) for v in supplier_data['COMPONENT_NAME'].tolist()]
                
                fig_scatter.add_trace(go.Scatter(
                    x=sup_x,
                    y=sup_y,
                    mode='markers+text',
                    name='Suppliers',
                    marker=dict(size=12, color=COLORS['primary'], opacity=0.8),
                    text=sup_text,
                    textposition='top center',
                    textfont=dict(size=9, color=COLORS['text_secondary']),
                    hovertemplate='<b>%{text}</b><br>Defects: %{x}<br>Risk Score: %{y:.2f}<extra></extra>'
                ))
            
            # Add station points
            station_data = risk_scores_df[risk_scores_df['COMPONENT_TYPE'] == 'station']
            if not station_data.empty:
                # Convert to native Python types for SiS compatibility
                stn_x = [int(v) for v in station_data['RELATED_DEFECTS'].tolist()]
                stn_y = [float(v) for v in station_data['RISK_SCORE'].tolist()]
                stn_text = [str(v) for v in station_data['COMPONENT_NAME'].tolist()]
                
                fig_scatter.add_trace(go.Scatter(
                    x=stn_x,
                    y=stn_y,
                    mode='markers+text',
                    name='Stations',
                    marker=dict(size=12, color=COLORS['purple'], symbol='square', opacity=0.8),
                    text=stn_text,
                    textposition='top center',
                    textfont=dict(size=9, color=COLORS['text_secondary']),
                    hovertemplate='<b>%{text}</b><br>Defects: %{x}<br>Risk Score: %{y:.2f}<extra></extra>'
                ))
            
            # Add threshold lines
            fig_scatter.add_hline(y=0.7, line_dash="dash", line_color=COLORS['critical'], 
                                  annotation_text="Critical (0.7)", annotation_position="right")
            fig_scatter.add_hline(y=0.4, line_dash="dash", line_color=COLORS['warning'],
                                  annotation_text="Elevated (0.4)", annotation_position="right")
            
            fig_scatter.update_layout(
                title=dict(text='Risk Score vs Defect Count', font=dict(size=14)),
                xaxis=dict(title='Related Defects', gridcolor=COLORS['border']),
                yaxis=dict(title='Risk Score', range=[0, 1.1], gridcolor=COLORS['border']),
                height=350,
                margin=dict(l=40, r=40, t=60, b=40),
                legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
            )
            apply_dark_theme(fig_scatter)
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with viz_col2:
            # Risk Level Distribution
            risk_levels = []
            for _, row in risk_scores_df.iterrows():
                score = row['RISK_SCORE']
                if score > 0.7:
                    risk_levels.append('Critical (>0.7)')
                elif score > 0.4:
                    risk_levels.append('Elevated (0.4-0.7)')
                else:
                    risk_levels.append('Normal (<0.4)')
            
            risk_level_counts = pd.Series(risk_levels).value_counts()
            
            # Ensure consistent ordering
            level_order = ['Critical (>0.7)', 'Elevated (0.4-0.7)', 'Normal (<0.4)']
            level_colors = [COLORS['critical'], COLORS['warning'], COLORS['success']]
            
            ordered_values = [risk_level_counts.get(level, 0) for level in level_order]
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=level_order,
                values=ordered_values,
                hole=0.4,
                marker=dict(colors=level_colors),
                textinfo='label+value',
                textposition='outside',
                textfont=dict(color=COLORS['text']),
                hovertemplate='<b>%{label}</b><br>Components: %{value}<br>Percentage: %{percent}<extra></extra>'
            )])
            
            fig_pie.update_layout(
                title=dict(text='Risk Level Distribution', font=dict(size=14)),
                height=350,
                margin=dict(l=20, r=20, t=60, b=20),
                showlegend=False,
                annotations=[dict(
                    text=f'{len(risk_scores_df)}<br>Total',
                    x=0.5, y=0.5,
                    font=dict(size=16, color=COLORS['text']),
                    showarrow=False
                )]
            )
            apply_dark_theme(fig_pie)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        # Quick stats row
        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        critical_count = len(risk_scores_df[risk_scores_df['RISK_SCORE'] > 0.7])
        elevated_count = len(risk_scores_df[(risk_scores_df['RISK_SCORE'] > 0.4) & (risk_scores_df['RISK_SCORE'] <= 0.7)])
        total_defects = risk_scores_df['RELATED_DEFECTS'].sum()
        avg_risk = risk_scores_df['RISK_SCORE'].mean()
        
        stat_col1.metric("Critical Risk Components", critical_count, delta=None)
        stat_col2.metric("Elevated Risk Components", elevated_count, delta=None)
        stat_col3.metric("Total Related Defects", int(total_defects), delta=None)
        stat_col4.metric("Average Risk Score", f"{avg_risk:.2f}", delta=None)
    else:
        st.info("Run the GNN notebook to generate risk correlation data.")
    
    st.markdown("---")
    
    # Recommendations
    st.markdown("### Recommended Actions")
    
    if not root_causes_df.empty:
        import json
        recommendations = []
        for _, pattern in root_causes_df.iterrows():
            try:
                recs_raw = pattern.get('RECOMMENDATIONS', '[]')
                
                # Handle case where it's already a list vs a JSON string
                if isinstance(recs_raw, list):
                    recs = recs_raw
                elif isinstance(recs_raw, str):
                    # Try to parse as JSON
                    try:
                        recs = json.loads(recs_raw)
                    except json.JSONDecodeError:
                        recs = []
                else:
                    recs = []
                
                # Validate recs is actually a list
                if not isinstance(recs, list):
                    recs = []
                
                for rec in recs:
                    # Only process valid string recommendations (ignore single chars)
                    if isinstance(rec, str) and len(rec) > 1:
                        priority = 'CRITICAL' if pattern['CORRELATION_SCORE'] > 0.8 else 'HIGH'
                        recommendations.append({
                            'priority': priority,
                            'action': rec,
                            'pattern': pattern['ENTITY_NAME']
                        })
            except Exception:
                pass
        
        if recommendations:
            for rec in recommendations[:5]:
                priority_color = COLORS['critical'] if rec['priority'] == 'CRITICAL' else COLORS['warning']
                st.markdown(f"""
                <div style="background: {COLORS['card']}; border-radius: 8px; padding: 1rem; 
                            margin-bottom: 0.5rem; border: 1px solid {COLORS['border']}; display: flex; gap: 1rem; align-items: center;">
                    <span style="background: {priority_color}; color: white; padding: 0.25rem 0.5rem; 
                                border-radius: 4px; font-size: 0.75rem; font-weight: bold;">{rec['priority']}</span>
                    <span style="color: {COLORS['text']};">{rec['action']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No specific recommendations available.")
    else:
        st.info("Run the GNN notebook to generate recommendations.")

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Make sure you have deployed the application and run the GNN notebook.")

