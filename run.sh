#!/bin/bash
###############################################################################
# run.sh - Runtime operations for GNN Process Traceability
#
# Commands:
#   main       - Execute the GNN analysis notebook
#   status     - Check status of resources and table row counts
#   notebook   - Get notebook URL
#   streamlit  - Get Streamlit app URL
#
# Usage:
#   ./run.sh main                     # Execute notebook
#   ./run.sh status                   # Check resource status
#   ./run.sh streamlit                # Get Streamlit URL
#   ./run.sh -c prod main             # Use 'prod' connection
###############################################################################

set -e
set -o pipefail

# =============================================================================
# Configuration
# =============================================================================
CONNECTION_NAME="demo"
ENV_PREFIX=""
COMMAND=""

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
Usage: $0 [OPTIONS] COMMAND

Runtime operations for GNN Process Traceability.

Commands:
  main       Execute the GNN analysis notebook
  status     Check status of resources and table row counts
  notebook   Get notebook URL
  streamlit  Get Streamlit app URL

Options:
  -c, --connection NAME    Snowflake CLI connection name (default: demo)
  -p, --prefix PREFIX      Environment prefix for resources (e.g., DEV, PROD)
  -h, --help               Show this help message

Examples:
  $0 main                  # Execute notebook
  $0 status                # Check resource status
  $0 streamlit             # Get Streamlit URL
  $0 -c prod main          # Use 'prod' connection
EOF
    exit 0
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
        main|status|notebook|streamlit)
            COMMAND="$1"
            shift
            ;;
        *)
            error_exit "Unknown option: $1\nUse --help for usage information"
            ;;
    esac
done

# Require a command
if [ -z "$COMMAND" ]; then
    usage
fi

# =============================================================================
# Compute Resource Names
# =============================================================================

SNOW_CONN="-c $CONNECTION_NAME"

# Compute full prefix
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
NOTEBOOK_NAME="${FULL_PREFIX}_NOTEBOOK"
APP_NAME="${FULL_PREFIX}_APP"

# =============================================================================
# Command: main - Execute Notebook
# =============================================================================

cmd_main() {
    echo "=================================================="
    echo "GNN Process Traceability - Execute Notebook"
    echo "=================================================="
    echo ""
    echo "Configuration:"
    echo "  Notebook: $NOTEBOOK_NAME"
    echo "  Compute Pool: $COMPUTE_POOL"
    echo ""
    
    # Stop existing services on compute pool to free capacity
    echo "Step 1: Stopping existing services on compute pool..."
    snow sql $SNOW_CONN -q "
        USE ROLE ACCOUNTADMIN;
        ALTER COMPUTE POOL ${COMPUTE_POOL} STOP ALL;
    " 2>/dev/null || echo -e "${YELLOW}[WARN]${NC} Could not stop services (may be none running)"
    echo -e "${GREEN}[OK]${NC} Compute pool cleared"
    echo ""
    
    # Wait a moment for services to stop
    echo "Step 2: Waiting for compute pool to be ready..."
    sleep 5
    echo -e "${GREEN}[OK]${NC} Ready"
    echo ""
    
    # Execute notebook
    echo "Step 3: Executing notebook..."
    echo "  This may take several minutes..."
    
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        USE WAREHOUSE ${WAREHOUSE};
        
        EXECUTE NOTEBOOK ${NOTEBOOK_NAME}();
    "
    
    echo ""
    echo -e "${GREEN}[OK]${NC} Notebook execution completed"
    echo ""
    
    # Check results
    echo "Step 4: Verifying results..."
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        SELECT 'ROOT_CAUSE_ANALYSIS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM ROOT_CAUSE_ANALYSIS
        UNION ALL
        SELECT 'COMPONENT_RISK_SCORES', COUNT(*) FROM COMPONENT_RISK_SCORES;
    "
    
    echo ""
    echo "=================================================="
    echo -e "${GREEN}Notebook Execution Complete!${NC}"
    echo "=================================================="
    echo ""
    echo "Next: Open the dashboard with ./run.sh streamlit"
}

# =============================================================================
# Command: status - Check Resource Status
# =============================================================================

