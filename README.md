# GNN Process Traceability

A Snowflake demo showcasing **Graph Neural Networks (GNN)** for tracing quality defects back through manufacturing processes to identify root causes. Designed for heavy industrial equipment manufacturing (excavators, loaders, bulldozers).

## The Problem

When quality defects emerge in the field, manufacturers face a critical challenge: tracing them back through complex manufacturing processes is slow, expensive, and often inconclusive. Traditional approaches analyze defects in isolation, missing **network effects** where root causes span multiple entities.

## The Solution

This demo models manufacturing as a connected network and uses GNN to discover hidden patterns:

- **Graph Construction**: Nodes represent suppliers, materials, work orders, process steps, and defects. Edges represent relationships (supplies, used_in, executed_at, resulted_in).
- **GNN Embedding**: Message-passing neural networks learn node representations that capture multi-hop relationships.
- **Root Cause Tracing**: Trace defects back through the graph to identify correlated suppliers, materials, and process parameters.
- **AI Insights**: Cortex Complete generates natural language explanations of discovered patterns.

## Hidden Patterns (Demo Data)

The demo data contains two deliberately planted patterns that traditional analysis would miss:

| Pattern | Description | Defect Rate |
|---------|-------------|-------------|
| **Supplier Issue** | Vulcan Steel Works batch #2847 has elevated sulfur content causing hydraulic failures | 45% vs 3% baseline |
| **Process Configuration** | Heat Treatment Line 3 uses wrong parameters (820C/45min) for HD-Series products | 55% vs 3% baseline |

## Quick Start

### Prerequisites

- Snowflake account with ACCOUNTADMIN access
- Snowflake CLI (`pip install snowflake-cli`)
- Configured connection (`snow connection add`)

### Deploy

```bash
# Clone the repository
git clone <repository-url>
cd gnn_process_traceability

# Deploy to Snowflake (creates database, tables, loads data, deploys apps)
./deploy.sh

# Check status
./run.sh status
```

### Run

```bash
# Execute the GNN analysis notebook
./run.sh main

# Open the Streamlit dashboard
./run.sh streamlit
```

### Clean Up

```bash
# Remove all resources
./clean.sh --yes
```

## Project Structure

```
gnn_process_traceability/
├── data/
│   └── synthetic/                    # Pre-generated demo data
│       ├── suppliers.csv
│       ├── materials.csv
│       ├── work_orders.csv
│       ├── process_steps.csv
│       ├── process_parameters.csv
│       ├── stations.csv
│       └── defects.csv
├── docs/
│   └── TEST_PLAN.md                  # Comprehensive test plan
├── notebooks/
│   ├── gnn_traceability.ipynb        # GNN analysis notebook
│   ├── environment.yml               # Notebook dependencies
│   └── snowflake.yml                 # Notebook deployment config
├── solution_presentation/
│   ├── GNN_Quality_Traceability_Overview.md
│   ├── GNN_Quality_Traceability_Overview.pdf
│   ├── generate_images.py            # Image generator for presentation
│   └── images/                       # Presentation images
├── sql/
│   ├── 01_account_setup.sql          # Role, database, warehouse, compute pool
│   └── 02_schema_setup.sql           # Tables, stages, views
├── streamlit/
│   ├── snowflake.yml                 # Streamlit deployment config
│   ├── environment.yml               # Streamlit dependencies
│   ├── streamlit_app.py              # Main app entry
│   ├── pages/                        # Dashboard pages
│   │   ├── 1_Process_Network.py
│   │   ├── 2_Defect_Tracing.py
│   │   ├── 3_Risk_Analysis.py
│   │   └── 4_About.py
│   └── utils/                        # Utility modules
│       ├── ai_insights.py
│       ├── data_loader.py
│       ├── database.py
│       └── visualizations.py
├── utils/
│   ├── generate_synthetic_data.py    # Data generator (dev use only)
│   └── validate_notebook.py          # Notebook cell name validator
├── deploy.sh                         # One-time deployment
├── run.sh                            # Runtime operations
├── clean.sh                          # Cleanup script
├── create_user.sh                    # Create demo users with access
├── DRD.md                            # Design requirements document
└── README.md                         # This file
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Snowflake Platform                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────┐ │
│  │   Bronze     │    │    Silver    │    │     Gold     │    │Streamlit│ │
│  │   Layer      │───▶│    Layer     │───▶│    Layer     │───▶│  App   │ │
│  │              │    │  (Notebook)  │    │              │    │        │ │
│  │ - SUPPLIERS  │    │  - Graph     │    │ - ROOT_CAUSE │    │- Network│ │
│  │ - MATERIALS  │    │    Build     │    │   _ANALYSIS  │    │  Viz   │ │
│  │ - WORK_ORDERS│    │  - GNN       │    │ - COMPONENT  │    │- Defect│ │
│  │ - PROCESS_   │    │    Train     │    │   _RISK_     │    │  Trace │ │
│  │   STEPS      │    │  - Trace     │    │   SCORES     │    │- Risk  │ │
│  │ - DEFECTS    │    │    Defects   │    │              │    │  Scores│ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────┘ │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Dashboard Pages

| Page | Description |
|------|-------------|
| **Process Network** | Interactive graph visualization of manufacturing flow |
| **Defect Tracing** | Trace individual defects to root causes with AI explanation |
| **Risk Analysis** | Risk scores by supplier, station, product family |
| **About** | Solution overview and technology stack |

## Snowflake Resources Created

| Resource | Name |
|----------|------|
| Database | GNN_PROCESS_TRACEABILITY |
| Schema | GNN_PROCESS_TRACEABILITY |
| Role | GNN_PROCESS_TRACEABILITY_ROLE |
| Warehouse | GNN_PROCESS_TRACEABILITY_WH |
| Compute Pool | GNN_PROCESS_TRACEABILITY_COMPUTE_POOL |

## Deployment Options

```bash
# Full deployment
./deploy.sh

