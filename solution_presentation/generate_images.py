#!/usr/bin/env python3
"""
Generate presentation images for GNN Process Traceability solution.

Creates visualization images for the solution presentation:
- problem-impact.png: Real-world quality incident statistics
- before-after.png: Reactive vs proactive comparison
- roi-value.png: Business value metrics
- data-erd.png: Data model diagram
- architecture.png: System architecture

Usage:
    python generate_images.py
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrow
import numpy as np
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

# Snowflake color palette
COLORS = {
    'primary': '#29B5E8',
    'secondary': '#11567F',
    'accent': '#FF9F0A',
    'purple': '#8B5CF6',
    'background': '#0f172a',
    'card': '#1e293b',
    'text': '#e2e8f0',
    'text_secondary': '#94a3b8',
    'border': '#334155',
    'critical': '#ef4444',
    'warning': '#f59e0b',
    'success': '#22c55e',
}

# Common figure setup
def setup_dark_figure(figsize=(12, 6)):
    fig, ax = plt.subplots(figsize=figsize, facecolor=COLORS['background'])
    ax.set_facecolor(COLORS['background'])
    return fig, ax


def generate_problem_impact():
    """Generate problem impact visualization."""
    fig, ax = setup_dark_figure((10, 6))
    
    categories = ['Warranty\nClaims', 'Recall\nCosts', 'Investigation\nTime', 'Production\nDowntime']
    values = [1.2, 0.5, 3, 40]  # $1.2M, $500K, 3 weeks, 40 hours
    colors = [COLORS['critical'], COLORS['warning'], COLORS['accent'], COLORS['purple']]
    
    bars = ax.bar(categories, values, color=colors, edgecolor=COLORS['border'], linewidth=1)
    
    # Add value labels
    for bar, val, cat in zip(bars, values, categories):
        if 'Warranty' in cat:
            label = f'${val}M/year'
        elif 'Recall' in cat:
            label = f'${val}M/incident'
        elif 'Investigation' in cat:
            label = f'{int(val)} weeks'
        else:
            label = f'{int(val)} hours'
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                label, ha='center', va='bottom', color=COLORS['text'], fontsize=12, fontweight='bold')
    
    ax.set_title('The Cost of Quality Failures', color=COLORS['text'], fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Relative Impact', color=COLORS['text'])
    ax.tick_params(colors=COLORS['text_secondary'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, max(values) * 1.3)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'problem-impact.png', dpi=150, facecolor=COLORS['background'])
    plt.close()
    print(f"[OK] Generated problem-impact.png")


def generate_before_after():
    """Generate before/after comparison."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), facecolor=COLORS['background'])
    
    for ax in [ax1, ax2]:
        ax.set_facecolor(COLORS['background'])
    
    # Before (Traditional)
    metrics_before = ['Investigation Time', 'Pattern Discovery', 'Defect Correlation', 'Action Priority']
    values_before = [4, 2, 3, 2]  # weeks, manual, single-var, reactive
    
    bars1 = ax1.barh(metrics_before, values_before, color=COLORS['critical'], edgecolor=COLORS['border'])
    ax1.set_title('Before: Traditional Analysis', color=COLORS['text'], fontsize=14, fontweight='bold')
    ax1.set_xlabel('Weeks / Effectiveness', color=COLORS['text'])
    
    labels_before = ['4 weeks', 'Manual', 'Single-variable', 'Reactive']
    for bar, label in zip(bars1, labels_before):
        ax1.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                label, va='center', color=COLORS['text'], fontsize=10)
    
    # After (GNN)
    values_after = [0.5, 5, 5, 5]  # minutes=0.5 days, automatic, multi-hop, proactive
    
    bars2 = ax2.barh(metrics_before, values_after, color=COLORS['success'], edgecolor=COLORS['border'])
    ax2.set_title('After: GNN Traceability', color=COLORS['text'], fontsize=14, fontweight='bold')
    ax2.set_xlabel('Weeks / Effectiveness', color=COLORS['text'])
    
    labels_after = ['Minutes', 'Automatic', 'Multi-hop', 'Proactive']
    for bar, label in zip(bars2, labels_after):
        ax2.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                label, va='center', color=COLORS['text'], fontsize=10)
    
    for ax in [ax1, ax2]:
        ax.tick_params(colors=COLORS['text_secondary'])
        ax.spines['bottom'].set_color(COLORS['border'])
        ax.spines['left'].set_color(COLORS['border'])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xlim(0, 6)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'before-after.png', dpi=150, facecolor=COLORS['background'])
    plt.close()
    print(f"[OK] Generated before-after.png")


