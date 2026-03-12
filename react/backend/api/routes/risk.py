from fastapi import APIRouter
from api.database import execute_query

router = APIRouter()

@router.get("/scores")
def get_risk_scores():
    query = """
    SELECT component_type as entity_type, component_id as entity_id, 
           risk_score, related_defects as defect_count, 
           risk_score as severity_weighted_score
    FROM COMPONENT_RISK_SCORES
    ORDER BY risk_score DESC
    """
    return execute_query(query)

@router.get("/root-causes")
def get_root_cause_analysis():
    query = """
    SELECT defect_type, entity_type as root_cause_type, entity_id as entity_1, 
           entity_name as entity_2, correlation_score as correlation_strength, 
           defect_count, affected_work_orders as total_defects_of_type, 
           CASE WHEN correlation_score >= 0.85 THEN TRUE ELSE FALSE END as is_primary_root_cause
    FROM ROOT_CAUSE_ANALYSIS
    ORDER BY correlation_score DESC
    """
    return execute_query(query)

@router.get("/supplier-batch")
def get_supplier_batch_correlations():
    query = """
    WITH ranked AS (
        SELECT supplier_name, batch_number as batch_id, 
               SUM(defect_count) as defect_count
        FROM DEFECT_TYPE_SUPPLIER_BATCH
        GROUP BY supplier_name, batch_number
        ORDER BY defect_count DESC
        LIMIT 15
    ),
    with_cumulative AS (
        SELECT supplier_name, batch_id, defect_count,
               SUM(defect_count) OVER (ORDER BY defect_count DESC) as cumulative_defects,
               SUM(defect_count) OVER () as total_defects
        FROM ranked
    )
    SELECT supplier_name, batch_id, defect_count,
           cumulative_defects,
           ROUND(cumulative_defects * 100.0 / total_defects, 1) as cumulative_pct
    FROM with_cumulative
    ORDER BY defect_count DESC
    """
    return execute_query(query)

@router.get("/station")
def get_station_correlations():
    query = """
    SELECT defect_type, station_name, line as line_id, 
           defect_count, defect_count as expected_defects, 
           defect_count as lift_ratio
    FROM DEFECT_TYPE_STATION
    ORDER BY defect_count DESC
    LIMIT 50
    """
    return execute_query(query)

@router.get("/process-steps")
def get_process_step_correlations():
    query = """
    WITH step_totals AS (
        SELECT step_type, COUNT(*) as total_occurrences
        FROM PROCESS_STEPS
        GROUP BY step_type
    )
    SELECT 
        ds.defect_type, 
        ds.step_type as step_name, 
        ds.defect_count,
        st.total_occurrences,
        ROUND(ds.defect_count * 100.0 / st.total_occurrences, 2) as defect_rate
    FROM DEFECT_TYPE_STEP ds
    JOIN step_totals st ON ds.step_type = st.step_type
    ORDER BY defect_rate DESC
    LIMIT 500
    """
    return execute_query(query)

@router.get("/supplier-defect-bubble")
def get_supplier_defect_bubble():
    query = """
    SELECT defect_type, supplier_name, material_type, SUM(defect_count) as defect_count
    FROM DEFECT_TYPE_SUPPLIER_BATCH
    GROUP BY defect_type, supplier_name, material_type
    ORDER BY defect_count DESC
    """
    return execute_query(query)

