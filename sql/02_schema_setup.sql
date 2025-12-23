-- =============================================================================
-- GNN Process Traceability - Schema-Level Setup
-- =============================================================================
-- This script creates schema-level objects:
--   1. File formats
--   2. Stages
--   3. Bronze layer tables
--   4. Gold layer tables (populated by notebook)
--   5. Utility views
--
-- Prerequisites: Role, database, schema, and warehouse set by shell script
-- Note: No CHECK constraints used (not supported by Snowflake)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. File Formats
-- -----------------------------------------------------------------------------
CREATE FILE FORMAT IF NOT EXISTS CSV_FORMAT
    TYPE = 'CSV'
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    SKIP_HEADER = 1
    NULL_IF = ('NULL', 'null', '')
    COMMENT = 'Standard CSV format for data loading';

-- -----------------------------------------------------------------------------
-- 2. Stages
-- -----------------------------------------------------------------------------
CREATE STAGE IF NOT EXISTS DATA_STAGE
    COMMENT = 'Stage for data files and Streamlit app';

CREATE STAGE IF NOT EXISTS MODELS_STAGE
    COMMENT = 'Stage for notebooks and model files';

-- -----------------------------------------------------------------------------
-- 3. Bronze Layer Tables
-- -----------------------------------------------------------------------------

-- Suppliers master data
-- Valid categories: steel, hydraulics, electronics, fasteners, seals, bearings, coatings, castings, electrical, tooling
CREATE TABLE IF NOT EXISTS SUPPLIERS (
    SUPPLIER_ID VARCHAR(20) NOT NULL,
    NAME VARCHAR(100) NOT NULL,
    CATEGORY VARCHAR(50) NOT NULL,
    LOCATION VARCHAR(100),
    QUALITY_RATING FLOAT,  -- Range: 0.0-5.0 (enforced at application level)
    CERTIFICATIONS VARCHAR(500),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (SUPPLIER_ID)
)
COMMENT = 'Supplier master data for manufacturing components';

-- Stations (manufacturing equipment)
-- Valid types: machining, welding, heat_treatment, assembly, testing
CREATE TABLE IF NOT EXISTS STATIONS (
    STATION_ID VARCHAR(20) NOT NULL,
    NAME VARCHAR(100) NOT NULL,
    TYPE VARCHAR(50) NOT NULL,
    LINE VARCHAR(20),
    CAPACITY INTEGER,
    LAST_MAINTENANCE DATE,
    PRIMARY KEY (STATION_ID)
)
COMMENT = 'Manufacturing station/equipment master data';

-- Materials inventory
CREATE TABLE IF NOT EXISTS MATERIALS (
    MATERIAL_ID VARCHAR(20) NOT NULL,
    SUPPLIER_ID VARCHAR(20) NOT NULL,
    BATCH_NUMBER VARCHAR(50),
    MATERIAL_TYPE VARCHAR(50) NOT NULL,
    SPECS VARIANT,  -- JSON with material specifications
    RECEIVED_DATE DATE,
    QUANTITY INTEGER,
    UNIT_COST FLOAT,
    PRIMARY KEY (MATERIAL_ID),
    FOREIGN KEY (SUPPLIER_ID) REFERENCES SUPPLIERS(SUPPLIER_ID)
)
COMMENT = 'Material inventory with batch tracking';

-- Work orders (production orders)
-- Valid product families: Excavator, Loader, Bulldozer, Grader
-- Valid product series: Standard, HD-Series, Compact
-- Valid statuses: completed, in_progress, quality_hold
CREATE TABLE IF NOT EXISTS WORK_ORDERS (
    WORK_ORDER_ID VARCHAR(20) NOT NULL,
    PRODUCT_FAMILY VARCHAR(50) NOT NULL,
    PRODUCT_SERIES VARCHAR(20),
    SERIAL_NUMBER VARCHAR(50),
    START_DATE DATE,
    COMPLETION_DATE DATE,
    STATUS VARCHAR(20),
    PRIMARY KEY (WORK_ORDER_ID)
)
COMMENT = 'Production work orders for equipment manufacturing';

-- Process steps (manufacturing operations)
-- Valid step types: machining, welding, heat_treatment, assembly, testing
CREATE TABLE IF NOT EXISTS PROCESS_STEPS (
    STEP_ID VARCHAR(20) NOT NULL,
    WORK_ORDER_ID VARCHAR(20) NOT NULL,
    STATION_ID VARCHAR(20) NOT NULL,
    MATERIAL_ID VARCHAR(20),
    STEP_SEQUENCE INTEGER NOT NULL,
    STEP_TYPE VARCHAR(50) NOT NULL,
    START_TIMESTAMP TIMESTAMP_NTZ,
    END_TIMESTAMP TIMESTAMP_NTZ,
    OPERATOR_ID VARCHAR(20),
    PRIMARY KEY (STEP_ID),
    FOREIGN KEY (WORK_ORDER_ID) REFERENCES WORK_ORDERS(WORK_ORDER_ID),
    FOREIGN KEY (STATION_ID) REFERENCES STATIONS(STATION_ID),
    FOREIGN KEY (MATERIAL_ID) REFERENCES MATERIALS(MATERIAL_ID)
)
COMMENT = 'Manufacturing process steps with material and station tracking';

