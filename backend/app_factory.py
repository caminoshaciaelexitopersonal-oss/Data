from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import mlflow

def create_app():
    app = FastAPI()

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Instrument for Prometheus
    Instrumentator().instrument(app).expose(app)

    # Initialize MLflow tracking URI
    mlflow.set_tracking_uri("http://mlflow:5000")

    # Import and include routers/endpoints here to avoid circular imports
    # and side effects on import time.
    # For now, as all endpoints are in main, we will refactor main.py to use this.
    # Import and include routers/endpoints here to avoid circular imports
    # and side effects on import time.
    from backend.app.api import core
    from backend.mcp import api as mcp_api
    from backend.mpa.ingestion import api as ingestion_mpa_api
 
    from backend.wpa.auto_analysis import api as wpa_auto_analysis_api
    from backend.wpa.modeling import api as wpa_modeling_api
    from backend.wpa.report_generation import api as wpa_report_generation_api
    from backend.wpa.db_ingestion import api as wpa_db_ingestion_api
    from backend.wpa.intelligent_merge import api as wpa_intelligent_merge_api
 

    # --- New MCP Router ---
    app.include_router(mcp_api.router)

    # --- MPA Routers ---
    app.include_router(ingestion_mpa_api.router)
    from backend.mpa.eda import api as eda_mpa_api
    app.include_router(eda_mpa_api.router)
 
    from backend.mpa.quality import api as quality_mpa_api
    app.include_router(quality_mpa_api.router)
    from backend.mpa.ml import api as ml_mpa_api
    app.include_router(ml_mpa_api.router)
 
 
    # --- WPA Routers ---
    app.include_router(wpa_auto_analysis_api.router)
    app.include_router(wpa_modeling_api.router)
    app.include_router(wpa_report_generation_api.router)
    app.include_router(wpa_db_ingestion_api.router)
    app.include_router(wpa_intelligent_merge_api.router)

 
    # --- Legacy Routers (to be phased out) ---
    app.include_router(core.router, prefix="/api/v1", tags=["Core (Legacy)"])

    return app
