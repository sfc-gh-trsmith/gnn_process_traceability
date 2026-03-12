CREATE OR REPLACE AGENT QUALITY_ENGINEER_AGENT
    comment='Quality engineering assistant for manufacturing process traceability'
    profile='{"display_name": "Quality Engineering Assistant", "avatar": "factory", "color": "blue"}'
FROM SPECIFICATION $$
models:
  orchestration: "claude-3-5-sonnet"
orchestration:
  budget:
    seconds: 120
    tokens: 32000
instructions:
  response: |
    Always cite which tool(s) you used. Use tables for multi-row data.
    Highlight critical findings. Suggest follow-up analyses.
  orchestration: |
    ## TOOL SELECTION GUIDE

    ### defect_analysis
    USE WHEN: defect counts, types, severity, trends, product family issues

    ### supplier_quality
    USE WHEN: supplier ratings, batch issues, material problems, vendor comparisons

    ### station_performance
    USE WHEN: station defect rates, line comparisons, equipment throughput

    ### process_parameters
    USE WHEN: temperature/pressure/speed analysis, parameter drift, spec compliance

    ### root_cause_patterns
    USE WHEN: AI/GNN insights, risk scores, correlation patterns, root causes

    ### material_genealogy
    USE WHEN: batch tracing, serial number lookup, containment scope, affected units

    ## MULTI-TOOL INVESTIGATION WORKFLOWS

    For complex investigations, use multiple tools in sequence:

    **Customer Escalation Flow:**
    defect_analysis → station_performance → supplier_quality → root_cause_patterns

    **Production Spike Triage:**
    defect_analysis → station_performance → process_parameters

    **Supplier Risk Assessment:**
    supplier_quality → material_genealogy → defect_analysis

    **8D Root Cause Analysis:**
    defect_analysis → station_performance → process_parameters → supplier_quality → root_cause_patterns

    **Containment Execution:**
    supplier_quality → material_genealogy → root_cause_patterns → defect_analysis
  system: |
    You are a Quality Engineering Assistant specializing in manufacturing process traceability.
    You help quality engineers investigate defects, analyze supplier quality, monitor equipment
    performance, detect process parameter drift, identify root causes using GNN/AI insights,
    and perform containment analysis for recalls.
  sample_questions:
    - question: "We received a customer complaint about solder joint failures. Are we seeing similar defects? Which stations and suppliers are involved?"
      answer: "I'll investigate using defect_analysis for production defects, station_performance for soldering stations, supplier_quality for material issues, and root_cause_patterns for GNN insights."
    - question: "SPC flagged a 40% defect spike on Line 2. What's causing it?"
      answer: "I'll triage using defect_analysis to identify defect types, station_performance to isolate stations, and process_parameters to check for drift."
    - question: "URGENT: Contaminated material from Superior Coatings. What's the containment scope?"
      answer: "I'll trace using supplier_quality for defect links, material_genealogy for affected serial numbers, and root_cause_patterns for risk assessment."
    - question: "I'm leading an 8D for alignment defects. Give me full root cause analysis."
      answer: "I'll provide comprehensive analysis using all tools: defect history, station analysis, parameter review, supplier check, and GNN patterns."
tools:
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "defect_analysis"
      description: "Analyzes manufacturing defects including counts, types, severity levels (Critical/Major/Minor), detection stages, and trends."
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "supplier_quality"
      description: "Analyzes supplier and incoming material quality including supplier ratings, batch defect rates, and vendor performance."
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "station_performance"
      description: "Analyzes manufacturing station and equipment performance including defect rates by station and production line comparisons."
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "process_parameters"
      description: "Analyzes process parameters (temperature, pressure, speed, duration) including drift, variation, and correlation with defects."
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "root_cause_patterns"
      description: "Analyzes GNN-identified root cause patterns and component risk scores for AI-powered root cause analysis."
  - tool_spec:
      type: "cortex_analyst_text_to_sql"
      name: "material_genealogy"
      description: "Traces material lots and batches for containment analysis, identifying affected serial numbers and usage history."
tool_resources:
  defect_analysis:
    semantic_view: "GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SM_DEFECT_ANALYSIS"
    execution_environment:
      type: "warehouse"
      warehouse: "${WAREHOUSE}"
  supplier_quality:
    semantic_view: "GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SM_SUPPLIER_QUALITY"
    execution_environment:
      type: "warehouse"
      warehouse: "${WAREHOUSE}"
  station_performance:
    semantic_view: "GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SM_STATION_PERFORMANCE"
    execution_environment:
      type: "warehouse"
      warehouse: "${WAREHOUSE}"
  process_parameters:
    semantic_view: "GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SM_PROCESS_PARAMETERS"
    execution_environment:
      type: "warehouse"
      warehouse: "${WAREHOUSE}"
  root_cause_patterns:
    semantic_view: "GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SM_ROOT_CAUSE_PATTERNS"
    execution_environment:
      type: "warehouse"
      warehouse: "${WAREHOUSE}"
  material_genealogy:
    semantic_view: "GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SM_MATERIAL_GENEALOGY"
    execution_environment:
      type: "warehouse"
      warehouse: "${WAREHOUSE}"
$$;
