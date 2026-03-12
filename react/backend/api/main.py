import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.database import get_connection_status, get_connection
from api.routes import summary, defects, risk, network, agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="GNN Process Traceability API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(summary.router, prefix="/summary", tags=["summary"])
app.include_router(defects.router, prefix="/defects", tags=["defects"])
app.include_router(risk.router, prefix="/risk", tags=["risk"])
app.include_router(network.router, prefix="/network", tags=["network"])
app.include_router(agent.router, prefix="/api/agent", tags=["agent"])

@app.get("/health")
def health_check():
    conn = get_connection()
    status = get_connection_status()
    
    if not status['connected']:
        return JSONResponse(
            status_code=503,
            content={
                'status': 'disconnected',
                'error': status['error'],
                'message': 'Unable to connect to Snowflake. Please check your credentials.',
            }
        )
    
    return {'status': 'connected'}

@app.get("/")
def root():
    return {"message": "GNN Process Traceability API", "version": "1.0.0"}
