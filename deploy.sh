#!/bin/bash
###############################################################################
# deploy.sh - Deploy GNN Process Traceability to Snowflake
#
# This script performs one-time deployment:
#   1. Checks prerequisites (snow CLI, files)
#   2. Runs account-level SQL (role, database, warehouse, compute pool)
#   3. Runs schema-level SQL (tables, stages, views)
#   4. Uploads data files to stage
#   5. Loads data into tables
#   6. Deploys notebook
#   7. Deploys Streamlit app
#
# Usage:
#   ./deploy.sh                       # Full deployment
#   ./deploy.sh -c prod               # Use 'prod' connection
#   ./deploy.sh --prefix DEV          # Deploy with DEV_ prefix
#   ./deploy.sh --only-streamlit      # Deploy only Streamlit app
###############################################################################

set -e
set -o pipefail

# =============================================================================
# Configuration
# =============================================================================
CONNECTION_NAME="demo"
ENV_PREFIX=""
ONLY_COMPONENT=""
SKIP_NOTEBOOK=false
SKIP_SEMANTIC_VIEWS=false
SKIP_AGENT=false

# Project settings
PROJECT_PREFIX="GNN_PROCESS_TRACEABILITY"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# =============================================================================
# Functions
# =============================================================================

error_exit() {
    echo -e "${RED}[ERROR] $1${NC}" >&2
    exit 1
}

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Deploy GNN Process Traceability to Snowflake.

Options:
  -c, --connection NAME    Snowflake CLI connection name (default: demo)
  -p, --prefix PREFIX      Environment prefix for resources (e.g., DEV, PROD)
  --only-sql               Run SQL setup only
  --only-data              Upload and load data only
  --only-notebook          Deploy notebook only
  --only-streamlit         Deploy Streamlit app only
  --only-semantic-views    Deploy semantic views only
  --only-agent             Deploy agent only
  --skip-notebook          Skip notebook deployment
  --skip-semantic-views    Skip semantic views deployment
  --skip-agent             Skip agent deployment
  -h, --help               Show this help message

Examples:
  $0                       # Full deployment
  $0 -c prod               # Use 'prod' connection
  $0 --prefix DEV          # Deploy with DEV_ prefix
  $0 --only-streamlit      # Redeploy Streamlit only
EOF
    exit 0
}

should_run_step() {
    local step_name="$1"
    # If no specific component requested, run all steps
    if [ -z "$ONLY_COMPONENT" ]; then
        return 0
    fi
    # Check if this step matches the requested component
    case "$ONLY_COMPONENT" in
        sql)
            [[ "$step_name" == "account_sql" || "$step_name" == "schema_sql" ]]
            ;;
        data)
            [[ "$step_name" == "upload_data" || "$step_name" == "load_data" ]]
            ;;
        notebook)
            [[ "$step_name" == "notebook" ]]
            ;;
        streamlit)
            [[ "$step_name" == "streamlit" ]]
            ;;
        semantic_views)
            [[ "$step_name" == "semantic_views" ]]
            ;;
        agent)
            [[ "$step_name" == "agent" ]]
            ;;
        *)
            return 1
            ;;
    esac
}

# =============================================================================
# Parse Arguments
# =============================================================================

while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            usage
            ;;
        -c|--connection)
            CONNECTION_NAME="$2"
            shift 2
            ;;
        -p|--prefix)
            ENV_PREFIX="$2"
            shift 2
            ;;
        --only-sql)
            ONLY_COMPONENT="sql"
            shift
            ;;
        --only-data)
            ONLY_COMPONENT="data"
            shift
            ;;
        --only-notebook)
            ONLY_COMPONENT="notebook"
            shift
            ;;
        --only-streamlit)
            ONLY_COMPONENT="streamlit"
            shift
            ;;
        --only-semantic-views)
            ONLY_COMPONENT="semantic_views"
            shift
            ;;
        --only-agent)
            ONLY_COMPONENT="agent"
            shift
            ;;
        --skip-notebook)
            SKIP_NOTEBOOK=true
            shift
            ;;
        --skip-semantic-views)
            SKIP_SEMANTIC_VIEWS=true
            shift
            ;;
        --skip-agent)
            SKIP_AGENT=true
            shift
            ;;
        *)
            error_exit "Unknown option: $1\nUse --help for usage information"
            ;;
    esac
done

# =============================================================================
# Compute Resource Names
# =============================================================================

SNOW_CONN="-c $CONNECTION_NAME"

# Compute full prefix (adds underscore only if prefix provided)
if [ -n "$ENV_PREFIX" ]; then
    FULL_PREFIX="${ENV_PREFIX}_${PROJECT_PREFIX}"