def generate_roi_value():
    """Generate ROI/value metrics."""
    fig, ax = setup_dark_figure((10, 6))
    
    metrics = ['Root Cause\nTime', 'Repeat\nDefects', 'Warranty\nCosts', 'Engineer\nProductivity']
    improvements = [-80, -40, -25, 50]
    
    colors = [COLORS['success'] if v > 0 else COLORS['primary'] for v in improvements]
    
    bars = ax.bar(metrics, [abs(v) for v in improvements], color=colors, edgecolor=COLORS['border'])
    
    for bar, val in zip(bars, improvements):
        sign = '+' if val > 0 else ''
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{sign}{val}%', ha='center', va='bottom', color=COLORS['text'], 
                fontsize=14, fontweight='bold')
    
    ax.set_title('Expected ROI Improvements', color=COLORS['text'], fontsize=16, fontweight='bold', pad=20)
    ax.set_ylabel('Improvement %', color=COLORS['text'])
    ax.tick_params(colors=COLORS['text_secondary'])
    ax.spines['bottom'].set_color(COLORS['border'])
    ax.spines['left'].set_color(COLORS['border'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'roi-value.png', dpi=150, facecolor=COLORS['background'])
    plt.close()
    print(f"[OK] Generated roi-value.png")


def generate_data_erd():
    """Generate simplified data model diagram."""
    fig, ax = setup_dark_figure((14, 8))
    
    # Entity positions - adjusted for better spacing and readability
    entities = {
        'Supplier': (1.5, 5),
        'Material': (4.0, 5),
        'Process Step': (6.5, 5),
        'Station': (6.5, 2.5),
        'Work Order': (9.0, 5),
        'Defect': (11.5, 5),
    }
    
    # Draw entities
    for name, (x, y) in entities.items():
        # Larger boxes for better readability
        width = 2.0
        height = 0.8
        box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                             boxstyle="round,pad=0.05,rounding_size=0.1",
                             facecolor=COLORS['card'], edgecolor=COLORS['primary'],
                             linewidth=2)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', color=COLORS['text'],
               fontsize=12, fontweight='bold')
    
    # Draw relationships
    relationships = [
        ('Supplier', 'Material', 'supplies'),
        ('Material', 'Process Step', 'used_in'),
        ('Process Step', 'Station', 'executed_at'),
        ('Process Step', 'Work Order', 'part_of'),
        ('Work Order', 'Defect', 'resulted_in'),
    ]
    
    for start, end, label in relationships:
        x1, y1 = entities[start]
        x2, y2 = entities[end]
        
        # Determine if vertical or horizontal relationship
        is_vertical = abs(x1 - x2) < 0.1
        
        # Calculate arrow start/end points to touch box edges
        # Box dimensions: width=2.0 (half=1.0), height=0.8 (half=0.4)
        if is_vertical:
            start_x, start_y = x1, y1 - 0.4
            end_x, end_y = x2, y2 + 0.4
            
            # Draw arrow
            ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                       arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=2))
            
            # Place label to the side for vertical lines
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            ax.text(mid_x + 0.15, mid_y, label, ha='left', va='center',
                   color=COLORS['text_secondary'], fontsize=10, style='italic')
            
        else:
            start_x, start_y = x1 + 1.0, y1
            end_x, end_y = x2 - 1.0, y2
            
            # Draw arrow
            ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                       arrowprops=dict(arrowstyle='->', color=COLORS['accent'], lw=2))
            
            # Place label above for horizontal lines
            mid_x = (start_x + end_x) / 2
            mid_y = (start_y + end_y) / 2
            ax.text(mid_x, mid_y + 0.2, label, ha='center', va='bottom',
                   color=COLORS['text_secondary'], fontsize=10, style='italic')
    
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 7)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('Manufacturing Process Graph Model', color=COLORS['text'], 
                fontsize=20, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'data-erd.png', dpi=150, facecolor=COLORS['background'])
    plt.close()
    print(f"[OK] Generated data-erd.png")


