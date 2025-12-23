# GNN Process Traceability - Design Requirements Document

## 1. Executive Summary

### Business Objective

Heavy industrial equipment manufacturers face a critical challenge: when quality defects emerge in the field, tracing them back to root causes through complex manufacturing processes is slow, expensive, and often inconclusive. Traditional approaches analyze defects in isolation, missing the **network effects** where root causes span multiple entities (suppliers, materials, process steps).

This demo showcases how **Graph Neural Networks (GNN)** on Snowflake can model manufacturing as a connected network, enabling rapid identification of hidden patterns that conventional analysis would miss.

### Technical Approach

- **Graph Construction**: Model manufacturing as nodes (suppliers, materials, work orders, process steps, defects) connected by edges (supplies, used_in, executed_at, resulted_in)
- **GNN Embedding**: Use message-passing neural networks to learn node representations that capture multi-hop relationships
- **Root Cause Tracing**: Trace defects back through the graph to identify correlated suppliers, materials, and process parameters
- **AI Insights**: Use Cortex Complete to generate natural language explanations of discovered patterns

### Hidden Patterns (Planted in Data)

The demo data contains two deliberately planted patterns that traditional analysis would miss:

| Pattern | Description | Why GNN Finds It |
|---------|-------------|------------------|
| **Supplier Issue** | Vulcan Steel Works batch #2847 has elevated sulfur content causing hydraulic failures weeks after assembly | Defects span multiple product lines; GNN correlates through material-to-defect paths |
| **Process Configuration** | Heat Treatment Line 3 uses wrong parameters for HD-Series products | Only affects specific product+station combination; GNN identifies through process step embeddings |

---

## 2. Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Snowflake Platform                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌───────────┐ │
│  │   Bronze     │    │    Silver    │    │     Gold     │    │ Streamlit │ │
│  │   Layer      │───▶│    Layer     │───▶│    Layer     │───▶│   App     │ │
│  │              │    │              │    │              │    │           │ │
│  │ - SUPPLIERS  │    │  Notebook:   │    │ - ROOT_CAUSE │    │ - Network │ │
│  │ - MATERIALS  │    │  - Graph     │    │   _ANALYSIS  │    │   Viz     │ │
│  │ - WORK_ORDERS│    │    Build     │    │ - COMPONENT  │    │ - Defect  │ │
│  │ - PROCESS_   │    │  - GNN       │    │   _RISK_     │    │   Trace   │ │
│  │   STEPS      │    │    Train     │    │   SCORES     │    │ - Risk    │ │
│  │ - PROCESS_   │    │  - Trace     │    │              │    │   Scores  │ │
│  │   PARAMETERS │    │    Defects   │    │              │    │ - About   │ │
│  │ - DEFECTS    │    │              │    │              │    │           │ │
│  │ - STATIONS   │    │              │    │              │    │ + Cortex  │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └───────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         SPCS Compute Pool                             │   │
│  │                   (CPU_X64_S - Notebook Execution)                    │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Medallion Architecture

| Layer | Tables | Purpose |
|-------|--------|---------|
| Bronze | SUPPLIERS, MATERIALS, WORK_ORDERS, PROCESS_STEPS, PROCESS_PARAMETERS, DEFECTS, STATIONS | Raw data from manufacturing systems |
| Silver | (Notebook processing) | Graph construction, GNN training, defect tracing |
| Gold | ROOT_CAUSE_ANALYSIS, COMPONENT_RISK_SCORES | Curated insights for dashboard consumption |

---

## 3. Data Model

### Entity Relationship Diagram

```
┌─────────────┐     supplies      ┌─────────────┐
│  SUPPLIERS  │──────────────────▶│  MATERIALS  │
│             │                    │             │
│ supplier_id │                    │ material_id │
│ name        │                    │ supplier_id │
│ category    │                    │ batch_number│
│ location    │                    │ specs (JSON)│
│ quality_    │                    │ received_   │
│   rating    │                    │   date      │
└─────────────┘                    └──────┬──────┘
                                          │
                                          │ used_in
                                          ▼
┌─────────────┐     has_step       ┌─────────────┐
│ WORK_ORDERS │───────────────────▶│PROCESS_STEPS│
│             │                    │             │
│work_order_id│                    │ step_id     │
│product_     │                    │work_order_id│
│  family     │                    │ station_id  │
│serial_number│                    │ material_id │
│ start_date  │                    │ timestamp   │
│ status      │                    │ operator_id │
└──────┬──────┘                    └──────┬──────┘
       │                                  │
       │ resulted_in                      │ has_params
       ▼                                  ▼
┌─────────────┐                    ┌─────────────┐
│   DEFECTS   │                    │  PROCESS_   │
│             │                    │ PARAMETERS  │
│ defect_id   │                    │             │
│work_order_id│                    │ param_id    │
│ defect_type │                    │ step_id     │
│ severity    │                    │ temperature │
│ detection_  │                    │ pressure    │
│   date      │                    │ speed       │
│ description │                    │ duration    │
└─────────────┘                    └─────────────┘

┌─────────────┐
│  STATIONS   │
│             │
│ station_id  │
│ name        │
│ type        │
│ line        │
│ capacity    │
└─────────────┘
```

