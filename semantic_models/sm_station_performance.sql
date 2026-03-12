CREATE OR REPLACE SEMANTIC VIEW SM_STATION_PERFORMANCE
    tables (
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.STATIONS unique (STATION_ID) comment='Manufacturing station/equipment master data',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.WORK_ORDERS unique (WORK_ORDER_ID) comment='Production work orders',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.PROCESS_STEPS unique (STEP_ID) comment='Manufacturing process steps executed at stations',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.DEFECTS unique (DEFECT_ID) comment='Quality defects associated with process steps'
    )
    relationships (
        PROCESS_STEPS_TO_STATIONS as PROCESS_STEPS(STATION_ID) references STATIONS(STATION_ID),
        PROCESS_STEPS_TO_WORK_ORDERS as PROCESS_STEPS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID),
        DEFECTS_TO_WORK_ORDERS as DEFECTS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID)
    )
    dimensions (
        STATIONS.STATION_ID as STATION_ID with synonyms=('station code','equipment id') comment='Unique identifier for the station',
        STATIONS.STATION_NAME as NAME with synonyms=('station','equipment name','machine name') comment='Name of the manufacturing station',
        STATIONS.STATION_TYPE as TYPE with synonyms=('equipment type','machine type') comment='Type of station (assembly, testing, etc.)',
        STATIONS.LINE as LINE with synonyms=('production line','manufacturing line') comment='Production line where station is located',
        WORK_ORDERS.WORK_ORDER_ID as WORK_ORDER_ID with synonyms=('work order','WO') comment='Unique work order identifier',
        WORK_ORDERS.PRODUCT_FAMILY as PRODUCT_FAMILY with synonyms=('product line') comment='Product family',
        WORK_ORDERS.STATUS as STATUS with synonyms=('WO status') comment='Work order status',
        PROCESS_STEPS.STEP_ID as STEP_ID comment='Unique process step identifier',
        PROCESS_STEPS.WORK_ORDER_ID as PS_WORK_ORDER_ID with synonyms=('work order','WO') comment='Work order being processed',
        PROCESS_STEPS.STATION_ID as PS_STATION_ID comment='Station executing this step',
        PROCESS_STEPS.STEP_TYPE as STEP_TYPE with synonyms=('process type','operation type') comment='Type of process step',
        PROCESS_STEPS.STEP_SEQUENCE as STEP_SEQUENCE with synonyms=('sequence number','step order') comment='Order of the step in the process',
        PROCESS_STEPS.OPERATOR_ID as OPERATOR_ID with synonyms=('operator','technician') comment='Operator who performed the step',
        PROCESS_STEPS.START_TIMESTAMP as START_TIMESTAMP with synonyms=('step start','operation start') comment='When the process step started',
        PROCESS_STEPS.END_TIMESTAMP as END_TIMESTAMP with synonyms=('step end','operation end') comment='When the process step ended',
        DEFECTS.DEFECT_ID as DEFECT_ID comment='Unique defect identifier',
        DEFECTS.DEFECT_TYPE as DEFECT_TYPE with synonyms=('defect category') comment='Type of defect',
        DEFECTS.SEVERITY as SEVERITY comment='Defect severity',
        DEFECTS.WORK_ORDER_ID as DEF_WORK_ORDER_ID comment='Work order with defect'
    )
    metrics (
        STATIONS.STATION_COUNT as COUNT(DISTINCT STATION_ID) with synonyms=('number of stations','equipment count') comment='Count of stations',
        WORK_ORDERS.TOTAL_WORK_ORDERS as COUNT(DISTINCT WORK_ORDER_ID) with synonyms=('WO count') comment='Count of work orders',
        PROCESS_STEPS.TOTAL_STEPS as COUNT(DISTINCT STEP_ID) with synonyms=('step count','operations count') comment='Total number of process steps',
        PROCESS_STEPS.WORK_ORDERS_PROCESSED as COUNT(DISTINCT WORK_ORDER_ID) with synonyms=('WOs processed','units processed') comment='Count of unique work orders processed',
        DEFECTS.TOTAL_DEFECTS as COUNT(DISTINCT DEFECT_ID) with synonyms=('defect count') comment='Count of defects'
    )
    comment='Equipment and process station health analysis - answers ''Which stations are underperforming?''';
