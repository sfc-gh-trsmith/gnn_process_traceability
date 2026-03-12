CREATE OR REPLACE SEMANTIC VIEW SM_DEFECT_ANALYSIS
    tables (
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.DEFECTS unique (DEFECT_ID) comment='Quality defects with traceability to work orders',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.WORK_ORDERS unique (WORK_ORDER_ID) comment='Production work orders for equipment manufacturing'
    )
    relationships (
        DEFECTS_TO_WORK_ORDERS as DEFECTS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID)
    )
    dimensions (
        DEFECTS.DEFECT_ID as DEFECT_ID with synonyms=('defect number','defect code') comment='Unique identifier for each defect',
        DEFECTS.DEFECT_TYPE as DEFECT_TYPE with synonyms=('defect category','type of defect','failure type') comment='Classification of the defect (e.g., solder, alignment, contamination)',
        DEFECTS.SEVERITY as SEVERITY with synonyms=('defect severity','criticality','severity level') comment='Severity classification of the defect (Critical, Major, Minor)',
        DEFECTS.DETECTION_STAGE as DETECTION_STAGE with synonyms=('inspection stage','where detected','detection point') comment='Manufacturing stage where defect was detected',
        DEFECTS.ROOT_CAUSE as ROOT_CAUSE with synonyms=('cause','reason','failure cause') comment='Identified root cause of the defect',
        DEFECTS.DESCRIPTION as DESCRIPTION with synonyms=('defect description','details') comment='Detailed description of the defect',
        DEFECTS.WORK_ORDER_ID as WORK_ORDER_ID with synonyms=('work order','WO','production order') comment='Work order associated with this defect',
        DEFECTS.DETECTION_DATE as DETECTION_DATE with synonyms=('defect date','found date','when detected') comment='Date when the defect was detected',
        WORK_ORDERS.WORK_ORDER_ID as WO_WORK_ORDER_ID with synonyms=('work order','WO','production order') comment='Unique work order identifier',
        WORK_ORDERS.PRODUCT_FAMILY as PRODUCT_FAMILY with synonyms=('product line','family') comment='Product family being manufactured',
        WORK_ORDERS.PRODUCT_SERIES as PRODUCT_SERIES with synonyms=('series','model series') comment='Product series within the family',
        WORK_ORDERS.SERIAL_NUMBER as SERIAL_NUMBER with synonyms=('serial','unit serial') comment='Serial number of the manufactured unit',
        WORK_ORDERS.STATUS as STATUS with synonyms=('work order status','WO status') comment='Current status of the work order',
        WORK_ORDERS.START_DATE as START_DATE with synonyms=('production start','WO start date') comment='Date when production started',
        WORK_ORDERS.COMPLETION_DATE as COMPLETION_DATE with synonyms=('production end','WO completion date') comment='Date when production completed'
    )
    metrics (
        DEFECTS.TOTAL_DEFECTS as COUNT(DISTINCT DEFECT_ID) with synonyms=('defect count','number of defects') comment='Total count of defects',
        DEFECTS.CRITICAL_DEFECTS as COUNT(DISTINCT CASE WHEN SEVERITY = 'Critical' THEN DEFECT_ID END) with synonyms=('critical count','critical issues') comment='Count of critical severity defects',
        DEFECTS.MAJOR_DEFECTS as COUNT(DISTINCT CASE WHEN SEVERITY = 'Major' THEN DEFECT_ID END) with synonyms=('major count','major issues') comment='Count of major severity defects',
        DEFECTS.MINOR_DEFECTS as COUNT(DISTINCT CASE WHEN SEVERITY = 'Minor' THEN DEFECT_ID END) with synonyms=('minor count','minor issues') comment='Count of minor severity defects',
        WORK_ORDERS.TOTAL_WORK_ORDERS as COUNT(DISTINCT WORK_ORDER_ID) with synonyms=('WO count','order count') comment='Total count of work orders',
        WORK_ORDERS.AFFECTED_WORK_ORDERS as COUNT(DISTINCT WORK_ORDER_ID) with synonyms=('WOs with defects','defective orders') comment='Work orders that have associated defects',
        DEFECT_RATE as defects.total_defects / NULLIF(work_orders.total_work_orders, 0) with synonyms=('defects per work order','DPU') comment='Average defects per work order'
    )
    comment='Defect investigation and quality analysis - answers ''What defects are occurring and how severe?''';
