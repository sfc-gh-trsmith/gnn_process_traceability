"""Defect Tracing Page - aggregated view by defect type with drill-down correlations."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Defect Tracing", page_icon="🔍", layout="wide")

from utils.database import (
    get_session,
    get_defect_type_counts,
    get_defect_type_supplier_batch,
    get_defect_type_station,
    get_defect_type_step,
    get_defect_type_param_stats,
    get_defect_type_paths,
)
from utils.visualizations import COLORS, apply_dark_theme, create_sankey_diagram


def build_defect_type_bar(counts_df: pd.DataFrame) -> go.Figure:
    # Convert to native Python types for SiS compatibility
    x_values = [int(v) for v in counts_df['DEFECT_COUNT'].tolist()]
    y_values = [str(t) for t in counts_df['DEFECT_TYPE'].tolist()]
    
    fig = go.Figure(
        go.Bar(
            x=x_values,
            y=y_values,
            orientation='h',
            marker=dict(color=COLORS['primary'])
        )
    )
    fig.update_layout(
        title='Defects by Type',
        xaxis=dict(title='Count'),
        yaxis=dict(title=''),
        margin=dict(l=140, r=40, t=60, b=40)
    )
    return apply_dark_theme(fig)


def build_corr_bar(df: pd.DataFrame, x_col: str, y_col: str, title: str, color=COLORS['accent']):
    # Convert to native Python types for SiS compatibility
    x_values = [int(v) if isinstance(v, (int, float)) else float(v) for v in df[x_col].tolist()]
    y_values = [str(v) for v in df[y_col].tolist()]
    
    fig = go.Figure(go.Bar(
        x=x_values,
        y=y_values,
        orientation='h',
        marker=dict(color=color)
    ))
    fig.update_layout(
        title=title,
        xaxis=dict(title='Defect Count'),
        yaxis=dict(title=''),
        margin=dict(l=160, r=40, t=60, b=40)
    )
    return apply_dark_theme(fig)


def build_param_bar(df: pd.DataFrame) -> go.Figure:
    # Convert to native Python types for SiS compatibility
    x_values = [float(v) for v in df['DELTA_MEAN'].tolist()]
    y_values = [str(v) for v in df['PARAM_NAME'].tolist()]
    error_values = [float(v) for v in df['DEFECT_STD'].fillna(0).tolist()]
    
    fig = go.Figure(go.Bar(
        x=x_values,
        y=y_values,
        orientation='h',
        marker=dict(color=COLORS['accent']),
        error_x=dict(array=error_values)
    ))
    fig.update_layout(
        title='Process Parameter Shift (vs baseline)',
        xaxis=dict(title='Delta Mean'),
        yaxis=dict(title='Parameter'),
        margin=dict(l=200, r=40, t=60, b=40)
    )
    return apply_dark_theme(fig)


def build_sankey_from_edges(edges_df: pd.DataFrame, defect_type: str):
    subset = edges_df[edges_df['DEFECT_TYPE'] == defect_type]
    if subset.empty:
        return None

    nodes = []
    node_labels = []
    node_colors = []
    node_index = {}

    def _add_node(node_type, node_id, label):
        key = f"{node_type}:{node_id}"
        if key not in node_index:
            node_index[key] = len(nodes)
            nodes.append(key)
            node_labels.append(label or node_id)
            node_colors.append({
                'supplier': COLORS['primary'],
                'material': COLORS['secondary'],
                'work_order': COLORS['success'],
                'defect_type': COLORS['critical']
            }.get(node_type, COLORS['text_secondary']))

    for _, row in subset.iterrows():
        _add_node(row['SOURCE_TYPE'], row['SOURCE_ID'], row['SOURCE_LABEL'])
        _add_node(row['TARGET_TYPE'], row['TARGET_ID'], row['TARGET_LABEL'])

    sources = []
    targets = []
    values = []
    for _, row in subset.iterrows():
        sources.append(node_index[f"{row['SOURCE_TYPE']}:{row['SOURCE_ID']}"])
        targets.append(node_index[f"{row['TARGET_TYPE']}:{row['TARGET_ID']}"])
        values.append(row['VALUE'])

    sankey_data = {
        'labels': node_labels,
        'colors': node_colors,
        'source': sources,
        'target': targets,
        'value': values
    }
    fig = create_sankey_diagram(sankey_data, title=f"Supplier → Material → Work Order → {defect_type}")
    fig.update_layout(height=450)
    return fig


st.title("Defect Tracing")
st.markdown("High-level defect overview with drill-down by defect type.")

try:
    session = get_session()
    with st.spinner("Loading aggregated defect data..."):
        counts_df = get_defect_type_counts(session)
        supplier_df = get_defect_type_supplier_batch(session)
        station_df = get_defect_type_station(session)
        step_df = get_defect_type_step(session)
        param_df = get_defect_type_param_stats(session)
        path_df = get_defect_type_paths(session)

        # Defensive re-aggregation to avoid duplicates and keep counts aligned with metrics
        if not counts_df.empty:
            counts_df = counts_df.groupby('DEFECT_TYPE', as_index=False).agg(
                DEFECT_COUNT=('DEFECT_COUNT', 'sum'),
                AFFECTED_WORK_ORDERS=('AFFECTED_WORK_ORDERS', 'sum')
            ).sort_values('DEFECT_COUNT', ascending=False)

    if counts_df.empty:
        st.warning("No defect aggregates found. Run the GNN analysis notebook to populate tables.")
    else:
        selected_type = st.selectbox(
            "Defect Type",
            options=counts_df['DEFECT_TYPE'].tolist(),
            index=0,
            key="defect_type_select"
        )

        st.plotly_chart(build_defect_type_bar(counts_df), use_container_width=True)

        sel_row = counts_df[counts_df['DEFECT_TYPE'] == selected_type].iloc[0]
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Defects", int(sel_row['DEFECT_COUNT']))
        with m2:
            st.metric("Affected Work Orders", int(sel_row['AFFECTED_WORK_ORDERS']))

        st.markdown("---")

        st.markdown("### Origin Flow")
        sankey_fig = build_sankey_from_edges(path_df, selected_type)
        if sankey_fig:
            st.plotly_chart(sankey_fig, use_container_width=True)
        else:
            st.info("No path data available for this defect type.")

        st.markdown("---")
        st.markdown("### Correlations by Defect Type")
        c1, c2 = st.columns(2)

        sup_slice = supplier_df[supplier_df['DEFECT_TYPE'] == selected_type].copy()
        sup_slice = sup_slice.sort_values('DEFECT_COUNT', ascending=False).head(10)
        if sup_slice.empty:
            c1.info("No supplier/batch correlation data.")
        else:
            sup_slice['SUPPLIER_LABEL'] = sup_slice['SUPPLIER_NAME'].fillna(sup_slice['SUPPLIER_ID'])
            c1.plotly_chart(
                build_corr_bar(sup_slice, 'DEFECT_COUNT', 'SUPPLIER_LABEL', 'Top Suppliers/Batches'),
                use_container_width=True
            )

        stn_slice = station_df[station_df['DEFECT_TYPE'] == selected_type].copy()
        stn_slice = stn_slice.sort_values('DEFECT_COUNT', ascending=False).head(10)
        if stn_slice.empty:
            c2.info("No station/line correlation data.")
        else:
            stn_slice['STATION_LABEL'] = stn_slice['STATION_NAME'].fillna(stn_slice['STATION_ID'])
            stn_slice['STATION_LABEL'] = stn_slice['STATION_LABEL'] + stn_slice['LINE'].fillna('').apply(lambda x: f" ({x})" if x else '')
            c2.plotly_chart(
                build_corr_bar(stn_slice, 'DEFECT_COUNT', 'STATION_LABEL', 'Top Stations/Lines', color=COLORS['purple']),
                use_container_width=True
            )

        c3, c4 = st.columns(2)
        step_slice = step_df[step_df['DEFECT_TYPE'] == selected_type].copy()
        step_slice = step_slice.sort_values('DEFECT_COUNT', ascending=False).head(10)
        if step_slice.empty:
            c3.info("No step concentration data.")
        else:
            step_slice['STEP_LABEL'] = step_slice['STEP_TYPE'].fillna(step_slice['STEP_ID'])
            c3.plotly_chart(
                build_corr_bar(step_slice, 'DEFECT_COUNT', 'STEP_LABEL', 'Process Steps', color=COLORS['secondary']),
                use_container_width=True
            )

        param_slice = param_df[param_df['DEFECT_TYPE'] == selected_type].copy()
        if not param_slice.empty:
            param_slice = param_slice.dropna(subset=['DELTA_MEAN'])
            param_slice = param_slice.sort_values('DELTA_MEAN', ascending=False).head(10)

        if param_slice.empty:
            if param_df.empty:
                c4.info("No process parameter shift data available.")
            else:
                fallback = param_df.dropna(subset=['DELTA_MEAN']).sort_values('DELTA_MEAN', ascending=False).head(10)
                if fallback.empty:
                    c4.info("No process parameter shift data available.")
                else:
                    c4.info("No parameter shift data for this defect type; showing top overall.")
                    c4.plotly_chart(build_param_bar(fallback), use_container_width=True)
        else:
            c4.plotly_chart(build_param_bar(param_slice), use_container_width=True)

except Exception as e:
    st.error(f"Error: {e}")
    st.info("Run the GNN notebook to refresh aggregated tables before using this page.")