cmd_status() {
    echo "=================================================="
    echo "GNN Process Traceability - Status"
    echo "=================================================="
    echo ""
    
    echo "Checking resources..."
    echo ""
    
    # Check compute pool
    echo "Compute Pool Status:"
    snow sql $SNOW_CONN -q "SHOW COMPUTE POOLS LIKE '${COMPUTE_POOL}';" 2>/dev/null || echo "  Not found or no access"
    echo ""
    
    # Check warehouse
    echo "Warehouse Status:"
    snow sql $SNOW_CONN -q "SHOW WAREHOUSES LIKE '${WAREHOUSE}';" 2>/dev/null || echo "  Not found or no access"
    echo ""
    
    # Check table row counts
    echo "Table Row Counts:"
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        SELECT 'SUPPLIERS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM SUPPLIERS
        UNION ALL SELECT 'STATIONS', COUNT(*) FROM STATIONS
        UNION ALL SELECT 'MATERIALS', COUNT(*) FROM MATERIALS
        UNION ALL SELECT 'WORK_ORDERS', COUNT(*) FROM WORK_ORDERS
        UNION ALL SELECT 'PROCESS_STEPS', COUNT(*) FROM PROCESS_STEPS
        UNION ALL SELECT 'PROCESS_PARAMETERS', COUNT(*) FROM PROCESS_PARAMETERS
        UNION ALL SELECT 'DEFECTS', COUNT(*) FROM DEFECTS
        UNION ALL SELECT 'ROOT_CAUSE_ANALYSIS', COUNT(*) FROM ROOT_CAUSE_ANALYSIS
        UNION ALL SELECT 'COMPONENT_RISK_SCORES', COUNT(*) FROM COMPONENT_RISK_SCORES
        ORDER BY TABLE_NAME;
    " 2>/dev/null || echo "  Error querying tables"
    echo ""
    
    # Check defect patterns
    echo "Defect Pattern Summary:"
    snow sql $SNOW_CONN -q "
        USE ROLE ${ROLE};
        USE DATABASE ${DATABASE};
        USE SCHEMA ${SCHEMA};
        
        SELECT 
            ROOT_CAUSE,
            COUNT(*) AS DEFECT_COUNT
        FROM DEFECTS
        WHERE ROOT_CAUSE IS NOT NULL
        GROUP BY ROOT_CAUSE
        ORDER BY DEFECT_COUNT DESC;
    " 2>/dev/null || echo "  Error querying defects"
}

# =============================================================================
# Command: notebook - Get Notebook URL
# =============================================================================

cmd_notebook() {
    echo "=================================================="
    echo "GNN Process Traceability - Notebook"
    echo "=================================================="
    echo ""
    
    echo "Notebook: $NOTEBOOK_NAME"
    echo ""
    echo "To open the notebook:"
    echo "  1. Go to Snowsight (https://app.snowflake.com)"
    echo "  2. Navigate to: Projects > Notebooks"
    echo "  3. Open: $NOTEBOOK_NAME"
    echo ""
    echo "Or use the direct SQL command:"
    echo "  DESCRIBE NOTEBOOK ${DATABASE}.${SCHEMA}.${NOTEBOOK_NAME};"
}

# =============================================================================
# Command: streamlit - Get Streamlit URL
# =============================================================================

cmd_streamlit() {
    echo "=================================================="
    echo "GNN Process Traceability - Streamlit Dashboard"
    echo "=================================================="
    echo ""
    
    # Try to get URL
    URL=$(snow streamlit get-url ${APP_NAME} \
        $SNOW_CONN \
        --database $DATABASE \
        --schema $SCHEMA \
        --role $ROLE 2>/dev/null) || true
    
    if [ -n "$URL" ]; then
        echo "Streamlit Dashboard URL:"
        echo ""
        echo "  $URL"
    else
        echo "Could not retrieve URL automatically."
        echo ""
        echo "To open the dashboard:"
        echo "  1. Go to Snowsight (https://app.snowflake.com)"
        echo "  2. Navigate to: Projects > Streamlit"
        echo "  3. Open: $APP_NAME"
    fi
    echo ""
}

# =============================================================================
# Execute Command
# =============================================================================

case $COMMAND in
    main)
        cmd_main
        ;;
    status)
        cmd_status
        ;;
    notebook)
        cmd_notebook
        ;;
    streamlit)
        cmd_streamlit
        ;;
    *)
        error_exit "Unknown command: $COMMAND"
        ;;
esac