-- Process parameters (machine settings)
CREATE TABLE IF NOT EXISTS PROCESS_PARAMETERS (
    PARAM_ID VARCHAR(20) NOT NULL,
    STEP_ID VARCHAR(20) NOT NULL,
    TEMPERATURE FLOAT,  -- Celsius
    PRESSURE FLOAT,  -- PSI
    SPEED FLOAT,  -- RPM or mm/min
    DURATION INTEGER,  -- Seconds
    ADDITIONAL_PARAMS VARIANT,  -- JSON for step-specific parameters
    PRIMARY KEY (PARAM_ID),
    FOREIGN KEY (STEP_ID) REFERENCES PROCESS_STEPS(STEP_ID)
)
COMMENT = 'Machine parameters for each process step';

-- Defects (quality issues)
-- Valid defect types: hydraulic_seal_failure, cylinder_scoring, premature_wear, stress_fracture, etc.
-- Valid severities: critical, major, minor
-- Valid detection stages: in_process, final_inspection, field_return
CREATE TABLE IF NOT EXISTS DEFECTS (
    DEFECT_ID VARCHAR(20) NOT NULL,
    WORK_ORDER_ID VARCHAR(20) NOT NULL,
    DEFECT_TYPE VARCHAR(50) NOT NULL,
    SEVERITY VARCHAR(20) NOT NULL,
    DETECTION_DATE DATE,
    DETECTION_STAGE VARCHAR(50),
    DESCRIPTION VARCHAR(500),
    ROOT_CAUSE VARCHAR(100),  -- May be null initially, populated by analysis
    PRIMARY KEY (DEFECT_ID),
    FOREIGN KEY (WORK_ORDER_ID) REFERENCES WORK_ORDERS(WORK_ORDER_ID)
)
COMMENT = 'Quality defects with traceability to work orders';

-- -----------------------------------------------------------------------------
-- 4. Gold Layer Tables (Populated by Notebook)
-- -----------------------------------------------------------------------------

-- Root cause analysis results
-- Valid pattern types: supplier_issue, process_config
-- Valid entity types: supplier, station, material_batch, operator
CREATE TABLE IF NOT EXISTS ROOT_CAUSE_ANALYSIS (
    ANALYSIS_ID VARCHAR(20) NOT NULL,
    PATTERN_TYPE VARCHAR(50) NOT NULL,
    ENTITY_TYPE VARCHAR(50) NOT NULL,
    ENTITY_ID VARCHAR(50) NOT NULL,
    ENTITY_NAME VARCHAR(100),
    CORRELATION_SCORE FLOAT NOT NULL,  -- Range: 0.0-1.0 (enforced at application level)
    DEFECT_COUNT INTEGER,
    AFFECTED_WORK_ORDERS INTEGER,
    DESCRIPTION VARCHAR(500),
    RECOMMENDATIONS VARIANT,  -- JSON array of recommended actions
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (ANALYSIS_ID)
)
COMMENT = 'GNN-identified root cause patterns from defect analysis';

-- Component risk scores
-- Valid component types: supplier, station, material_batch, product_family
CREATE TABLE IF NOT EXISTS COMPONENT_RISK_SCORES (
    COMPONENT_ID VARCHAR(50) NOT NULL,
    COMPONENT_TYPE VARCHAR(50) NOT NULL,
    COMPONENT_NAME VARCHAR(100),
    RISK_SCORE FLOAT NOT NULL,  -- Range: 0.0-1.0 (enforced at application level)
    RISK_FACTORS VARIANT,  -- JSON object with contributing factors
    RELATED_DEFECTS INTEGER,
    LAST_UPDATED TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    PRIMARY KEY (COMPONENT_ID, COMPONENT_TYPE)
)
COMMENT = 'Risk scores for manufacturing components based on GNN analysis';

-- -----------------------------------------------------------------------------
-- 5. Utility Views
-- -----------------------------------------------------------------------------

-- View: Defects with full context
CREATE OR REPLACE VIEW VW_DEFECTS_WITH_CONTEXT AS
SELECT 
    d.DEFECT_ID,
    d.DEFECT_TYPE,
    d.SEVERITY,
    d.DETECTION_DATE,
    d.DETECTION_STAGE,
    d.DESCRIPTION,
    d.ROOT_CAUSE,
    wo.WORK_ORDER_ID,
    wo.PRODUCT_FAMILY,
    wo.PRODUCT_SERIES,
    wo.SERIAL_NUMBER,
    wo.STATUS AS WORK_ORDER_STATUS
