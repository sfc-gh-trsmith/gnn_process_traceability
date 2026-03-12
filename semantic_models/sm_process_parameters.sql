CREATE OR REPLACE SEMANTIC VIEW SM_PROCESS_PARAMETERS
    tables (
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.PROCESS_PARAMETERS unique (PARAM_ID) comment='Machine parameters captured for each process step',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.PROCESS_STEPS unique (STEP_ID) comment='Process steps with station and work order context',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.WORK_ORDERS unique (WORK_ORDER_ID) comment='Production work orders',
        GNN_PROCESS_TRACEABILITY.GNN_PROCESS_TRACEABILITY.DEFECTS unique (DEFECT_ID) comment='Quality defects for correlation analysis'
    )
    relationships (
        PARAMETERS_TO_STEPS as PROCESS_PARAMETERS(STEP_ID) references PROCESS_STEPS(STEP_ID),
        PROCESS_STEPS_TO_WORK_ORDERS as PROCESS_STEPS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID),
        DEFECTS_TO_WORK_ORDERS as DEFECTS(WORK_ORDER_ID) references WORK_ORDERS(WORK_ORDER_ID)
    )
    facts (
        PROCESS_PARAMETERS.TEMPERATURE as TEMPERATURE with synonyms=('temp','process temperature') comment='Temperature setting during the process step (degrees)',
        PROCESS_PARAMETERS.PRESSURE as PRESSURE with synonyms=('process pressure') comment='Pressure setting during the process step (PSI)',
        PROCESS_PARAMETERS.SPEED as SPEED with synonyms=('process speed','rpm') comment='Speed setting during the process step',
        PROCESS_PARAMETERS.DURATION as DURATION with synonyms=('process duration','cycle time') comment='Duration of the process step (seconds)'
    )
    dimensions (
        PROCESS_PARAMETERS.PARAM_ID as PARAM_ID comment='Unique parameter record identifier',
        PROCESS_PARAMETERS.STEP_ID as PP_STEP_ID with synonyms=('process step') comment='Process step these parameters belong to',
        PROCESS_STEPS.STEP_ID as STEP_ID comment='Unique step identifier',
        PROCESS_STEPS.WORK_ORDER_ID as PS_WORK_ORDER_ID with synonyms=('work order','WO') comment='Associated work order',
        PROCESS_STEPS.STATION_ID as STATION_ID with synonyms=('station','equipment') comment='Station executing this step',
        PROCESS_STEPS.STEP_TYPE as STEP_TYPE with synonyms=('process type','operation') comment='Type of process step',
        PROCESS_STEPS.STEP_SEQUENCE as STEP_SEQUENCE comment='Sequence order of the step',
        PROCESS_STEPS.START_TIMESTAMP as START_TIMESTAMP with synonyms=('start time') comment='When the step started',
        PROCESS_STEPS.END_TIMESTAMP as END_TIMESTAMP with synonyms=('end time') comment='When the step ended',
        WORK_ORDERS.WORK_ORDER_ID as WORK_ORDER_ID with synonyms=('work order','WO') comment='Unique work order identifier',
        WORK_ORDERS.PRODUCT_FAMILY as PRODUCT_FAMILY with synonyms=('product line') comment='Product family',
        WORK_ORDERS.STATUS as STATUS with synonyms=('WO status') comment='Work order status',
        DEFECTS.DEFECT_ID as DEFECT_ID comment='Unique defect identifier',
        DEFECTS.DEFECT_TYPE as DEFECT_TYPE with synonyms=('defect category') comment='Type of defect',
        DEFECTS.SEVERITY as SEVERITY comment='Defect severity',
        DEFECTS.WORK_ORDER_ID as DEF_WORK_ORDER_ID comment='Work order with defect'
    )
    metrics (
        PROCESS_PARAMETERS.AVG_TEMPERATURE as AVG(TEMPERATURE) with synonyms=('average temperature','mean temp') comment='Average temperature across process steps',
        PROCESS_PARAMETERS.MIN_TEMPERATURE as MIN(TEMPERATURE) with synonyms=('minimum temperature','lowest temp') comment='Minimum temperature recorded',
        PROCESS_PARAMETERS.MAX_TEMPERATURE as MAX(TEMPERATURE) with synonyms=('maximum temperature','highest temp') comment='Maximum temperature recorded',
        PROCESS_PARAMETERS.TEMP_STD_DEV as STDDEV(TEMPERATURE) with synonyms=('temperature variance','temp variation') comment='Standard deviation of temperature',
        PROCESS_PARAMETERS.AVG_PRESSURE as AVG(PRESSURE) with synonyms=('average pressure','mean pressure') comment='Average pressure across process steps',
        PROCESS_PARAMETERS.PRESSURE_STD_DEV as STDDEV(PRESSURE) with synonyms=('pressure variance','pressure variation') comment='Standard deviation of pressure',
        PROCESS_PARAMETERS.AVG_SPEED as AVG(SPEED) with synonyms=('average speed','mean speed') comment='Average speed across process steps',
        PROCESS_PARAMETERS.AVG_DURATION as AVG(DURATION) with synonyms=('average duration','mean cycle time') comment='Average duration of process steps',
        PROCESS_STEPS.TOTAL_STEPS as COUNT(DISTINCT STEP_ID) with synonyms=('step count') comment='Count of process steps',
        DEFECTS.TOTAL_DEFECTS as COUNT(DISTINCT DEFECT_ID) with synonyms=('defect count') comment='Count of defects'
    )
    comment='Process parameter drift analysis - answers ''Are process parameters within spec? Any correlation to defects?''';