### Table Specifications

#### SUPPLIERS
| Column | Type | Description |
|--------|------|-------------|
| SUPPLIER_ID | VARCHAR(20) | Primary key (e.g., SUP-001) |
| NAME | VARCHAR(100) | Company name |
| CATEGORY | VARCHAR(50) | steel, hydraulics, electronics, fasteners |
| LOCATION | VARCHAR(100) | City, State/Country |
| QUALITY_RATING | FLOAT | 0.0-5.0 scale |
| CERTIFICATIONS | VARCHAR(500) | Comma-separated certifications |
| CREATED_AT | TIMESTAMP_NTZ | Record creation timestamp |

#### MATERIALS
| Column | Type | Description |
|--------|------|-------------|
| MATERIAL_ID | VARCHAR(20) | Primary key (e.g., MAT-00001) |
| SUPPLIER_ID | VARCHAR(20) | Foreign key to SUPPLIERS |
| BATCH_NUMBER | VARCHAR(50) | Supplier batch identifier |
| MATERIAL_TYPE | VARCHAR(50) | steel_rod, hydraulic_seal, circuit_board, etc. |
| SPECS | VARIANT | JSON with material specifications |
| RECEIVED_DATE | DATE | Date received at facility |
| QUANTITY | INTEGER | Units received |
| UNIT_COST | FLOAT | Cost per unit |

#### WORK_ORDERS
| Column | Type | Description |
|--------|------|-------------|
| WORK_ORDER_ID | VARCHAR(20) | Primary key (e.g., WO-00001) |
| PRODUCT_FAMILY | VARCHAR(50) | Excavator, Loader, Bulldozer, Grader |
| PRODUCT_SERIES | VARCHAR(20) | Standard, HD-Series, Compact |
| SERIAL_NUMBER | VARCHAR(50) | Unit serial number |
| START_DATE | DATE | Production start date |
| COMPLETION_DATE | DATE | Production completion date |
| STATUS | VARCHAR(20) | completed, in_progress, quality_hold |

#### PROCESS_STEPS
| Column | Type | Description |
|--------|------|-------------|
| STEP_ID | VARCHAR(20) | Primary key (e.g., STEP-000001) |
| WORK_ORDER_ID | VARCHAR(20) | Foreign key to WORK_ORDERS |
| STATION_ID | VARCHAR(20) | Foreign key to STATIONS |
| MATERIAL_ID | VARCHAR(20) | Foreign key to MATERIALS (nullable) |
| STEP_SEQUENCE | INTEGER | Order within work order |
| STEP_TYPE | VARCHAR(50) | machining, welding, heat_treatment, assembly, testing |
| START_TIMESTAMP | TIMESTAMP_NTZ | Step start time |
| END_TIMESTAMP | TIMESTAMP_NTZ | Step end time |
| OPERATOR_ID | VARCHAR(20) | Operator identifier |

#### PROCESS_PARAMETERS
| Column | Type | Description |
|--------|------|-------------|
| PARAM_ID | VARCHAR(20) | Primary key (e.g., PARAM-000001) |
| STEP_ID | VARCHAR(20) | Foreign key to PROCESS_STEPS |
| TEMPERATURE | FLOAT | Celsius (nullable) |
| PRESSURE | FLOAT | PSI (nullable) |
| SPEED | FLOAT | RPM or mm/min (nullable) |
| DURATION | INTEGER | Seconds |
| ADDITIONAL_PARAMS | VARIANT | JSON for step-specific parameters |

#### DEFECTS
| Column | Type | Description |
|--------|------|-------------|
| DEFECT_ID | VARCHAR(20) | Primary key (e.g., DEF-0001) |
| WORK_ORDER_ID | VARCHAR(20) | Foreign key to WORK_ORDERS |
| DEFECT_TYPE | VARCHAR(50) | hydraulic_seal_failure, cylinder_scoring, premature_wear, stress_fracture, etc. |
| SEVERITY | VARCHAR(20) | critical, major, minor |
| DETECTION_DATE | DATE | When defect was detected |
| DETECTION_STAGE | VARCHAR(50) | in_process, final_inspection, field_return |
| DESCRIPTION | VARCHAR(500) | Detailed description |
| ROOT_CAUSE | VARCHAR(100) | Assigned root cause (may be null initially) |

#### STATIONS
| Column | Type | Description |
|--------|------|-------------|
| STATION_ID | VARCHAR(20) | Primary key (e.g., STN-001) |
| NAME | VARCHAR(100) | Station name |
| TYPE | VARCHAR(50) | machining, welding, heat_treatment, assembly, testing |
| LINE | VARCHAR(20) | Line 1, Line 2, Line 3 |
| CAPACITY | INTEGER | Units per hour |
| LAST_MAINTENANCE | DATE | Last maintenance date |

### Hidden Patterns Implementation

