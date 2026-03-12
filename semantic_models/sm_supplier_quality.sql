CREATE OR REPLACE SEMANTIC VIEW SM_SUPPLIER_QUALITY
    tables (
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.SUPPLIERS unique (SUPPLIER_ID) comment='Supplier master data for manufacturing components',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.MATERIALS unique (MATERIAL_ID) comment='Material inventory with batch tracking',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.WORK_ORDERS unique (WORK_ORDER_ID) comment='Production work orders',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.DEFECTS unique (DEFECT_ID) comment='Quality defects linked to materials',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.PROCESS_STEPS unique (STEP_ID) comment='Process steps linking materials to work orders'
    )
    relationships (
        MATERIALS_TO_SUPPLIERS as MATERIALS(SUPPLIER_ID) references SUPPLIERS(SUPPLIER_ID),
        DEFECTS_TO_WORK_ORDERS as DEFECTS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID),
        PROCESS_STEPS_TO_MATERIALS as PROCESS_STEPS(MATERIAL_ID) references MATERIALS(MATERIAL_ID),
        PROCESS_STEPS_TO_WORK_ORDERS as PROCESS_STEPS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID)
    )
    facts (
        SUPPLIERS.QUALITY_RATING as QUALITY_RATING with synonyms=('supplier rating','vendor rating','quality score') comment='Quality rating of the supplier (0-100)'
    )
    dimensions (
        SUPPLIERS.SUPPLIER_ID as SUPPLIER_ID with synonyms=('supplier code','vendor id') comment='Unique identifier for supplier',
        SUPPLIERS.SUPPLIER_NAME as NAME with synonyms=('supplier','vendor name','vendor') comment='Name of the supplier',
        SUPPLIERS.CATEGORY as CATEGORY with synonyms=('supplier category','vendor category','supplier type') comment='Category of materials/components supplied',
        MATERIALS.MATERIAL_ID as MATERIAL_ID with synonyms=('material code','part id') comment='Unique identifier for material',
        MATERIALS.MATERIAL_TYPE as MATERIAL_TYPE with synonyms=('material category','part type') comment='Type/category of material',
        MATERIALS.BATCH_NUMBER as BATCH_NUMBER with synonyms=('lot number','batch','lot') comment='Batch/lot number for traceability',
        MATERIALS.SUPPLIER_ID as MAT_SUPPLIER_ID comment='Supplier who provided this material',
        MATERIALS.RECEIVED_DATE as RECEIVED_DATE with synonyms=('receipt date','delivery date','incoming date') comment='Date material was received',
        WORK_ORDERS.WORK_ORDER_ID as WORK_ORDER_ID with synonyms=('work order','WO') comment='Unique work order identifier',
        WORK_ORDERS.PRODUCT_FAMILY as PRODUCT_FAMILY with synonyms=('product line') comment='Product family being manufactured',
        WORK_ORDERS.STATUS as STATUS with synonyms=('WO status') comment='Work order status',
        DEFECTS.DEFECT_ID as DEFECT_ID comment='Unique defect identifier',
        DEFECTS.DEFECT_TYPE as DEFECT_TYPE with synonyms=('defect category','failure type') comment='Type of defect',
        DEFECTS.SEVERITY as SEVERITY comment='Defect severity level',
        DEFECTS.WORK_ORDER_ID as DEF_WORK_ORDER_ID comment='Work order associated with defect',
        PROCESS_STEPS.STEP_ID as STEP_ID comment='Unique step identifier',
        PROCESS_STEPS.WORK_ORDER_ID as PS_WORK_ORDER_ID comment='Work order for this step',
        PROCESS_STEPS.MATERIAL_ID as PS_MATERIAL_ID comment='Material used in this step'
    )
    metrics (
        SUPPLIERS.AVG_QUALITY_RATING as AVG(QUALITY_RATING) with synonyms=('average rating','mean quality rating') comment='Average quality rating across suppliers',
        SUPPLIERS.SUPPLIER_COUNT as COUNT(DISTINCT SUPPLIER_ID) with synonyms=('number of suppliers','total suppliers') comment='Count of suppliers',
        MATERIALS.TOTAL_MATERIALS as COUNT(DISTINCT MATERIAL_ID) with synonyms=('material count','parts count') comment='Count of distinct materials',
        MATERIALS.TOTAL_BATCHES as COUNT(DISTINCT BATCH_NUMBER) with synonyms=('batch count','lot count') comment='Count of distinct batches',
        WORK_ORDERS.TOTAL_WORK_ORDERS as COUNT(DISTINCT WORK_ORDER_ID) with synonyms=('WO count') comment='Count of work orders',
        DEFECTS.TOTAL_DEFECTS as COUNT(DISTINCT DEFECT_ID) with synonyms=('defect count') comment='Count of defects'
    )
    comment='Incoming material quality analysis - answers ''Which suppliers are contributing to quality issues?''';