@router.get("/five-whys/{defect_type}")
def get_five_whys_analysis(defect_type: str):
    import json
    import re
    
    context_query = """
    SELECT description, recommendations, correlation_score, entity_name
    FROM ROOT_CAUSE_ANALYSIS
    WHERE defect_type = %s
    """
    context_data = execute_query(context_query, (defect_type,))
    
    correlation_query = """
    SELECT supplier_name, material_type, SUM(defect_count) as defects
    FROM DEFECT_TYPE_SUPPLIER_BATCH
    WHERE defect_type = %s
    GROUP BY supplier_name, material_type
    ORDER BY defects DESC
    LIMIT 5
    """
    supplier_data = execute_query(correlation_query, (defect_type,))
    
    station_query = """
    SELECT station_name, line, SUM(defect_count) as defects
    FROM DEFECT_TYPE_STATION
    WHERE defect_type = %s
    GROUP BY station_name, line
    ORDER BY defects DESC
    LIMIT 5
    """
    station_data = execute_query(station_query, (defect_type,))
    
    context_str = json.dumps(context_data) if context_data else "No prior root cause analysis available"
    supplier_str = json.dumps(supplier_data) if supplier_data else "No supplier data"
    station_str = json.dumps(station_data) if station_data else "No station data"
    
    prompt = f"""You are a manufacturing quality engineer. Analyze the defect type "{defect_type.replace('_', ' ')}" using the 5-Whys method and Ishikawa (fishbone) diagram categories.

Context from prior analysis: {context_str}
Top correlated suppliers: {supplier_str}
Top correlated stations: {station_str}

Generate a root cause analysis with EXACTLY this JSON structure (no markdown, just raw JSON):
{{
  "defect_type": "{defect_type}",
  "problem_statement": "Brief description of the defect problem",
  "categories": [
    {{
      "category": "Material",
      "causes": [{{
        "why1": "First level cause related to materials",
        "why2": "Why does why1 happen?",
        "why3": "Why does why2 happen?",
        "why4": "Why does why3 happen?",
        "why5": "Why does why4 happen?",
        "root_cause": "The fundamental root cause"
      }}]
    }},
    {{
      "category": "Method",
      "causes": [{{
        "why1": "First level cause related to processes/methods",
        "why2": "Why does why1 happen?",
        "why3": "Why does why2 happen?",
        "why4": "Why does why3 happen?",
        "why5": "Why does why4 happen?",
        "root_cause": "The fundamental root cause"
      }}]
    }},
    {{
      "category": "Machine",
      "causes": [{{
        "why1": "First level cause related to equipment",
        "why2": "Why does why1 happen?",
        "why3": "Why does why2 happen?",
        "why4": "Why does why3 happen?",
        "why5": "Why does why4 happen?",
        "root_cause": "The fundamental root cause"
      }}]
    }},
    {{
      "category": "Man",
      "causes": [{{
        "why1": "First level cause related to personnel/training",
        "why2": "Why does why1 happen?",
        "why3": "Why does why2 happen?",
        "why4": "Why does why3 happen?",
        "why5": "Why does why4 happen?",
        "root_cause": "The fundamental root cause"
      }}]
    }},
    {{
      "category": "Measurement",
      "causes": [{{
        "why1": "First level cause related to inspection/measurement",
        "why2": "Why does why1 happen?",
        "why3": "Why does why2 happen?",
        "why4": "Why does why3 happen?",
        "why5": "Why does why4 happen?",
        "root_cause": "The fundamental root cause"
      }}]
    }},
    {{
      "category": "Environment",
      "causes": [{{
        "why1": "First level cause related to environment",
        "why2": "Why does why1 happen?",
        "why3": "Why does why2 happen?",
        "why4": "Why does why3 happen?",
        "why5": "Why does why4 happen?",
        "root_cause": "The fundamental root cause"
      }}]
    }}
  ],
  "ai_confidence": 0.85
}}

Use the context data to make the analysis specific and actionable. Return ONLY the JSON object, no explanation."""
    
    escaped_prompt = prompt.replace("'", "''")
    
    llm_query = f"""
    SELECT SNOWFLAKE.CORTEX.COMPLETE('llama3.1-70b', '{escaped_prompt}') as analysis
    """
    
    result = execute_query(llm_query)
    
    if result and result[0].get('analysis'):
        raw_response = result[0]['analysis']
        json_match = re.search(r'\{[\s\S]*\}', raw_response)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
    
    return {
        "defect_type": defect_type,
        "problem_statement": f"Analysis of {defect_type.replace('_', ' ')} defects",
        "categories": [
            {"category": "Material", "causes": [{"why1": "Material quality issues", "why2": "Supplier batch variability", "why3": "Inconsistent raw materials", "why4": "Supply chain issues", "why5": "Procurement standards", "root_cause": "Supplier quality control gaps"}]},
            {"category": "Method", "causes": [{"why1": "Process deviation", "why2": "SOP not followed", "why3": "Training gaps", "why4": "Documentation outdated", "why5": "Change management", "root_cause": "Process standardization needed"}]},
            {"category": "Machine", "causes": [{"why1": "Equipment wear", "why2": "Maintenance delay", "why3": "Resource constraints", "why4": "Budget limitations", "why5": "Priority conflicts", "root_cause": "Preventive maintenance program"}]},
            {"category": "Man", "causes": [{"why1": "Operator error", "why2": "Skill gap", "why3": "Training incomplete", "why4": "High turnover", "why5": "Working conditions", "root_cause": "Training program enhancement"}]},
            {"category": "Measurement", "causes": [{"why1": "Detection delay", "why2": "Inspection frequency", "why3": "Tool calibration", "why4": "Standards unclear", "why5": "Specification review", "root_cause": "Quality control standards"}]},
            {"category": "Environment", "causes": [{"why1": "Contamination", "why2": "Cleanliness standards", "why3": "Facility age", "why4": "Investment needed", "why5": "Capital planning", "root_cause": "Facility upgrades"}]}
        ],
        "ai_confidence": 0.5
    }

