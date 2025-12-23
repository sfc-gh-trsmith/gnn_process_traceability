"""
Database operations with caching for Streamlit performance.
"""

import streamlit as st
from snowflake.snowpark.context import get_active_session


def get_session():
    """Get the Snowflake session from SPCS context."""
    return get_active_session()


@st.cache_data(ttl=300)
def get_defects_summary(_session):
    """Get cached summary of defects."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            SEVERITY,
            COUNT(*) as DEFECT_COUNT,
            COUNT(DISTINCT WORK_ORDER_ID) as AFFECTED_WORK_ORDERS
        FROM DEFECTS
        GROUP BY DEFECT_TYPE, SEVERITY
        ORDER BY DEFECT_COUNT DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_root_cause_analysis(_session):
    """Get cached root cause analysis results."""
    return _session.sql("""
        SELECT * FROM ROOT_CAUSE_ANALYSIS
        ORDER BY CORRELATION_SCORE DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_risk_scores(_session):
    """Get cached component risk scores."""
    return _session.sql("""
        SELECT 
            COMPONENT_ID,
            COMPONENT_TYPE,
            COMPONENT_NAME,
            RISK_SCORE,
            RISK_FACTORS,
            RELATED_DEFECTS
        FROM COMPONENT_RISK_SCORES
        ORDER BY RISK_SCORE DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_defect_type_counts(_session):
    """Aggregated counts by defect type."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            DEFECT_COUNT,
            AFFECTED_WORK_ORDERS
        FROM DEFECT_TYPE_COUNTS
        ORDER BY DEFECT_COUNT DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_defect_type_supplier_batch(_session):
    """Supplier/batch lift by defect type."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            SUPPLIER_ID,
            SUPPLIER_NAME,
            BATCH_NUMBER,
            MATERIAL_TYPE,
            DEFECT_COUNT,
            USAGE_COUNT,
            DEFECT_RATE,
            LIFT
        FROM DEFECT_TYPE_SUPPLIER_BATCH
        ORDER BY DEFECT_COUNT DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_defect_type_station(_session):
    """Station + line hot spots by defect type."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            STATION_ID,
            STATION_NAME,
            LINE,
            PRODUCT_SERIES,
            PRODUCT_FAMILY,
            DEFECT_COUNT
        FROM DEFECT_TYPE_STATION
        ORDER BY DEFECT_COUNT DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_defect_type_step(_session):
    """Step concentration by defect type."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            STEP_ID,
            STEP_TYPE,
            STATION_ID,
            DEFECT_COUNT
        FROM DEFECT_TYPE_STEP
        ORDER BY DEFECT_COUNT DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_defect_type_param_stats(_session):
    """Process parameter shifts by defect type."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            PARAM_NAME,
            DEFECT_MEAN,
            DEFECT_STD,
            DEFECT_COUNT,
            BASELINE_MEAN,
            BASELINE_STD,
            BASELINE_COUNT,
            DELTA_MEAN
        FROM DEFECT_TYPE_PARAM_STATS
        ORDER BY DEFECT_TYPE, PARAM_NAME
    """).to_pandas()


@st.cache_data(ttl=300)
def get_defect_type_paths(_session):
    """Aggregated path edges for defect-type Sankey."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            SOURCE_TYPE,
            SOURCE_ID,
            SOURCE_LABEL,
            TARGET_TYPE,
            TARGET_ID,
            TARGET_LABEL,
            VALUE
        FROM DEFECT_TYPE_PATH_EDGES
        ORDER BY DEFECT_TYPE, VALUE DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_defects_list(_session):
    """Get list of defects for selection."""
    return _session.sql("""
        SELECT 
            d.DEFECT_ID,
            d.DEFECT_TYPE,
            d.SEVERITY,
            d.WORK_ORDER_ID,
            d.ROOT_CAUSE,
            wo.PRODUCT_FAMILY,
            wo.PRODUCT_SERIES
        FROM DEFECTS d
        JOIN WORK_ORDERS wo ON d.WORK_ORDER_ID = wo.WORK_ORDER_ID
        ORDER BY d.DETECTION_DATE DESC
    """).to_pandas()


@st.cache_data(ttl=300)
def get_suppliers(_session):
    """Get suppliers data."""
    return _session.sql("SELECT * FROM SUPPLIERS ORDER BY NAME").to_pandas()


@st.cache_data(ttl=300)
def get_stations(_session):
    """Get stations data."""
    return _session.sql("SELECT * FROM STATIONS ORDER BY NAME").to_pandas()


@st.cache_data(ttl=300)
def get_materials(_session):
    """Get materials data."""
    return _session.sql("SELECT * FROM MATERIALS").to_pandas()


@st.cache_data(ttl=300)
def get_work_orders(_session):
    """Get work orders data."""
    return _session.sql("SELECT * FROM WORK_ORDERS").to_pandas()


@st.cache_data(ttl=300)
def get_process_steps(_session):
    """Get process steps data."""
    return _session.sql("SELECT * FROM PROCESS_STEPS").to_pandas()


@st.cache_data(ttl=300)
def get_defects(_session):
    """Get defects data."""
    return _session.sql("SELECT * FROM DEFECTS").to_pandas()


def get_defect_trace(_session, defect_id):
    """Get trace data for a specific defect."""
    return _session.sql(f"""
        WITH defect_wo AS (
            SELECT WORK_ORDER_ID FROM DEFECTS WHERE DEFECT_ID = '{defect_id}'
        ),
        wo_steps AS (
            SELECT ps.* FROM PROCESS_STEPS ps
            JOIN defect_wo dw ON ps.WORK_ORDER_ID = dw.WORK_ORDER_ID
        ),
        step_materials AS (
            SELECT DISTINCT m.*, s.NAME as SUPPLIER_NAME
            FROM MATERIALS m
            JOIN SUPPLIERS s ON m.SUPPLIER_ID = s.SUPPLIER_ID
            WHERE m.MATERIAL_ID IN (SELECT MATERIAL_ID FROM wo_steps WHERE MATERIAL_ID IS NOT NULL)
        )
        SELECT 
            d.DEFECT_ID,
            d.DEFECT_TYPE,
            d.SEVERITY,
            wo.WORK_ORDER_ID,
            wo.PRODUCT_FAMILY,
            wo.PRODUCT_SERIES,
            sm.MATERIAL_ID,
            sm.MATERIAL_TYPE,
            sm.BATCH_NUMBER,
            sm.SUPPLIER_ID,
            sm.SUPPLIER_NAME
        FROM DEFECTS d
        JOIN WORK_ORDERS wo ON d.WORK_ORDER_ID = wo.WORK_ORDER_ID
        LEFT JOIN step_materials sm ON 1=1
        WHERE d.DEFECT_ID = '{defect_id}'
    """).to_pandas()