#### Pattern 1: Vulcan Steel Batch 2847

**Data Generation Rules:**
- Supplier "Vulcan Steel Works" (SUP-003) provides steel materials
- Batch #2847 has elevated sulfur content (recorded in SPECS JSON)
- Materials from this batch are used across multiple product lines
- Defects of type "hydraulic_seal_failure" and "cylinder_scoring" appear 4-8 weeks after assembly
- Defect rate: ~8% for batch 2847 vs ~0.5% baseline (16x higher risk)

**Graph Pattern:**
```
SUP-003 (Vulcan Steel) → MAT-* (batch=2847) → STEP-* → WO-* → DEF-* (hydraulic failures)
```

#### Pattern 2: Heat Treatment Line 3 + HD-Series

**Data Generation Rules:**
- Station "Heat Treatment Line 3" (STN-HT3) has incorrect temperature profile
- Parameters: 820°C/45min instead of correct 870°C/60min for HD-Series
- Only affects products with PRODUCT_SERIES = "HD-Series"
- Other lines (Line 1, Line 2) have correct parameters
- Defects of type "premature_wear" and "stress_fracture" appear
- Defect rate: ~8% for HD-Series on Line 3 vs ~0.5% baseline (16x higher risk)

**Graph Pattern:**
```
WO-* (HD-Series) → STEP-* (STN-HT3, temp=820) → PARAM-* → DEF-* (premature wear)
```

---

## 4. Notebook Specification (`notebooks/gnn_traceability.ipynb`)

### Section 1: Title and Objectives

**Cell Name:** `title_and_objectives`

Content:
- Business objective: Trace quality defects to root causes using graph intelligence
- Technical approach: Graph Neural Networks with message passing
- Learning objectives: Understand GNN for root cause analysis, graph construction, embedding interpretation
- Prerequisites: Basic ML/DL concepts, Python, SQL
- Notebook structure: Table of contents
- Output: ROOT_CAUSE_ANALYSIS and COMPONENT_RISK_SCORES tables

### Section 2: Environment Setup

**Cell Names:** `environment_setup_header`, `install_packages`, `import_libraries`, `snowflake_session_setup`

Packages to install:
```python
packages = ["torch", "torch-geometric", "networkx", "matplotlib", "seaborn"]
```

Session setup:
```python
from snowflake.snowpark.context import get_active_session
session = get_active_session()
```

### Section 3: Data Loading

**Cell Names:** `data_loading_header`, `load_bronze_tables`, `display_data_summary`

Load tables:
- SUPPLIERS, MATERIALS, WORK_ORDERS, PROCESS_STEPS, PROCESS_PARAMETERS, DEFECTS, STATIONS

Summary display:
- Record counts per table
- Date ranges
- Defect rate overview

### Section 4: Data Exploration

**Cell Names:** `data_exploration_header`, `defect_distribution_viz`, `supplier_quality_viz`, `process_parameter_analysis`

Visualizations:
- Defect type distribution (bar chart)
- Defects by product family (grouped bar)
- Supplier quality ratings distribution
- Process parameter distributions by station

### Section 5: Graph Construction

**Cell Names:** `graph_construction_header`, `graph_theory_explainer`, `create_node_mappings_cell`, `build_heterogeneous_graph_cell`, `graph_statistics_display`

Conceptual explanation (markdown):
```markdown
## Why Graph Neural Networks for Root Cause Analysis?

Traditional approaches analyze each defect independently, looking for correlations
in tabular data. This misses **network effects** where the root cause is not a
single attribute but a **path** through the manufacturing process.

### The Graph Perspective

We model manufacturing as a connected network:
- **Nodes** are entities: suppliers, materials, process steps, work orders, defects
- **Edges** are relationships: supplies, used_in, executed_at, resulted_in

### What GNN Learns

Through **message passing**, each node aggregates information from its neighbors:

$$h_v^{(l+1)} = \sigma\left( W \cdot \text{AGG}\left(\{h_u^{(l)} : u \in \mathcal{N}(v)\}\right) + B \cdot h_v^{(l)} \right)$$

Where:
- $h_v^{(l)}$ = embedding of node $v$ at layer $l$
- $\mathcal{N}(v)$ = neighbors of node $v$
- AGG = aggregation function (mean)
- $W$, $B$ = learnable weight matrices

With **2 layers**, a defect node's embedding contains information from:
- Its work order (1 hop)
- The process steps and materials in that work order (2 hops)

This enables root cause discovery that spans multiple entities.
```

Graph construction:
```python
# Node types: supplier, material, work_order, process_step, defect, station
# Edge types: supplies, used_in, has_step, executed_at, resulted_in, has_params
```

### Section 6: GNN Model Definition

**Cell Names:** `gnn_model_header`, `message_passing_explainer`, `define_hetero_gnn_model_cell`, `model_summary_display`