@router.get("/supplier-defect-heatmap")
def get_supplier_defect_heatmap():
    query = """
    WITH supplier_totals AS (
        SELECT supplier_name, SUM(defect_count) as total
        FROM DEFECT_TYPE_SUPPLIER_BATCH
        GROUP BY supplier_name
        ORDER BY total DESC
        LIMIT 10
    )
    SELECT d.defect_type, d.supplier_name, SUM(d.defect_count) as defect_count
    FROM DEFECT_TYPE_SUPPLIER_BATCH d
    JOIN supplier_totals s ON d.supplier_name = s.supplier_name
    GROUP BY d.defect_type, d.supplier_name
    ORDER BY d.supplier_name, d.defect_type
    """
    return execute_query(query)

@router.get("/param-stats")
def get_param_stats():
    query = """
    WITH defective_wo AS (
        SELECT DISTINCT work_order_id, defect_type
        FROM DEFECTS
    ),
    all_params AS (
        SELECT 
            ps.work_order_id,
            pp.temperature, pp.pressure, pp.speed
        FROM PROCESS_STEPS ps
        JOIN PROCESS_PARAMETERS pp ON ps.step_id = pp.step_id
    ),
    baseline_stats AS (
        SELECT 
            AVG(temperature) as baseline_temp,
            AVG(pressure) as baseline_pressure,
            AVG(speed) as baseline_speed
        FROM all_params ap
        WHERE NOT EXISTS (SELECT 1 FROM defective_wo d WHERE d.work_order_id = ap.work_order_id)
    ),
    defect_stats AS (
        SELECT 
            d.defect_type,
            AVG(ap.temperature) as defect_temp,
            AVG(ap.pressure) as defect_pressure,
            AVG(ap.speed) as defect_speed
        FROM all_params ap
        JOIN defective_wo d ON ap.work_order_id = d.work_order_id
        GROUP BY d.defect_type
    )
    SELECT 
        ds.defect_type,
        'temperature' as param_name,
        ROUND(ds.defect_temp, 2) as mean_defect,
        ROUND(bs.baseline_temp, 2) as mean_no_defect,
        ROUND(((ds.defect_temp - bs.baseline_temp) / NULLIF(bs.baseline_temp, 0)) * 100, 1) as shift_pct
    FROM defect_stats ds
    CROSS JOIN baseline_stats bs
    WHERE ds.defect_temp IS NOT NULL AND bs.baseline_temp IS NOT NULL

    UNION ALL

    SELECT 
        ds.defect_type,
        'pressure' as param_name,
        ROUND(ds.defect_pressure, 2) as mean_defect,
        ROUND(bs.baseline_pressure, 2) as mean_no_defect,
        ROUND(((ds.defect_pressure - bs.baseline_pressure) / NULLIF(bs.baseline_pressure, 0)) * 100, 1) as shift_pct
    FROM defect_stats ds
    CROSS JOIN baseline_stats bs
    WHERE ds.defect_pressure IS NOT NULL AND bs.baseline_pressure IS NOT NULL

    UNION ALL

    SELECT 
        ds.defect_type,
        'speed' as param_name,
        ROUND(ds.defect_speed, 2) as mean_defect,
        ROUND(bs.baseline_speed, 2) as mean_no_defect,
        ROUND(((ds.defect_speed - bs.baseline_speed) / NULLIF(bs.baseline_speed, 0)) * 100, 1) as shift_pct
    FROM defect_stats ds
    CROSS JOIN baseline_stats bs
    WHERE ds.defect_speed IS NOT NULL AND bs.baseline_speed IS NOT NULL

    ORDER BY ABS(shift_pct) DESC
    LIMIT 30
    """
    return execute_query(query)