def generate_architecture():
    """Generate architecture diagram."""
    fig, ax = setup_dark_figure((14, 8))
    
    # Layers
    layers = [
        ('Bronze Layer', 1, ['Suppliers', 'Materials', 'Work Orders', 'Stations', 'Defects']),
        ('Silver Layer', 3, ['Graph Builder', 'GNN Processor', 'Pattern Discovery']),
        ('Gold Layer', 5, ['Root Causes', 'Risk Scores', 'Recommendations']),
        ('Presentation', 7, ['Streamlit Dashboard', 'Cortex AI Insights']),
    ]
    
    layer_colors = {
        'Bronze Layer': COLORS['secondary'],
        'Silver Layer': COLORS['accent'],
        'Gold Layer': COLORS['success'],
        'Presentation': COLORS['primary'],
    }
    
    for layer_name, y, components in layers:
        # Layer box
        box = FancyBboxPatch((0.5, y-0.8), 13, 1.6,
                             boxstyle="round,pad=0.1,rounding_size=0.2",
                             facecolor=COLORS['card'], edgecolor=layer_colors[layer_name],
                             linewidth=2, alpha=0.8)
        ax.add_patch(box)
        
        # Layer label
        ax.text(0.8, y, layer_name, ha='left', va='center', color=layer_colors[layer_name],
               fontsize=11, fontweight='bold')
        
        # Components
        x_start = 4
        x_step = 10 / len(components)
        for i, comp in enumerate(components):
            x = x_start + i * x_step
            comp_box = FancyBboxPatch((x-0.6, y-0.3), 1.8, 0.6,
                                       boxstyle="round,pad=0.02,rounding_size=0.1",
                                       facecolor=COLORS['background'], edgecolor=COLORS['border'],
                                       linewidth=1)
            ax.add_patch(comp_box)
            ax.text(x+0.3, y, comp, ha='center', va='center', color=COLORS['text'],
                   fontsize=9)
    
    # Arrows between layers
    for i in range(len(layers) - 1):
        y1 = layers[i][1]
        y2 = layers[i+1][1]
        ax.annotate('', xy=(7, y2-0.8), xytext=(7, y1+0.8),
                   arrowprops=dict(arrowstyle='->', color=COLORS['text_secondary'], lw=2))
    
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis('off')
    ax.set_title('GNN Process Traceability Architecture', color=COLORS['text'], 
                fontsize=16, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'architecture.png', dpi=150, facecolor=COLORS['background'])
    plt.close()
    print(f"[OK] Generated architecture.png")


