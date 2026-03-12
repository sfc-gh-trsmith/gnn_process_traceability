from fastapi import APIRouter
from api.database import execute_query

router = APIRouter()

@router.get("/metrics")
def get_dashboard_metrics():
    work_orders = execute_query("SELECT COUNT(*) as cnt FROM WORK_ORDERS")
    defects = execute_query("SELECT COUNT(*) as cnt FROM DEFECTS")
    suppliers = execute_query("SELECT COUNT(DISTINCT supplier_id) as cnt FROM SUPPLIERS")
    patterns = execute_query("SELECT COUNT(*) as cnt FROM ROOT_CAUSE_ANALYSIS WHERE correlation_score >= 0.85")
    
    total_wo = work_orders[0]['cnt'] if work_orders else 0
    total_defects = defects[0]['cnt'] if defects else 0
    
    return {
        "workOrders": total_wo,
        "defects": total_defects,
        "suppliers": suppliers[0]['cnt'] if suppliers else 0,
        "patternsFound": patterns[0]['cnt'] if patterns else 0,
        "defectRate": round((total_defects / total_wo * 100) if total_wo > 0 else 0, 2),
    }
