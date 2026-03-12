CREATE OR REPLACE SEMANTIC VIEW SM_ROOT_CAUSE_PATTERNS
    tables (
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.ROOT_CAUSE_ANALYSIS unique (ANALYSIS_ID) comment='GNN-identified root cause patterns from defect analysis',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.COMPONENT_RISK_SCORES unique (COMPONENT_ID) comment='Risk scores for manufacturing components based on GNN analysis'
    )
    facts (
        ROOT_CAUSE_ANALYSIS.CORRELATION_SCORE as CORRELATION_SCORE with synonyms=('confidence score','pattern strength') comment='GNN correlation score (0-1) indicating pattern strength',
        ROOT_CAUSE_ANALYSIS.DEFECT_COUNT as DEFECT_COUNT with synonyms=('associated defects','defects linked') comment='Number of defects associated with this pattern',
        ROOT_CAUSE_ANALYSIS.AFFECTED_WORK_ORDERS as AFFECTED_WORK_ORDERS with synonyms=('impacted work orders','WOs affected') comment='Number of work orders affected by this pattern',
        COMPONENT_RISK_SCORES.RISK_SCORE as RISK_SCORE with synonyms=('risk level','risk rating') comment='Calculated risk score (0-100)',
        COMPONENT_RISK_SCORES.RELATED_DEFECTS as RELATED_DEFECTS with synonyms=('defects linked','associated defects') comment='Number of defects related to this component'
    )
    dimensions (
        ROOT_CAUSE_ANALYSIS.ANALYSIS_ID as ANALYSIS_ID with synonyms=('analysis code','pattern id') comment='Unique identifier for the analysis record',
        ROOT_CAUSE_ANALYSIS.PATTERN_TYPE as PATTERN_TYPE with synonyms=('root cause pattern','failure pattern') comment='Type of pattern identified (e.g., correlation, clustering)',
        ROOT_CAUSE_ANALYSIS.ENTITY_TYPE as ENTITY_TYPE with synonyms=('component type','factor type') comment='Type of entity identified as root cause (supplier, station, material)',
        ROOT_CAUSE_ANALYSIS.ENTITY_ID as ENTITY_ID with synonyms=('component id') comment='ID of the entity identified',
        ROOT_CAUSE_ANALYSIS.ENTITY_NAME as ENTITY_NAME with synonyms=('component name','factor name') comment='Name of the entity identified',
        ROOT_CAUSE_ANALYSIS.DEFECT_TYPE as DEFECT_TYPE with synonyms=('defect category','failure type') comment='Type of defect this pattern is associated with',
        ROOT_CAUSE_ANALYSIS.DESCRIPTION as DESCRIPTION with synonyms=('pattern description','analysis description') comment='Detailed description of the root cause pattern',
        ROOT_CAUSE_ANALYSIS.CREATED_AT as CREATED_AT with synonyms=('analysis date','identified date') comment='When this pattern was identified',
        COMPONENT_RISK_SCORES.COMPONENT_ID as COMPONENT_ID with synonyms=('component code') comment='Unique identifier for the component',
        COMPONENT_RISK_SCORES.COMPONENT_TYPE as COMPONENT_TYPE with synonyms=('component category') comment='Type of component (supplier, station, material, etc.)',
        COMPONENT_RISK_SCORES.COMPONENT_NAME as COMPONENT_NAME with synonyms=('component') comment='Name of the component',
        COMPONENT_RISK_SCORES.LAST_UPDATED as LAST_UPDATED with synonyms=('score date','updated date') comment='When the risk score was last calculated'
    )
    metrics (
        ROOT_CAUSE_ANALYSIS.AVG_CORRELATION_SCORE as AVG(CORRELATION_SCORE) with synonyms=('average confidence','mean pattern strength') comment='Average correlation score across patterns',
        ROOT_CAUSE_ANALYSIS.TOTAL_PATTERNS as COUNT(DISTINCT ANALYSIS_ID) with synonyms=('pattern count','number of patterns') comment='Count of identified patterns',
        ROOT_CAUSE_ANALYSIS.TOTAL_DEFECTS_EXPLAINED as SUM(DEFECT_COUNT) with synonyms=('defects explained') comment='Total defects explained by patterns',
        ROOT_CAUSE_ANALYSIS.TOTAL_AFFECTED_WORK_ORDERS as SUM(AFFECTED_WORK_ORDERS) with synonyms=('work orders impacted') comment='Total work orders affected by identified patterns',
        COMPONENT_RISK_SCORES.AVG_RISK_SCORE as AVG(RISK_SCORE) with synonyms=('average risk','mean risk') comment='Average risk score across components',
        COMPONENT_RISK_SCORES.MAX_RISK_SCORE as MAX(RISK_SCORE) with synonyms=('highest risk','peak risk') comment='Maximum risk score',
        COMPONENT_RISK_SCORES.HIGH_RISK_COMPONENTS as COUNT(DISTINCT CASE WHEN RISK_SCORE >= 70 THEN COMPONENT_ID END) with synonyms=('high risk count') comment='Count of components with risk score >= 70',
        COMPONENT_RISK_SCORES.COMPONENT_COUNT as COUNT(DISTINCT COMPONENT_ID) with synonyms=('number of components') comment='Count of components with risk scores'
    )
    comment='GNN-identified root cause patterns and correlations - answers ''What are the AI-identified root cause patterns?''';