def generate_cascade_analysis():
    """Generate cascade/network analysis visualization showing defect tracing."""
    fig, ax = setup_dark_figure((14, 8))
    
    # Node positions for the cascade flow
    nodes = {
        # Supplier level
        'Vulcan Steel': (1, 4),
        # Material level
        'Batch 2847': (3, 5),
        'Batch 2851': (3, 3),
        # Process level
        'Machining L2': (5, 5.5),
        'Heat Treat L3': (5, 4),
        'Assembly L2': (5, 2.5),
        # Work Order level
        'WO-00234\nHD-Series': (7, 5.5),
        'WO-00567\nHD-Series': (7, 4),
        'WO-00891\nStandard': (7, 2.5),
        # Defect level
        'DEF: Seal\nFailure': (9.5, 5.5),
        'DEF: Cylinder\nScoring': (9.5, 4),
        'OK': (9.5, 2.5),
    }
    
    # Node colors by type
    node_colors = {
        'Vulcan Steel': COLORS['secondary'],
        'Batch 2847': COLORS['critical'],  # Problem batch
        'Batch 2851': COLORS['primary'],
        'Machining L2': COLORS['accent'],
        'Heat Treat L3': COLORS['accent'],
        'Assembly L2': COLORS['accent'],
        'WO-00234\nHD-Series': COLORS['purple'],
        'WO-00567\nHD-Series': COLORS['purple'],
        'WO-00891\nStandard': COLORS['purple'],
        'DEF: Seal\nFailure': COLORS['critical'],
        'DEF: Cylinder\nScoring': COLORS['critical'],
        'OK': COLORS['success'],
    }
    
    # Draw nodes
    for name, (x, y) in nodes.items():
        color = node_colors.get(name, COLORS['primary'])
        box = FancyBboxPatch((x-0.7, y-0.35), 1.4, 0.7,
                             boxstyle="round,pad=0.05,rounding_size=0.15",
                             facecolor=COLORS['card'], edgecolor=color,
                             linewidth=2.5 if 'Batch 2847' in name or 'DEF' in name else 1.5)
        ax.add_patch(box)
        ax.text(x, y, name, ha='center', va='center', color=COLORS['text'],
               fontsize=8, fontweight='bold' if 'Batch 2847' in name else 'normal')
    
    # Edges - defining the cascade paths
    edges = [
        # From supplier to batches
        ('Vulcan Steel', 'Batch 2847', True),
        ('Vulcan Steel', 'Batch 2851', False),
        # From problem batch to processes
        ('Batch 2847', 'Machining L2', True),
        ('Batch 2847', 'Heat Treat L3', True),
        ('Batch 2851', 'Assembly L2', False),
        # From processes to work orders
        ('Machining L2', 'WO-00234\nHD-Series', True),
        ('Heat Treat L3', 'WO-00567\nHD-Series', True),
        ('Assembly L2', 'WO-00891\nStandard', False),
        # From work orders to defects
        ('WO-00234\nHD-Series', 'DEF: Seal\nFailure', True),
        ('WO-00567\nHD-Series', 'DEF: Cylinder\nScoring', True),
        ('WO-00891\nStandard', 'OK', False),
    ]
    
    for start, end, is_defect_path in edges:
        x1, y1 = nodes[start]
        x2, y2 = nodes[end]
        color = COLORS['critical'] if is_defect_path else COLORS['text_secondary']
        linewidth = 2.5 if is_defect_path else 1
        
        ax.annotate('', xy=(x2-0.7, y2), xytext=(x1+0.7, y1),
                   arrowprops=dict(arrowstyle='->', color=color, lw=linewidth,
                                   connectionstyle='arc3,rad=0.1'))
    
    # Add column headers
    headers = [
        (1, 'SUPPLIER'),
        (3, 'MATERIAL'),
        (5, 'PROCESS'),
        (7, 'WORK ORDER'),
        (9.5, 'OUTCOME'),
    ]
    for x, label in headers:
        ax.text(x, 6.5, label, ha='center', va='center', color=COLORS['text_secondary'],
               fontsize=10, fontweight='bold')
    
    # Add pattern annotation
    annotation_box = FancyBboxPatch((0.3, 0.5), 10.4, 1.0,
                                     boxstyle="round,pad=0.1,rounding_size=0.2",
                                     facecolor=COLORS['card'], edgecolor=COLORS['critical'],
                                     linewidth=2, alpha=0.9)
    ax.add_patch(annotation_box)
    ax.text(5.5, 1.0, '[!] PATTERN DETECTED: Vulcan Steel Batch #2847 → 87% correlation with defects\n'
                      '    Root Cause: Elevated sulfur content causing hydraulic seal failures',
           ha='center', va='center', color=COLORS['text'], fontsize=9)
    
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis('off')
    ax.set_title('Defect Cascade Tracing: Batch 2847 Pattern Discovery', 
                color=COLORS['text'], fontsize=14, fontweight='bold', pad=20)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'cascade-analysis.png', dpi=150, facecolor=COLORS['background'])
    plt.close()
    print(f"[OK] Generated cascade-analysis.png")