else
    FULL_PREFIX="${PROJECT_PREFIX}"
fi

# Derive all resource names
DATABASE="${FULL_PREFIX}"
SCHEMA="${PROJECT_PREFIX}"
ROLE="${FULL_PREFIX}_ROLE"
WAREHOUSE="${FULL_PREFIX}_WH"
COMPUTE_POOL="${FULL_PREFIX}_COMPUTE_POOL"
GPU_COMPUTE_POOL="${FULL_PREFIX}_GPU_COMPUTE_POOL"
NOTEBOOK_NAME="${FULL_PREFIX}_NOTEBOOK"
APP_NAME="${FULL_PREFIX}_APP"

# =============================================================================
# Display Configuration
# =============================================================================

echo "=================================================="
echo "GNN Process Traceability - Deployment"
echo "=================================================="
echo ""
echo "Configuration:"
echo "  Connection: $CONNECTION_NAME"
if [ -n "$ENV_PREFIX" ]; then
    echo "  Environment Prefix: $ENV_PREFIX"
fi
if [ -n "$ONLY_COMPONENT" ]; then
    echo "  Deploy Only: $ONLY_COMPONENT"
fi
echo "  Database: $DATABASE"
echo "  Schema: $SCHEMA"
echo "  Role: $ROLE"
echo "  Warehouse: $WAREHOUSE"
echo "  Compute Pool: $COMPUTE_POOL"
echo ""

###############################################################################
# Step 1: Check Prerequisites
###############################################################################

echo "Step 1: Checking prerequisites..."
echo "------------------------------------------------"

# Check for snow CLI
if ! command -v snow &> /dev/null; then
    error_exit "Snowflake CLI (snow) not found. Install with: pip install snowflake-cli"
fi
echo -e "${GREEN}[OK]${NC} Snowflake CLI found"

# Test Snowflake connection
echo "Testing Snowflake connection..."
if ! snow sql $SNOW_CONN -q "SELECT 1" &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Failed to connect to Snowflake"
    snow connection test $SNOW_CONN 2>&1 || true
    exit 1
fi
echo -e "${GREEN}[OK]${NC} Connection '$CONNECTION_NAME' verified"

# Check required files
for file in "sql/01_account_setup.sql" "sql/02_schema_setup.sql"; do
    if [ ! -f "$file" ]; then
        error_exit "Required file not found: $file"
    fi
done
echo -e "${GREEN}[OK]${NC} SQL files present"

# Check data files
if [ ! -d "data/synthetic" ] || [ -z "$(ls -A data/synthetic/*.csv 2>/dev/null)" ]; then
    error_exit "Data files not found in data/synthetic/. Run: python3 utils/generate_synthetic_data.py"
fi
echo -e "${GREEN}[OK]${NC} Data files present"
echo ""

###############################################################################
# Step 2: Run Account-Level SQL
###############################################################################

if should_run_step "account_sql"; then
    echo "Step 2: Running account-level SQL setup..."
    echo "------------------------------------------------"
    
    {
        echo "-- Set session variables for account-level objects"
        echo "SET FULL_PREFIX = '${FULL_PREFIX}';"
        echo "SET PROJECT_ROLE = '${ROLE}';"
        echo "SET PROJECT_WH = '${WAREHOUSE}';"
        echo "SET PROJECT_COMPUTE_POOL = '${COMPUTE_POOL}';"
        echo "SET PROJECT_GPU_COMPUTE_POOL = '${GPU_COMPUTE_POOL}';"
        echo "SET PROJECT_PYPI_NETWORK_RULE = '${FULL_PREFIX}_PYPI_NETWORK_RULE';"
        echo "SET PROJECT_EXTERNAL_ACCESS = '${FULL_PREFIX}_EXTERNAL_ACCESS';"
        echo "SET PROJECT_SCHEMA = '${SCHEMA}';"
        echo ""
        cat sql/01_account_setup.sql
    } | snow sql $SNOW_CONN -i
    
    echo -e "${GREEN}[OK]${NC} Account-level setup completed"
    echo ""
else
    echo "Step 2: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Step 3: Run Schema-Level SQL
###############################################################################

if should_run_step "schema_sql"; then
    echo "Step 3: Running schema-level SQL setup..."
    echo "------------------------------------------------"
    
    {
        echo "USE ROLE ${ROLE};"
        echo "USE DATABASE ${DATABASE};"
        echo "USE SCHEMA ${SCHEMA};"
        echo "USE WAREHOUSE ${WAREHOUSE};"
        echo ""
        cat sql/02_schema_setup.sql
    } | snow sql $SNOW_CONN -i
    
    echo -e "${GREEN}[OK]${NC} Schema-level setup completed"
    echo ""