Model architecture:
```python
class HeteroGNN(torch.nn.Module):
    """
    Heterogeneous Graph Neural Network for manufacturing process graph.
    
    Architecture:
        Input features → HeteroConv (layer 1) → ReLU → HeteroConv (layer 2) → Output embeddings
    
    Parameters:
        hidden_dim: Dimension of hidden layers (default: 64)
        out_dim: Dimension of output embeddings (default: 32)
    """
```

### Section 7: Model Training

**Cell Names:** `training_header`, `prepare_training_data_cell`, `train_model_cell`, `training_curves_viz`

Training configuration:
- Epochs: 100
- Learning rate: 0.01
- Optimizer: Adam
- Task: Link prediction (predict defect associations)

Training diagnostics:
- Loss curve plot
- Epoch-by-epoch metrics

### Section 8: Defect Tracing

**Cell Names:** `defect_tracing_header`, `trace_algorithm_explainer`, `compute_risk_scores_cell`, `trace_defects_cell`

Tracing algorithm:
1. For each defect node, traverse backward through graph
2. Aggregate embeddings of connected suppliers, materials, stations
3. Compute similarity scores between defect embeddings and entity embeddings
4. Rank entities by correlation with defect patterns

### Section 9: Pattern Discovery

**Cell Names:** `pattern_discovery_header`, `discover_patterns_cell`, `pattern_visualization`, `ai_explanation_cell`

Pattern discovery:
- Cluster defect embeddings
- Identify common upstream entities
- Surface supplier batch and station correlations

Expected discoveries:
- Vulcan Steel batch 2847 correlation
- Heat Treatment Line 3 + HD-Series correlation

### Section 10: Write Results

**Cell Names:** `write_results_header`, `write_root_cause_analysis_cell`, `write_risk_scores_cell`, `grant_permissions_cell`

Tables created:
```sql
CREATE OR REPLACE TABLE ROOT_CAUSE_ANALYSIS (
    ANALYSIS_ID VARCHAR(20),
    PATTERN_TYPE VARCHAR(50),  -- 'supplier_issue', 'process_config'
    ENTITY_TYPE VARCHAR(50),   -- 'supplier', 'station', 'material_batch'
    ENTITY_ID VARCHAR(50),
    ENTITY_NAME VARCHAR(100),
    CORRELATION_SCORE FLOAT,
    DEFECT_COUNT INTEGER,
    AFFECTED_WORK_ORDERS INTEGER,
    DESCRIPTION VARCHAR(500),
    RECOMMENDATIONS VARIANT,
    CREATED_AT TIMESTAMP_NTZ
);

CREATE OR REPLACE TABLE COMPONENT_RISK_SCORES (
    COMPONENT_ID VARCHAR(50),
    COMPONENT_TYPE VARCHAR(50),
    COMPONENT_NAME VARCHAR(100),
    RISK_SCORE FLOAT,
    RISK_FACTORS VARIANT,
    RELATED_DEFECTS INTEGER,
    LAST_UPDATED TIMESTAMP_NTZ
);
```

### Section 11: Key Takeaways

**Cell Names:** `key_takeaways_header`, `summary_and_interpretation`

Content:
- What the model learned
- Interpretation guidelines for risk scores
- Limitations (data dependency, graph construction assumptions)
- Mathematical recap
- Next steps (integration with quality systems)

---

## 5. Streamlit Application Specification

### Common Utilities

#### `streamlit/utils/data_loader.py`

```python
"""
Parallel query execution for fast dashboard loading.

Uses ThreadPoolExecutor to run independent Snowflake queries concurrently,
reducing page load times from ~8s to ~1.5s (80% improvement).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Any
import streamlit as st

def run_queries_parallel(session, queries: Dict[str, str], max_workers: int = 4) -> Dict[str, Any]:
    """
    Execute multiple independent queries in parallel.
    
    Args:
        session: Snowpark session
        queries: Dict mapping result names to SQL queries
        max_workers: Maximum concurrent queries
    
    Returns:
        Dict mapping result names to DataFrames
    """
    results = {}
    
    def execute_query(name: str, sql: str):
        return name, session.sql(sql).to_pandas()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(execute_query, name, sql): name 
            for name, sql in queries.items()
        }
        for future in as_completed(futures):
            name, df = future.result()
            results[name] = df
    
    return results
```

#### `streamlit/utils/visualizations.py`

