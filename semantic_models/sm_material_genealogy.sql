CREATE OR REPLACE SEMANTIC VIEW SM_MATERIAL_GENEALOGY
    tables (
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.MATERIALS unique (MATERIAL_ID) comment='Material inventory with batch tracking for traceability',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SUPPLIERS unique (SUPPLIER_ID) comment='Supplier information for material sourcing',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.PROCESS_STEPS unique (STEP_ID) comment='Process steps showing where materials were used',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.WORK_ORDERS unique (WORK_ORDER_ID) comment='Work orders for production context',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.DEFECTS unique (DEFECT_ID) comment='Quality defects for traceability impact analysis'
    )
    relationships (
        MATERIALS_TO_SUPPLIERS as MATERIALS(SUPPLIER_ID) references SUPPLIERS(SUPPLIER_ID),
        PROCESS_STEPS_TO_MATERIALS as PROCESS_STEPS(MATERIAL_ID) references MATERIALS(MATERIAL_ID),
        PROCESS_STEPS_TO_WORK_ORDERS as PROCESS_STEPS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID),
        DEFECTS_TO_WORK_ORDERS as DEFECTS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID)
    )
    facts (
        SUPPLIERS.QUALITY_RATING as QUALITY_RATING with synonyms=('supplier rating') comment='Supplier quality rating'
    )
    dimensions (
        MATERIALS.MATERIAL_ID as MATERIAL_ID with synonyms=('material code','part id') comment='Unique identifier for material',
        MATERIALS.MATERIAL_TYPE as MATERIAL_TYPE with synonyms=('material category','part type','component type') comment='Type/category of material',
        MATERIALS.BATCH_NUMBER as BATCH_NUMBER with synonyms=('lot number','batch','lot','batch id') comment='Batch/lot number for traceability',
        MATERIALS.SUPPLIER_ID as MAT_SUPPLIER_ID comment='Supplier who provided this material',
        MATERIALS.RECEIVED_DATE as RECEIVED_DATE with synonyms=('receipt date','delivery date','incoming date') comment='Date material was received',
        SUPPLIERS.SUPPLIER_ID as SUPPLIER_ID comment='Unique supplier identifier',
        SUPPLIERS.SUPPLIER_NAME as NAME with synonyms=('supplier','vendor name') comment='Name of the supplier',
        SUPPLIERS.CATEGORY as CATEGORY with synonyms=('supplier category') comment='Supplier category',
        PROCESS_STEPS.STEP_ID as STEP_ID comment='Unique step identifier',
        PROCESS_STEPS.WORK_ORDER_ID as PS_WORK_ORDER_ID with synonyms=('work order','WO','production order') comment='Work order where material was used',
        PROCESS_STEPS.MATERIAL_ID as PS_MATERIAL_ID comment='Material used in this step',
        PROCESS_STEPS.STATION_ID as STATION_ID with synonyms=('station') comment='Station where step was performed',
        PROCESS_STEPS.STEP_TYPE as STEP_TYPE with synonyms=('process type') comment='Type of process step',
        PROCESS_STEPS.START_TIMESTAMP as START_TIMESTAMP with synonyms=('process date','usage date') comment='When the material was used',
        WORK_ORDERS.WORK_ORDER_ID as WORK_ORDER_ID with synonyms=('work order','WO') comment='Work order identifier',
        WORK_ORDERS.PRODUCT_FAMILY as PRODUCT_FAMILY with synonyms=('product line') comment='Product family',
        WORK_ORDERS.PRODUCT_SERIES as PRODUCT_SERIES with synonyms=('series','model') comment='Product series',
        WORK_ORDERS.SERIAL_NUMBER as SERIAL_NUMBER with synonyms=('serial','unit serial') comment='Serial number of manufactured unit',
        WORK_ORDERS.STATUS as STATUS with synonyms=('WO status') comment='Work order status',
        WORK_ORDERS.START_DATE as START_DATE with synonyms=('production start') comment='Production start date',
        WORK_ORDERS.COMPLETION_DATE as COMPLETION_DATE with synonyms=('production end') comment='Production completion date',
        DEFECTS.DEFECT_ID as DEFECT_ID comment='Unique defect identifier',
        DEFECTS.DEFECT_TYPE as DEFECT_TYPE with synonyms=('defect category','failure type') comment='Type of defect',
        DEFECTS.SEVERITY as SEVERITY comment='Defect severity',
        DEFECTS.WORK_ORDER_ID as DEF_WORK_ORDER_ID comment='Affected work order',
        DEFECTS.ROOT_CAUSE as ROOT_CAUSE comment='Identified root cause'
    )
    metrics (
        MATERIALS.TOTAL_MATERIALS as COUNT(DISTINCT MATERIAL_ID) with synonyms=('material count') comment='Count of distinct materials',
        MATERIALS.TOTAL_BATCHES as COUNT(DISTINCT BATCH_NUMBER) with synonyms=('batch count','lot count') comment='Count of distinct batches',
        SUPPLIERS.SUPPLIER_COUNT as COUNT(DISTINCT SUPPLIER_ID) with synonyms=('number of suppliers') comment='Count of suppliers',
        PROCESS_STEPS.TOTAL_USAGE as COUNT(DISTINCT STEP_ID) with synonyms=('usage count','times used') comment='Number of times materials were used',
        WORK_ORDERS.TOTAL_WORK_ORDERS as COUNT(DISTINCT WORK_ORDER_ID) with synonyms=('WO count','units affected') comment='Count of work orders',
        DEFECTS.TOTAL_DEFECTS as COUNT(DISTINCT DEFECT_ID) with synonyms=('defect count') comment='Count of defects'
    )
    comment='Lot/batch traceability analysis - answers ''Where was this material used and what defects occurred?''';