def generate_dashboard_preview():
    """Generate dashboard UI mockup."""
    fig = plt.figure(figsize=(14, 10), facecolor=COLORS['background'])
    
    # Create grid layout
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.2, 
                          left=0.05, right=0.95, top=0.92, bottom=0.05)
    
    # Header bar
    header_ax = fig.add_axes([0.02, 0.94, 0.96, 0.04])
    header_ax.set_facecolor(COLORS['card'])
    header_ax.text(0.02, 0.5, 'GNN Process Traceability', 
                  transform=header_ax.transAxes, fontsize=14, 
                  color=COLORS['text'], fontweight='bold', va='center')
    header_ax.text(0.98, 0.5, 'Process Network  |  Defect Tracing  |  Risk Analysis  |  About', 
                  transform=header_ax.transAxes, fontsize=10, 
                  color=COLORS['text_secondary'], ha='right', va='center')
    header_ax.axis('off')
    
    # KPI Cards row
    kpis = [
        ('Total Defects', '162', COLORS['critical']),
        ('Patterns Found', '2', COLORS['accent']),
        ('High Risk Components', '5', COLORS['warning']),
        ('Avg Correlation', '89%', COLORS['success']),
    ]
    
    for i, (label, value, color) in enumerate(kpis):
        ax = fig.add_subplot(gs[0, :])
        ax.set_facecolor(COLORS['background'])
        ax.axis('off')
        
        # Draw KPI cards
        card_width = 0.22
        card_x = 0.02 + i * 0.25
        card = FancyBboxPatch((card_x, 0.1), card_width, 0.8,
                              boxstyle="round,pad=0.02,rounding_size=0.05",
                              facecolor=COLORS['card'], edgecolor=color,
                              linewidth=2, transform=ax.transAxes)
        ax.add_patch(card)
        ax.text(card_x + card_width/2, 0.7, value, transform=ax.transAxes,
               fontsize=20, fontweight='bold', color=color, ha='center', va='center')
        ax.text(card_x + card_width/2, 0.3, label, transform=ax.transAxes,
               fontsize=10, color=COLORS['text_secondary'], ha='center', va='center')
    
    # Left panel - Network preview
    ax_network = fig.add_subplot(gs[1, :2])
    ax_network.set_facecolor(COLORS['card'])
    ax_network.set_title('Manufacturing Process Network', color=COLORS['text'], 
                        fontsize=12, fontweight='bold', loc='left', pad=10)
    
    # Draw simplified network nodes
    np.random.seed(42)
    n_nodes = 25
    x = np.random.rand(n_nodes) * 0.8 + 0.1
    y = np.random.rand(n_nodes) * 0.8 + 0.1
    node_types = np.random.choice(['supplier', 'material', 'station', 'defect'], n_nodes, 
                                   p=[0.1, 0.3, 0.3, 0.3])
    type_colors = {
        'supplier': COLORS['secondary'],
        'material': COLORS['primary'],
        'station': COLORS['accent'],
        'defect': COLORS['critical'],
    }
    colors = [type_colors[t] for t in node_types]
    
    ax_network.scatter(x, y, c=colors, s=80, alpha=0.8, edgecolors=COLORS['border'])
    
    # Draw some edges
    for _ in range(30):
        i, j = np.random.choice(n_nodes, 2, replace=False)
        ax_network.plot([x[i], x[j]], [y[i], y[j]], color=COLORS['border'], 
                       alpha=0.3, linewidth=0.5)
    
    ax_network.axis('off')
    
    # Right panel - Risk scores
    ax_risk = fig.add_subplot(gs[1, 2])
    ax_risk.set_facecolor(COLORS['card'])
    ax_risk.set_title('Top Risk Components', color=COLORS['text'], 
                     fontsize=12, fontweight='bold', loc='left', pad=10)
    
    risks = [
        ('Vulcan Steel B2847', 0.87),
        ('Heat Treat L3', 0.85),
        ('Precision Hyd.', 0.42),
        ('Machining L2', 0.38),
    ]
    
    y_pos = np.arange(len(risks))
    values = [r[1] for r in risks]
    bar_colors = [COLORS['critical'] if v > 0.7 else COLORS['warning'] if v > 0.4 else COLORS['primary'] 
                  for v in values]
    
    ax_risk.barh(y_pos, values, color=bar_colors, edgecolor=COLORS['border'], height=0.6)
    ax_risk.set_yticks(y_pos)
    ax_risk.set_yticklabels([r[0] for r in risks], color=COLORS['text'], fontsize=9)
    ax_risk.set_xlim(0, 1)
    ax_risk.tick_params(colors=COLORS['text_secondary'])
    ax_risk.spines['bottom'].set_color(COLORS['border'])
    ax_risk.spines['left'].set_color(COLORS['border'])
    ax_risk.spines['top'].set_visible(False)
    ax_risk.spines['right'].set_visible(False)
    ax_risk.invert_yaxis()
    
    # Bottom panel - AI Insights
    ax_ai = fig.add_subplot(gs[2, :])
    ax_ai.set_facecolor(COLORS['card'])
    
    # AI insight card
    insight_text = '''[AI] Analysis: Pattern detected linking Vulcan Steel Works Batch #2847 to 87% of hydraulic seal failures.
   The elevated sulfur content (0.042% vs spec max 0.035%) correlates with premature seal degradation.
   Recommendation: Quarantine remaining batch materials and conduct immediate supplier audit.'''
    
    ax_ai.text(0.02, 0.5, insight_text, transform=ax_ai.transAxes,
              fontsize=10, color=COLORS['text'], va='center', wrap=True,
              family='monospace')
    ax_ai.set_title('Cortex AI Insights', color=COLORS['primary'], 
                   fontsize=12, fontweight='bold', loc='left', pad=10)
    ax_ai.axis('off')
    
    plt.savefig(OUTPUT_DIR / 'dashboard-preview.png', dpi=150, facecolor=COLORS['background'])
    plt.close()
    print(f"[OK] Generated dashboard-preview.png")


def main():
    """Generate all presentation images."""
    print("Generating presentation images...")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    generate_problem_impact()
    generate_before_after()
    generate_roi_value()
    generate_data_erd()
    generate_architecture()
    generate_cascade_analysis()
    generate_dashboard_preview()
    
    print()
    print(f"[OK] All images generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