```python
"""
Plotly visualization utilities with Snowflake dark theme.

All visualizations use consistent styling aligned with Snowflake brand colors
and dark mode best practices for reduced eye strain.
"""

import plotly.graph_objects as go
import plotly.io as pio
import networkx as nx

# Snowflake Color Palette
SNOWFLAKE_BLUE = '#29B5E8'
MID_BLUE = '#11567F'
ACCENT_ORANGE = '#FF9F0A'
ACCENT_PURPLE = '#8B5CF6'
DARK_BG = '#0f172a'
CARD_BG = '#1e293b'
TEXT_PRIMARY = '#e2e8f0'
TEXT_SECONDARY = '#94a3b8'

# Set default template
SNOWFLAKE_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=TEXT_PRIMARY, family='Helvetica Neue, Arial, sans-serif'),
        title=dict(font=dict(size=16, color=TEXT_PRIMARY)),
        xaxis=dict(gridcolor='#334155', linecolor='#475569', tickfont=dict(color=TEXT_SECONDARY)),
        yaxis=dict(gridcolor='#334155', linecolor='#475569', tickfont=dict(color=TEXT_SECONDARY)),
        colorway=[SNOWFLAKE_BLUE, ACCENT_ORANGE, ACCENT_PURPLE, MID_BLUE],
        hoverlabel=dict(bgcolor=CARD_BG, bordercolor='#334155', font=dict(color=TEXT_PRIMARY))
    )
)
pio.templates.default = SNOWFLAKE_TEMPLATE

def create_network_graph(nodes_df, edges_df, highlight_defects=True):
    """Create interactive network visualization using NetworkX layout."""
    pass

def create_sankey_diagram(trace_data, title="Defect Trace"):
    """Create Sankey diagram for defect flow visualization."""
    pass

def create_risk_bar_chart(risk_df, category_col, value_col, title):
    """Create horizontal bar chart for risk scores."""
    pass
```

#### `streamlit/utils/ai_insights.py`

```python
"""
Cortex AI integration for natural language insights.

Uses Cortex Complete to generate explanations of root causes and risk summaries.
Includes graceful fallback when Cortex is unavailable.
"""

import streamlit as st

def get_root_cause_explanation(session, pattern_data: dict) -> str:
    """
    Generate natural language explanation of a root cause pattern.
    
    Uses Cortex Complete with specific prompt engineering to produce
    concise, actionable explanations without preamble.
    """
    prompt = f"""
    Analyze this manufacturing root cause pattern and provide a concise explanation:
    
    Pattern Type: {pattern_data['type']}
    Entity: {pattern_data['entity_name']}
    Correlation Score: {pattern_data['score']:.2f}
    Affected Defects: {pattern_data['defect_count']}
    Defect Types: {pattern_data['defect_types']}
    
    Explain the likely root cause and recommend immediate actions.
    No preamble, headers, or follow-up questions.
    """
    
    try:
        result = session.sql(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'mistral-large',
                '{prompt.replace("'", "''")}'
            ) as response
        """).collect()[0]['RESPONSE']
        return result
    except Exception as e:
        return _fallback_explanation(pattern_data)

def _fallback_explanation(pattern_data: dict) -> str:
    """Provide rule-based fallback when Cortex is unavailable."""
    if pattern_data['type'] == 'supplier_issue':
        return f"High correlation ({pattern_data['score']:.0%}) between {pattern_data['entity_name']} materials and defects. Recommend immediate supplier audit and batch quarantine."
    elif pattern_data['type'] == 'process_config':
        return f"Process configuration issue detected at {pattern_data['entity_name']}. {pattern_data['defect_count']} defects linked to parameter deviations. Recommend immediate parameter verification."
    return "Pattern requires further investigation."
```

#### `streamlit/utils/database.py`

```python
"""
Database operations with caching for Streamlit performance.
"""

import streamlit as st

@st.cache_data(ttl=300)
def get_defects_summary(_session):
    """Get cached summary of defects."""
    return _session.sql("""
        SELECT 
            DEFECT_TYPE,
            SEVERITY,
            COUNT(*) as DEFECT_COUNT,
            COUNT(DISTINCT WORK_ORDER_ID) as AFFECTED_WORK_ORDERS
        FROM DEFECTS
        GROUP BY DEFECT_TYPE, SEVERITY
        ORDER BY DEFECT_COUNT DESC
    """).to_pandas()

@st.cache_data(ttl=300)
def get_root_cause_analysis(_session):
    """Get cached root cause analysis results."""
    return _session.sql("""
        SELECT * FROM ROOT_CAUSE_ANALYSIS
        ORDER BY CORRELATION_SCORE DESC
    """).to_pandas()
```

### Page 1: Process Network (`pages/1_Process_Network.py`)

**Purpose:** Interactive visualization of the manufacturing process graph showing material flow, process steps, and defect paths.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Process Network                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────┐ │
│  │ Product Family      │  │ Date Range          │  │ Show Defects    │ │
│  │ [Dropdown]          │  │ [Date Picker]       │  │ [Toggle]        │ │
│  └─────────────────────┘  └─────────────────────┘  └─────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│                    ┌─────────────────────────────┐                      │
│                    │                             │                      │
│                    │    Network Graph            │                      │
│                    │    (Plotly + NetworkX)      │                      │
│                    │                             │                      │
│                    │   Suppliers → Materials     │                      │
│                    │       ↓                     │                      │
│                    │   Work Orders → Steps       │                      │
│                    │       ↓                     │                      │
│                    │   Defects (red highlight)   │                      │
│                    │                             │                      │
│                    └─────────────────────────────┘                      │
│                                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Graph Statistics                                                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Suppliers│  │ Materials│  │ Work     │  │ Process  │  │ Defects  │  │
│  │    15    │  │  14,200  │  │ Orders   │  │ Steps    │  │   ~160   │  │
│  │          │  │          │  │  6,500   │  │  58,500  │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Data Queries (Parallel):**
- `suppliers`: SELECT * FROM SUPPLIERS
- `materials`: SELECT * FROM MATERIALS
- `work_orders`: SELECT * FROM WORK_ORDERS WHERE product_family = :filter
- `process_steps`: SELECT * FROM PROCESS_STEPS
- `defects`: SELECT * FROM DEFECTS