else
    echo "Step 3: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Step 4: Upload Data Files to Stage
###############################################################################

if should_run_step "upload_data"; then
    echo "Step 4: Uploading data files to stage..."
    echo "------------------------------------------------"
    
    for csv_file in data/synthetic/*.csv; do
        filename=$(basename "$csv_file")
        echo "  Uploading $filename..."
        snow sql $SNOW_CONN -q "
            USE ROLE ${ROLE};
            USE DATABASE ${DATABASE};
            USE SCHEMA ${SCHEMA};
            PUT file://${SCRIPT_DIR}/${csv_file} @DATA_STAGE/raw/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        " > /dev/null
    done
    
    echo -e "${GREEN}[OK]${NC} Data files uploaded"
    echo ""
else
    echo "Step 4: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Step 5: Load Data into Tables
###############################################################################

if should_run_step "load_data"; then
    echo "Step 5: Loading data into tables..."
    echo "------------------------------------------------"
    
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        USE WAREHOUSE ${WAREHOUSE};
        
        -- Truncate tables for idempotent load
        TRUNCATE TABLE IF EXISTS DEFECTS;
        TRUNCATE TABLE IF EXISTS PROCESS_PARAMETERS;
        TRUNCATE TABLE IF EXISTS PROCESS_STEPS;
        TRUNCATE TABLE IF EXISTS WORK_ORDERS;
        TRUNCATE TABLE IF EXISTS MATERIALS;
        TRUNCATE TABLE IF EXISTS STATIONS;
        TRUNCATE TABLE IF EXISTS SUPPLIERS;
        
        -- Load in order (respecting foreign keys)
        COPY INTO SUPPLIERS FROM @DATA_STAGE/raw/suppliers.csv FILE_FORMAT = CSV_FORMAT;
        COPY INTO STATIONS FROM @DATA_STAGE/raw/stations.csv FILE_FORMAT = CSV_FORMAT;
        COPY INTO MATERIALS FROM @DATA_STAGE/raw/materials.csv FILE_FORMAT = CSV_FORMAT;
        COPY INTO WORK_ORDERS FROM @DATA_STAGE/raw/work_orders.csv FILE_FORMAT = CSV_FORMAT;
        COPY INTO PROCESS_STEPS FROM @DATA_STAGE/raw/process_steps.csv FILE_FORMAT = CSV_FORMAT;
        COPY INTO PROCESS_PARAMETERS FROM @DATA_STAGE/raw/process_parameters.csv FILE_FORMAT = CSV_FORMAT;
        COPY INTO DEFECTS FROM @DATA_STAGE/raw/defects.csv FILE_FORMAT = CSV_FORMAT;
        
        -- Show row counts
        SELECT 'SUPPLIERS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM SUPPLIERS
        UNION ALL SELECT 'STATIONS', COUNT(*) FROM STATIONS
        UNION ALL SELECT 'MATERIALS', COUNT(*) FROM MATERIALS
        UNION ALL SELECT 'WORK_ORDERS', COUNT(*) FROM WORK_ORDERS
        UNION ALL SELECT 'PROCESS_STEPS', COUNT(*) FROM PROCESS_STEPS
        UNION ALL SELECT 'PROCESS_PARAMETERS', COUNT(*) FROM PROCESS_PARAMETERS
        UNION ALL SELECT 'DEFECTS', COUNT(*) FROM DEFECTS;
    "
    
    echo -e "${GREEN}[OK]${NC} Data loaded"
    echo ""
else
    echo "Step 5: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Step 6: Deploy Notebook
###############################################################################

if should_run_step "notebook" && [ "$SKIP_NOTEBOOK" = false ]; then
    echo "Step 6: Deploying notebook..."
    echo "------------------------------------------------"
    
    if [ -f "notebooks/gnn_traceability.ipynb" ]; then
        # Upload notebook files
        snow sql $SNOW_CONN -q "
            USE ROLE ${ROLE};
            USE DATABASE ${DATABASE};
            USE SCHEMA ${SCHEMA};
            PUT file://${SCRIPT_DIR}/notebooks/gnn_traceability.ipynb @MODELS_STAGE/notebooks/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
        " > /dev/null
        
        # Upload environment.yml if exists
        if [ -f "notebooks/environment.yml" ]; then
            snow sql $SNOW_CONN -q "
                USE ROLE ${ROLE};
                USE DATABASE ${DATABASE};
                USE SCHEMA ${SCHEMA};
                PUT file://${SCRIPT_DIR}/notebooks/environment.yml @MODELS_STAGE/notebooks/ AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
            " > /dev/null
        fi
        
        # Create notebook
        snow sql $SNOW_CONN -q "
            USE ROLE ${ROLE};
            USE DATABASE ${DATABASE};
            USE SCHEMA ${SCHEMA};
            
            CREATE OR REPLACE NOTEBOOK ${NOTEBOOK_NAME}
                FROM '@MODELS_STAGE/notebooks/'
                MAIN_FILE = 'gnn_traceability.ipynb'
                RUNTIME_NAME = 'SYSTEM\$GPU_RUNTIME'
                COMPUTE_POOL = '${GPU_COMPUTE_POOL}'
                QUERY_WAREHOUSE = '${WAREHOUSE}'
                IDLE_AUTO_SHUTDOWN_TIME_SECONDS = 600
                EXTERNAL_ACCESS_INTEGRATIONS = (${FULL_PREFIX}_EXTERNAL_ACCESS)
                COMMENT = 'GNN Process Traceability - GPU-accelerated graph analysis notebook';
            
            -- Set live version for headless execution
            ALTER NOTEBOOK ${NOTEBOOK_NAME} ADD LIVE VERSION FROM LAST;
        " > /dev/null
        
        echo -e "${GREEN}[OK]${NC} Notebook deployed"
    else
        echo -e "${YELLOW}[WARN]${NC} Notebook file not found, skipping"
    fi
    echo ""
elif [ "$SKIP_NOTEBOOK" = true ]; then
    echo "Step 6: Skipped (--skip-notebook)"
    echo ""
else
    echo "Step 6: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Step 7: Deploy Streamlit App
###############################################################################

if should_run_step "streamlit"; then
    echo "Step 7: Deploying Streamlit app..."
    echo "------------------------------------------------"
    
    if [ -d "streamlit" ] && [ -f "streamlit/streamlit_app.py" ]; then
        # --- 7a: Clean up __pycache__ directories ---
        echo "  Cleaning up __pycache__ directories..."
        find streamlit -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        
        # --- 7b: Validate Python syntax before deployment ---
        echo "  Validating Python syntax..."
        for pyfile in $(find streamlit -name "*.py" -type f); do
            python3 -m py_compile "$pyfile" || error_exit "Syntax error in $pyfile"
        done
        # Clean up .pyc files created by validation
        find streamlit -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        echo -e "${GREEN}[OK]${NC} Python syntax validated"
        
        # --- 7c: Drop existing Streamlit app ---
        echo "  Dropping existing Streamlit app..."
        snow sql $SNOW_CONN -q "
            USE ROLE ${ROLE};
            USE DATABASE ${DATABASE};
            USE SCHEMA ${SCHEMA};
            DROP STREAMLIT IF EXISTS ${APP_NAME};
        " 2>/dev/null || true
        
        # Wait for Snowflake to fully release the dropped app
        echo "  Waiting for app cleanup..."
        sleep 3
        
        # --- 7d: Clear Streamlit stage files ---
        echo "  Clearing Streamlit stage files..."
        snow sql $SNOW_CONN -q "
            USE ROLE ${ROLE};
            USE DATABASE ${DATABASE};
            USE SCHEMA ${SCHEMA};
            REMOVE @STREAMLIT_STAGE PATTERN='.*';
        " 2>/dev/null || true
        
        # Clear local bundle cache
        rm -rf streamlit/output/bundle 2>/dev/null || true
        
        # --- 7e: Inject deployment timestamp for cache invalidation ---
        DEPLOY_TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        echo "  Injecting deployment timestamp: ${DEPLOY_TS}"
        # Backup original file
        cp streamlit/streamlit_app.py streamlit/streamlit_app.py.bak
        # Prepend timestamp comment
        echo "# Deploy: ${DEPLOY_TS}" | cat - streamlit/streamlit_app.py.bak > streamlit/streamlit_app.py
        
        # --- 7f: Deploy Streamlit app ---
        echo "  Deploying to Snowflake..."
        cd streamlit
        snow streamlit deploy \
            $SNOW_CONN \
            --database $DATABASE \
            --schema $SCHEMA \
            --role $ROLE \
            --replace 2>&1 || {
                echo -e "${YELLOW}[WARN]${NC} Streamlit deployment had warnings (may still work)"
            }
        cd ..
        
        # --- 7g: Restore original file (remove timestamp from local copy) ---
        mv streamlit/streamlit_app.py.bak streamlit/streamlit_app.py
        
        echo -e "${GREEN}[OK]${NC} Streamlit app deployed"
    else
        echo -e "${YELLOW}[WARN]${NC} Streamlit app not found, skipping"
    fi
    echo ""
else
    echo "Step 7: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Step 8: Deploy Semantic Views
###############################################################################

if should_run_step "semantic_views" && [ "$SKIP_SEMANTIC_VIEWS" = false ]; then
    echo "Step 8: Deploying semantic views..."
    echo "------------------------------------------------"
    
    if [ -d "semantic_models" ] && [ -n "$(ls -A semantic_models/*.sql 2>/dev/null)" ]; then
        for sv_file in semantic_models/*.sql; do
            sv_name=$(basename "$sv_file" .sql | tr '[:lower:]' '[:upper:]')
            echo "  Deploying $sv_name..."
            snow sql $SNOW_CONN -q "
                USE ROLE ${ROLE};
                USE DATABASE ${DATABASE};
                USE SCHEMA ${SCHEMA};
                USE WAREHOUSE ${WAREHOUSE};
            " > /dev/null
            
            # Execute the semantic view DDL
            {
                echo "USE ROLE ${ROLE};"
                echo "USE DATABASE ${DATABASE};"
                echo "USE SCHEMA ${SCHEMA};"
                echo "USE WAREHOUSE ${WAREHOUSE};"
                cat "$sv_file"
            } | snow sql $SNOW_CONN -i > /dev/null
        done
        
        echo -e "${GREEN}[OK]${NC} Semantic views deployed"
    else
        echo -e "${YELLOW}[WARN]${NC} No semantic view files found in semantic_models/, skipping"
    fi
    echo ""
elif [ "$SKIP_SEMANTIC_VIEWS" = true ]; then
    echo "Step 8: Skipped (--skip-semantic-views)"
    echo ""
else
    echo "Step 8: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Step 9: Deploy Cortex Agent
###############################################################################

if should_run_step "agent" && [ "$SKIP_AGENT" = false ]; then
    echo "Step 9: Deploying Cortex Agent..."
    echo "------------------------------------------------"
    
    if [ -d "agents" ] && [ -n "$(ls -A agents/*.sql 2>/dev/null)" ]; then
        for agent_file in agents/*.sql; do
            agent_name=$(basename "$agent_file" .sql | tr '[:lower:]' '[:upper:]')
            echo "  Deploying $agent_name..."
            
            # Substitute warehouse variable and execute agent DDL
            {
                echo "USE ROLE ${ROLE};"
                echo "USE DATABASE ${DATABASE};"
                echo "USE SCHEMA ${SCHEMA};"
                echo "USE WAREHOUSE ${WAREHOUSE};"
                # Replace ${WAREHOUSE} placeholder with actual warehouse name
                sed "s/\${WAREHOUSE}/${WAREHOUSE}/g" "$agent_file"
            } | snow sql $SNOW_CONN -i > /dev/null
        done
        
        echo -e "${GREEN}[OK]${NC} Cortex Agent deployed"
    else
        echo -e "${YELLOW}[WARN]${NC} No agent files found in agents/, skipping"
    fi
    echo ""
elif [ "$SKIP_AGENT" = true ]; then
    echo "Step 9: Skipped (--skip-agent)"
    echo ""
else
    echo "Step 9: Skipped (--only-$ONLY_COMPONENT)"
    echo ""
fi

###############################################################################
# Completion Summary
###############################################################################

echo "=================================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "=================================================="
echo ""

if [ -n "$ONLY_COMPONENT" ]; then
    echo "Deployed component: $ONLY_COMPONENT"
else
    echo "Next Steps:"
    echo "  1. Run the GNN analysis notebook:"
    echo "     ./run.sh main"
    echo ""
    echo "  2. Open the Streamlit dashboard:"
    echo "     ./run.sh streamlit"
    echo ""
    echo "  3. Chat with the Quality Engineer Agent in Snowsight"
    echo ""
    echo "Resources Created:"
    echo "  - Database: $DATABASE"
    echo "  - Schema: $DATABASE.$SCHEMA"
    echo "  - Role: $ROLE"
    echo "  - Warehouse: $WAREHOUSE"
    echo "  - Compute Pool: $COMPUTE_POOL"
    echo "  - Semantic Views: SM_DEFECT_ANALYSIS, SM_SUPPLIER_QUALITY, SM_STATION_PERFORMANCE,"
    echo "                    SM_PROCESS_PARAMETERS, SM_ROOT_CAUSE_PATTERNS, SM_MATERIAL_GENEALOGY"
    echo "  - Agent: QUALITY_ENGINEER_AGENT"
fi
echo ""