# Use different connection
./deploy.sh -c prod

# Deploy with environment prefix (for multi-environment)
./deploy.sh --prefix DEV

# Deploy only SQL setup
./deploy.sh --only-sql

# Deploy only data
./deploy.sh --only-data

# Deploy only notebook
./deploy.sh --only-notebook

# Deploy only Streamlit (for faster iteration)
./deploy.sh --only-streamlit

# Skip notebook deployment (useful if compute pool is unavailable)
./deploy.sh --skip-notebook
```

## Runtime Operations

```bash
# Execute GNN analysis notebook
./run.sh main

# Check resource status and table counts
./run.sh status

# Get notebook URL
./run.sh notebook

# Get Streamlit app URL
./run.sh streamlit

# Use different connection
./run.sh -c prod main
```

## Creating Demo Users

To create additional users with access to the demo:

```bash
# Create user with password
./create_user.sh -u demo_user -p TempPass123!

# Create user with specific connection
./create_user.sh -u demo_user -c prod -p TempPass123!

# Use environment prefix (matches deploy.sh --prefix option)
./create_user.sh -u demo_user --prefix DEV -p TempPass123!

# Show inferred configuration
./create_user.sh --show-config

# Dry run to preview SQL
./create_user.sh -u test_user --dry-run
```

## Technology Stack

- **Platform**: Snowflake (SPCS, Notebooks, Streamlit)
- **ML/AI**: PyTorch Geometric, NetworkX, Cortex Complete
- **Visualization**: Plotly, NetworkX layouts
- **Data**: Snowpark, Pandas

## Documentation

- [DRD.md](DRD.md) - Complete design requirements document
- [docs/TEST_PLAN.md](docs/TEST_PLAN.md) - Comprehensive test plan with validation steps
- [solution_presentation/](solution_presentation/) - Presentation materials and overview PDF
- [.cursor/rules](.cursor/rules) - Project standards and conventions
- [.cursor/SNOWFLAKE_NOTEBOOK_GUIDELINES.md](.cursor/SNOWFLAKE_NOTEBOOK_GUIDELINES.md) - Notebook development guide
- [.cursor/SNOWFLAKE_STREAMLIT_GUIDELINES.md](.cursor/SNOWFLAKE_STREAMLIT_GUIDELINES.md) - Streamlit development guide

## Troubleshooting

### Compute Pool Full Error

If you see "Notebook service is unschedulable in full compute pool":

```bash
# Stop all services on the compute pool
snow sql -q "ALTER COMPUTE POOL GNN_PROCESS_TRACEABILITY_COMPUTE_POOL STOP ALL;"
```

### Connection Issues

```bash
# Test connection
snow connection test -c demo

# List connections
snow connection list
```

### Redeploy Components

```bash
# Redeploy only Streamlit
./deploy.sh --only-streamlit

# Redeploy only notebook
./deploy.sh --only-notebook

# Reload data
./deploy.sh --only-data
```

### Debug Commands

```bash
# Check compute pool status
snow sql -q "SHOW COMPUTE POOLS LIKE 'GNN_PROCESS_TRACEABILITY%';"

# Check notebook status
snow sql -q "
    USE DATABASE GNN_PROCESS_TRACEABILITY;
    SHOW NOTEBOOKS LIKE 'GNN_PROCESS_TRACEABILITY%';
"

# Check Streamlit app status
snow sql -q "
    USE DATABASE GNN_PROCESS_TRACEABILITY;
    SHOW STREAMLITS LIKE 'GNN_PROCESS_TRACEABILITY%';
"
```

## License

MIT License - See [LICENSE](LICENSE) for details.