**Visualization:**
- Use NetworkX for layout computation (spring layout)
- Use Plotly Scatter for rendering nodes and edges
- Node colors by type (supplier=blue, material=cyan, work_order=green, defect=red)
- Edge colors: normal=gray, defect_path=red

### Page 2: Defect Tracing (`pages/2_Defect_Tracing.py`)

**Purpose:** Select a defect and trace its path back through the manufacturing process to identify potential root causes.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Defect Tracing                                                          │
├─────────────────────────────────────────────────────────────────────────┤
│  Select Defect                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ [Dropdown: DEF-0001 - Hydraulic Seal Failure - WO-00234]            ││
│  └─────────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────┤
│  Trace Path                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                                                                      ││
│  │   Vulcan Steel ─┬─▶ Steel Rod ─┬─▶ Machining ─┬─▶ WO-00234 ─┬─▶ DEF ││
│  │   Works         │   Batch 2847 │   Line 2     │   HD-Series │   0001││
│  │                 │              │              │             │       ││
│  │          (Sankey Diagram showing flow from supplier to defect)      ││
│  │                                                                      ││
│  └─────────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────┤
│  AI Analysis                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  This defect traces back to Vulcan Steel Works batch #2847.         ││
│  │  The batch has a 12% defect correlation vs 2% baseline.             ││
│  │  Recommend: Quarantine remaining batch materials, audit supplier.   ││
│  └─────────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────┤
│  Similar Defects                                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │ DEF-0005 │ Hydraulic Seal │ Same batch │ WO-00567 │ 2024-01-15   │  │
│  │ DEF-0012 │ Cylinder Score │ Same batch │ WO-00891 │ 2024-01-18   │  │
│  │ DEF-0019 │ Hydraulic Seal │ Same batch │ WO-01023 │ 2024-01-22   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

**Data Queries:**
- `defects_list`: SELECT DEFECT_ID, DEFECT_TYPE, WORK_ORDER_ID FROM DEFECTS
- `trace_data`: Complex query joining DEFECTS → WORK_ORDERS → PROCESS_STEPS → MATERIALS → SUPPLIERS
- `similar_defects`: Query for defects with same upstream entities

**Visualizations:**
- Sankey diagram (Plotly go.Sankey) showing flow from supplier to defect
- Similar defects table with expandable details

**AI Integration:**
- Call `get_root_cause_explanation()` with trace data
- Display in styled card with blue border-left accent

### Page 3: Risk Analysis (`pages/3_Risk_Analysis.py`)

