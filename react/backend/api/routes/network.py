import math
import random
from fastapi import APIRouter
from api.database import execute_query

router = APIRouter()

@router.get("/flow")
def get_manufacturing_flow():
    query = """
    SELECT supplier_name, material_type, defect_type, SUM(defect_count) as cnt
    FROM DEFECT_TYPE_SUPPLIER_BATCH
    GROUP BY supplier_name, material_type, defect_type
    ORDER BY cnt DESC
    LIMIT 100
    """
    rows = execute_query(query)
    
    if not rows:
        return {"nodes": [], "links": []}
    
    nodes = set()
    link_counts = {}
    
    for row in rows:
        supplier = f"Supplier: {row['supplier_name']}"
        material = f"Material: {row['material_type']}"
        defect = f"Defect: {row['defect_type']}"
        cnt = row['cnt']
        
        nodes.update([supplier, material, defect])
        
        for src, tgt in [(supplier, material), (material, defect)]:
            key = (src, tgt)
            link_counts[key] = link_counts.get(key, 0) + cnt
    
    links = [{"source": k[0], "target": k[1], "value": v} for k, v in link_counts.items()]
    
    return {
        "nodes": list(nodes),
        "links": links,
    }

@router.get("/graph")
def get_network_graph(sample_size: int = 50):
    query = f"""
    SELECT component_type as entity_type, component_id as entity_id, 
           risk_score, related_defects as defect_count
    FROM COMPONENT_RISK_SCORES
    ORDER BY risk_score DESC
    LIMIT {sample_size}
    """
    entities = execute_query(query)
    
    if not entities:
        return {"nodes": [], "edges": []}
    
    nodes = []
    for i, e in enumerate(entities):
        angle = 2 * math.pi * i / len(entities)
        radius = 1 + (float(e['risk_score']) / 100) * 2
        nodes.append({
            "id": e['entity_id'],
            "label": str(e['entity_id'])[:15],
            "type": e['entity_type'],
            "risk_score": float(e['risk_score']),
            "defect_count": int(e['defect_count']),
            "x": math.cos(angle) * radius,
            "y": math.sin(angle) * radius,
        })
    
    edges = []
    for i, n1 in enumerate(nodes):
        for n2 in nodes[i+1:]:
            if n1['type'] != n2['type'] and random.random() < 0.15:
                edges.append({
                    "source": n1['id'],
                    "target": n2['id'],
                    "weight": min(n1['risk_score'], n2['risk_score']) / 100,
                })
    
    return {"nodes": nodes, "edges": edges}

@router.get("/paths/{defect_type}")
def get_defect_paths(defect_type: str):
    query = """
    SELECT supplier_name as source, material_type as target, SUM(defect_count) as value
    FROM DEFECT_TYPE_SUPPLIER_BATCH
    WHERE defect_type = %(defect_type)s
    GROUP BY supplier_name, material_type
    ORDER BY value DESC
    LIMIT 50
    """
    rows = execute_query(query, {"defect_type": defect_type})
    
    if not rows:
        return {"nodes": [], "links": []}
    
    nodes = set()
    for row in rows:
        nodes.add(f"Supplier: {row['source']}")
        nodes.add(f"Material: {row['target']}")
    
    return {
        "nodes": list(nodes),
        "links": [{"source": f"Supplier: {r['source']}", "target": f"Material: {r['target']}", "value": r['value']} for r in rows],
    }
