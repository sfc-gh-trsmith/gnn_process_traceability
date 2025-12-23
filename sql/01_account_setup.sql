-- =============================================================================
-- GNN Process Traceability - Account-Level Setup
-- =============================================================================
-- This script creates account-level resources:
--   1. Project role
--   2. Database
--   3. Schema
--   4. Warehouse
--   5. Compute pool (for notebooks)
--   6. Ownership grants
--
-- Required Session Variables (set by shell script):
--   $FULL_PREFIX, $PROJECT_ROLE, $PROJECT_WH, $PROJECT_COMPUTE_POOL,
--   $PROJECT_SCHEMA
--
-- Must be run with ACCOUNTADMIN role.
-- =============================================================================

USE ROLE ACCOUNTADMIN;

-- -----------------------------------------------------------------------------
-- 1. Create Project Role
-- -----------------------------------------------------------------------------
CREATE ROLE IF NOT EXISTS IDENTIFIER($PROJECT_ROLE)
    COMMENT = 'Role for GNN Process Traceability demo';

-- Grant role to current user
SET MY_USER = (SELECT CURRENT_USER());
GRANT ROLE IDENTIFIER($PROJECT_ROLE) TO USER IDENTIFIER($MY_USER);

-- Grant role to SYSADMIN for administrative access
GRANT ROLE IDENTIFIER($PROJECT_ROLE) TO ROLE SYSADMIN;

-- -----------------------------------------------------------------------------
-- 2. Create Database
-- -----------------------------------------------------------------------------
CREATE DATABASE IF NOT EXISTS IDENTIFIER($FULL_PREFIX)
    COMMENT = 'Database for GNN Process Traceability demo';

-- -----------------------------------------------------------------------------
-- 3. Create Schema
-- -----------------------------------------------------------------------------
SET FQ_SCHEMA = $FULL_PREFIX || '.' || $PROJECT_SCHEMA;
CREATE SCHEMA IF NOT EXISTS IDENTIFIER($FQ_SCHEMA)
    COMMENT = 'Schema for GNN Process Traceability tables and objects';

-- -----------------------------------------------------------------------------
-- 4. Create Warehouse
-- -----------------------------------------------------------------------------
CREATE WAREHOUSE IF NOT EXISTS IDENTIFIER($PROJECT_WH)
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for GNN Process Traceability queries';

-- -----------------------------------------------------------------------------
-- 5. Create Compute Pool (for Notebooks)
-- -----------------------------------------------------------------------------
CREATE COMPUTE POOL IF NOT EXISTS IDENTIFIER($PROJECT_COMPUTE_POOL)
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = CPU_X64_S
    AUTO_RESUME = TRUE
    AUTO_SUSPEND_SECS = 300
    COMMENT = 'Compute pool for GNN Process Traceability notebooks';

-- -----------------------------------------------------------------------------
-- 6. Grant Ownership on All Resources
-- -----------------------------------------------------------------------------

-- Database ownership
GRANT OWNERSHIP ON DATABASE IDENTIFIER($FULL_PREFIX)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- Schema ownership
GRANT OWNERSHIP ON SCHEMA IDENTIFIER($FQ_SCHEMA)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- Warehouse ownership
GRANT OWNERSHIP ON WAREHOUSE IDENTIFIER($PROJECT_WH)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- Compute pool ownership
GRANT OWNERSHIP ON COMPUTE POOL IDENTIFIER($PROJECT_COMPUTE_POOL)
    TO ROLE IDENTIFIER($PROJECT_ROLE) COPY CURRENT GRANTS;

-- Grant usage on warehouse to role (needed for queries)
GRANT USAGE ON WAREHOUSE IDENTIFIER($PROJECT_WH) TO ROLE IDENTIFIER($PROJECT_ROLE);

-- Grant bind service endpoint permission for Streamlit apps
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE IDENTIFIER($PROJECT_ROLE);

-- -----------------------------------------------------------------------------
-- 7. Summary
-- -----------------------------------------------------------------------------
SELECT 'Account-level setup completed successfully!' AS STATUS;
SELECT 'Database: ' || $FULL_PREFIX AS RESOURCE;
SELECT 'Schema: ' || $FQ_SCHEMA AS RESOURCE;
SELECT 'Role: ' || $PROJECT_ROLE AS RESOURCE;
SELECT 'Warehouse: ' || $PROJECT_WH AS RESOURCE;
SELECT 'Compute Pool: ' || $PROJECT_COMPUTE_POOL AS RESOURCE;

