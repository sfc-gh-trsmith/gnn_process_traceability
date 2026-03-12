from fastapi import APIRouter
from api.database import execute_query

router = APIRouter()

@router.get("/defects")
def get_defects(limit: int = 100):
    query = f"""
    SELECT defect_id, work_order_id, defect_type, severity, detection_date, detection_stage
    FROM DEFECTS
    LIMIT {limit}
    """
    return execute_query(query)

@router.get("/type-counts")
def get_defect_type_counts():
    query = """
    SELECT defect_type, defect_count
    FROM DEFECT_TYPE_COUNTS
    ORDER BY defect_count DESC
    """
    return execute_query(query)

@router.get("/summary")
def get_defects_summary():
    counts = execute_query("SELECT defect_type, defect_count FROM DEFECT_TYPE_COUNTS ORDER BY defect_count DESC")
    total = sum(c['defect_count'] for c in counts)
    return {
        "total": total,
        "by_type": counts,
    }