**Purpose:** Display risk scores across suppliers, stations, and product families with prominent highlighting of the two discovered patterns.

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  Risk Analysis                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Discovered Patterns                                                     │
│  ┌────────────────────────────────┐  ┌────────────────────────────────┐ │
│  │  SUPPLIER ISSUE                │  │  PROCESS CONFIGURATION         │ │
│  │                                │  │                                │ │
│  │  Vulcan Steel Works            │  │  Heat Treatment Line 3         │ │
│  │  Batch #2847                   │  │  + HD-Series Products          │ │
│  │                                │  │                                │ │
│  │  Correlation: 0.87             │  │  Correlation: 0.92             │ │
│  │  Affected: 23 defects          │  │  Affected: 18 defects          │ │
│  │  Products: Excavator, Loader   │  │  Expected: 870°C/60min         │ │
│  │                                │  │  Actual: 820°C/45min           │ │
│  │  [View Details]                │  │  [View Details]                │ │
│  └────────────────────────────────┘  └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│  Risk by Category                                  AI Risk Summary       │
│  ┌────────────────────────────────────────┐  ┌────────────────────────┐ │
│  │ [Tabs: Suppliers | Stations | Products]│  │ Top risks identified:  │ │
│  │                                         │  │                        │ │
│  │ Vulcan Steel    ████████████████ 0.87  │  │ 1. Vulcan batch 2847   │ │
│  │ Precision Hyd.  ████████ 0.42          │  │    requires immediate  │ │
│  │ Global Elect.   ███████ 0.38           │  │    quarantine.         │ │
│  │ Allied Fasten.  ████ 0.21              │  │                        │ │
│  │ ...                                     │  │ 2. Heat Treat Line 3   │ │
│  │                                         │  │    needs recalibration │ │
│  │                                         │  │    for HD-Series.      │ │
│  └────────────────────────────────────────┘  └────────────────────────┘ │
├─────────────────────────────────────────────────────────────────────────┤
│  Recommendations                                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │ Priority │ Action                                    │ Impact       ││
│  │──────────│───────────────────────────────────────────│──────────────││
│  │ CRITICAL │ Quarantine Vulcan batch 2847 materials    │ -23 defects  ││
│  │ CRITICAL │ Recalibrate Heat Treatment Line 3         │ -18 defects  ││
│  │ HIGH     │ Audit Precision Hydraulics QC process     │ -8 defects   ││
│  └─────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────┘
```

**Data Queries:**
- `root_causes`: SELECT * FROM ROOT_CAUSE_ANALYSIS ORDER BY CORRELATION_SCORE DESC
- `risk_scores`: SELECT * FROM COMPONENT_RISK_SCORES
- `supplier_risks`: Aggregated risk by supplier
- `station_risks`: Aggregated risk by station
- `product_risks`: Aggregated risk by product family

**Visualizations:**
- Pattern highlight cards (styled with red/orange borders for critical)
- Horizontal bar charts for risk by category (Plotly)
- Recommendations table

**AI Integration:**
- Summary of top risks using Cortex Complete
- Styled inline card (not expander)

### Page 4: About (`pages/4_About.py`)

**Purpose:** Solution overview for dual audience (business stakeholders and technical users).

**Layout:**
```
┌─────────────────────────────────────────────────────────────────────────┐
│  About                                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│  Solution Overview                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │  GNN Process Traceability uses Graph Neural Networks to trace       ││
│  │  quality defects back through the manufacturing process, identifying││
│  │  root causes that span multiple suppliers, materials, and stations. ││
│  │                                                                      ││
│  │  Unlike traditional analysis that examines defects in isolation,    ││
│  │  GNN captures network effects where root causes are paths through   ││
│  │  the manufacturing graph, not single attributes.                    ││
│  └─────────────────────────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────┤
│  Data Architecture                                                       │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                                                                    │  │
│  │  [Bronze Layer]    [Silver Layer]    [Gold Layer]                 │  │
│  │   - Suppliers       - GNN Model       - Root Cause Analysis       │  │
│  │   - Materials       - Graph           - Risk Scores               │  │
│  │   - Work Orders     - Embeddings                                  │  │
│  │   - Process Steps                                                 │  │
│  │   - Defects                                                       │  │
│  │                                                                    │  │
│  └───────────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────────┤
│  Application Pages                                                       │
│  ┌──────────────────┬──────────────────────────────────────────────────┐│
│  │ Process Network  │ Interactive visualization of manufacturing graph ││
│  │ Defect Tracing   │ Trace defects to root causes with AI insights    ││
│  │ Risk Analysis    │ Risk scores and discovered patterns              ││
│  └──────────────────┴──────────────────────────────────────────────────┘│
├─────────────────────────────────────────────────────────────────────────┤
│  Technology Stack                                                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Snowflake│ │ Snowpark │ │ PyTorch  │ │ Cortex   │ │ Plotly   │      │
│  │ Notebooks│ │          │ │ Geometric│ │ Complete │ │          │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
├─────────────────────────────────────────────────────────────────────────┤
│  Getting Started                                                         │
│  1. Run the notebook to generate risk scores                             │
│  2. Explore the Process Network to understand material flow              │
│  3. Use Defect Tracing to investigate specific quality issues            │
│  4. Review Risk Analysis for prioritized remediation actions             │
└─────────────────────────────────────────────────────────────────────────┘
```

**Data Sources Section:**
| Source | Type | Badge Color |
|--------|------|-------------|
| MES/ERP (Synthetic) | Internal | Blue (#1e40af) |
| Supplier QMS | External | Amber (#b45309) |
| GNN Model Output | Model | Green (#166534) |

---

## 6. Shell Scripts Specification

### deploy.sh

**Purpose:** One-time deployment of all infrastructure and applications.

**Supported Flags:**
- `-c, --connection NAME`: Snowflake CLI connection name (default: demo)
- `-p, --prefix PREFIX`: Environment prefix (DEV, PROD)
- `--only-sql`: Run SQL setup only
- `--only-data`: Upload and load data only
- `--only-notebook`: Deploy notebook only
- `--only-streamlit`: Deploy Streamlit app only
- `--skip-notebook`: Skip notebook deployment
- `-h, --help`: Show help

**Steps:**
1. Check prerequisites (snow CLI, required files)
2. Run account-level SQL (01_account_setup.sql)
3. Run schema-level SQL (02_schema_setup.sql)
4. Upload data to stage (PUT commands)
5. Load data into tables (COPY INTO)
6. Deploy notebook
7. Deploy Streamlit app
8. Display completion summary

### run.sh

**Purpose:** Runtime operations after deployment.

**Commands:**
- `main`: Execute the GNN notebook
- `status`: Check resource status and table row counts
- `notebook`: Get notebook URL
- `streamlit`: Get Streamlit app URL

**Steps for `main`:**
1. Stop existing services on compute pool
2. Execute notebook headlessly
3. Display completion status

### clean.sh

**Purpose:** Remove all project resources.

**Supported Flags:**
- `-c, --connection NAME`: Snowflake CLI connection
- `-p, --prefix PREFIX`: Environment prefix
- `--yes, -y, --force`: Skip confirmation prompt

**Deletion Order:**
1. Compute Pool (stop first, then drop)
2. Warehouse
3. Database (cascades to all contained objects)
4. Role

### ci_test_cycle.sh

**Purpose:** Automated test cycle for CI/CD.

**Steps:**
1. Run deploy.sh
2. Run run.sh main
3. Verify table row counts
4. Run run.sh streamlit (verify URL retrievable)
5. Run clean.sh --yes
6. Exit with success/failure code

---

## 7. File Specifications

### data/synthetic/ (Pre-generated CSVs)

| File | Records | Description |
|------|---------|-------------|
| suppliers.csv | 15 | Supplier master data |
| materials.csv | ~14,200 | Material inventory with batch info |
| work_orders.csv | 6,500 | Production orders (62 months: Jan 2020 - Feb 2025) |
| process_steps.csv | ~58,500 | Manufacturing steps (9 steps per work order) |
| process_parameters.csv | ~58,500 | Machine parameters |
| defects.csv | ~150-180 | Quality defects with hidden patterns |
| stations.csv | 15 | Manufacturing stations (3 production lines) |

### notebooks/environment.yml

```yaml
name: gnn_traceability_env
channels:
  - snowflake