FROM DEFECTS d
JOIN WORK_ORDERS wo ON d.WORK_ORDER_ID = wo.WORK_ORDER_ID;

-- View: Material traceability
CREATE OR REPLACE VIEW VW_MATERIAL_TRACEABILITY AS
SELECT 
    m.MATERIAL_ID,
    m.MATERIAL_TYPE,
    m.BATCH_NUMBER,
    s.SUPPLIER_ID,
    s.NAME AS SUPPLIER_NAME,
    s.CATEGORY AS SUPPLIER_CATEGORY,
    s.QUALITY_RATING AS SUPPLIER_RATING,
    m.SPECS,
    m.RECEIVED_DATE,
    COUNT(DISTINCT ps.WORK_ORDER_ID) AS USED_IN_WORK_ORDERS,
    COUNT(DISTINCT d.DEFECT_ID) AS ASSOCIATED_DEFECTS
FROM MATERIALS m
JOIN SUPPLIERS s ON m.SUPPLIER_ID = s.SUPPLIER_ID
LEFT JOIN PROCESS_STEPS ps ON m.MATERIAL_ID = ps.MATERIAL_ID
LEFT JOIN DEFECTS d ON ps.WORK_ORDER_ID = d.WORK_ORDER_ID
GROUP BY 
    m.MATERIAL_ID, m.MATERIAL_TYPE, m.BATCH_NUMBER,
    s.SUPPLIER_ID, s.NAME, s.CATEGORY, s.QUALITY_RATING,
    m.SPECS, m.RECEIVED_DATE;

-- View: Station performance
CREATE OR REPLACE VIEW VW_STATION_PERFORMANCE AS
SELECT 
    st.STATION_ID,
    st.NAME AS STATION_NAME,
    st.TYPE AS STATION_TYPE,
    st.LINE,
    COUNT(DISTINCT ps.STEP_ID) AS TOTAL_STEPS,
    COUNT(DISTINCT ps.WORK_ORDER_ID) AS WORK_ORDERS_PROCESSED,
    COUNT(DISTINCT d.DEFECT_ID) AS ASSOCIATED_DEFECTS,
    ROUND(COUNT(DISTINCT d.DEFECT_ID)::FLOAT / NULLIF(COUNT(DISTINCT ps.WORK_ORDER_ID), 0), 4) AS DEFECT_RATE
FROM STATIONS st
LEFT JOIN PROCESS_STEPS ps ON st.STATION_ID = ps.STATION_ID
LEFT JOIN DEFECTS d ON ps.WORK_ORDER_ID = d.WORK_ORDER_ID
GROUP BY 
    st.STATION_ID, st.NAME, st.TYPE, st.LINE;

-- View: Supplier risk summary
CREATE OR REPLACE VIEW VW_SUPPLIER_RISK AS
SELECT 
    s.SUPPLIER_ID,
    s.NAME AS SUPPLIER_NAME,
    s.CATEGORY,
    s.QUALITY_RATING,
    COUNT(DISTINCT m.MATERIAL_ID) AS TOTAL_MATERIALS,
    COUNT(DISTINCT m.BATCH_NUMBER) AS TOTAL_BATCHES,
    COUNT(DISTINCT d.DEFECT_ID) AS TOTAL_DEFECTS,
    COUNT(DISTINCT d.WORK_ORDER_ID) AS AFFECTED_WORK_ORDERS,
    ROUND(COUNT(DISTINCT d.DEFECT_ID)::FLOAT / NULLIF(COUNT(DISTINCT m.MATERIAL_ID), 0), 4) AS DEFECT_PER_MATERIAL
FROM SUPPLIERS s
LEFT JOIN MATERIALS m ON s.SUPPLIER_ID = m.SUPPLIER_ID
LEFT JOIN PROCESS_STEPS ps ON m.MATERIAL_ID = ps.MATERIAL_ID
LEFT JOIN DEFECTS d ON ps.WORK_ORDER_ID = d.WORK_ORDER_ID
GROUP BY 
    s.SUPPLIER_ID, s.NAME, s.CATEGORY, s.QUALITY_RATING;

-- -----------------------------------------------------------------------------
-- 6. Summary
-- -----------------------------------------------------------------------------
SELECT 'Schema-level setup completed successfully!' AS STATUS;

-- Show created objects
SELECT TABLE_NAME, TABLE_TYPE, COMMENT
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = CURRENT_SCHEMA()
ORDER BY TABLE_TYPE, TABLE_NAME;