dependencies:
  - pandas
  - numpy
  - scipy
  - matplotlib
  - seaborn
  - networkx
```

### streamlit/environment.yml

```yaml
name: streamlit_env
channels:
  - snowflake
dependencies:
  - pandas
  - numpy
  - plotly
  - networkx
```

### streamlit/snowflake.yml

```yaml
definition_version: "2"
entities:
  gnn_traceability_app:
    type: streamlit
    identifier:
      name: GNN_PROCESS_TRACEABILITY_APP
    main_file: streamlit_app.py
    pages_dir: pages/
    query_warehouse: GNN_PROCESS_TRACEABILITY_WH
    artifacts:
      - streamlit_app.py
      - pages/
      - utils/
```

---

## 8. Naming Convention

| Object | Name |
|--------|------|
| Database | GNN_PROCESS_TRACEABILITY |
| Schema | GNN_PROCESS_TRACEABILITY |
| Role | GNN_PROCESS_TRACEABILITY_ROLE |
| Warehouse | GNN_PROCESS_TRACEABILITY_WH |
| Compute Pool | GNN_PROCESS_TRACEABILITY_COMPUTE_POOL |
| Notebook | GNN_PROCESS_TRACEABILITY_NOTEBOOK |
| Streamlit App | GNN_PROCESS_TRACEABILITY_APP |
| Data Stage | DATA_STAGE |
| Models Stage | MODELS_STAGE |

---

## 9. Success Criteria

### Functional Requirements
- [ ] Deploy in under 5 minutes with `./deploy.sh`
- [ ] Notebook executes successfully and populates Gold layer tables
- [ ] Streamlit dashboard shows network visualization and defect tracing
- [ ] Both hidden patterns discoverable through the UI:
  - [ ] Vulcan Steel batch 2847 identified as supplier risk
  - [ ] Heat Treatment Line 3 + HD-Series identified as process configuration issue
- [ ] AI insights provide natural language explanation of root causes

### Quality Requirements
- [ ] DDL compliant (no CHECK constraints, documented in comments)
- [ ] Notebook cells named (all cells have meaningful metadata names)
- [ ] Parallel queries (dashboard uses ThreadPoolExecutor for fast loading)
- [ ] Production ready (error handling, caching, graceful AI fallbacks)
- [ ] Color scheme (Snowflake Blue #29B5E8 as primary accent)
- [ ] Pre-publication ready (passes SNOWFLAKE_DEMO_PREPUBLICATION_CHECKLIST)

### CI/CD
- [ ] Full test cycle passes (`./ci_test_cycle.sh` completes without errors)
- [ ] Clean teardown with `./clean.sh --yes`

---

## 10. Appendix: Color Palette

### Primary Colors
| Name | Hex | Usage |
|------|-----|-------|
| Snowflake Blue | #29B5E8 | Primary accent (80% of accent usage) |
| Mid Blue | #11567F | Secondary accent |

### Dark Theme
| Name | Hex | Usage |
|------|-----|-------|
| Background | #0f172a | Page background |
| Card Background | #1e293b | Cards, panels |
| Text Primary | #e2e8f0 | Main text |
| Text Secondary | #94a3b8 | Labels, captions |
| Border | #334155 | Card borders, dividers |

### Semantic Colors
| Name | Hex | Usage |
|------|-----|-------|
| Critical/High Risk | #ef4444 | Critical issues |
| Warning | #f59e0b | Warnings, medium risk |
| Success | #22c55e | Success states |
| Info | #3b82f6 | Informational |

### Visualization Palette
```python
CHART_COLORS = ['#29B5E8', '#FF9F0A', '#8B5CF6', '#11567F', '#22c55e']
```

