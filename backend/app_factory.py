from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import mlflow
from backend.middleware.hardening_middleware import HardeningMiddleware

def create_app():
    app = FastAPI()

    # Add Hardening Middleware first to process requests early
    app.add_middleware(HardeningMiddleware)

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

    # --- Experimental Router Setup ---
    # Create a single router to host all new and non-core legacy endpoints
    # under a unified experimental namespace.
    experimental_router = APIRouter(prefix="/experimental/v1")

    # Import and include routers/endpoints here to avoid circular imports
    # and side effects on import time.
    from backend.app.api import core
    from backend.app.api import ingestion_orchestrator
    from backend.mcp import api as mcp_api
    from backend.mpa.ingestion import api as ingestion_mpa_api
    from backend.mpa.eda import api as eda_mpa_api
    from backend.mpa.quality import api as quality_mpa_api
    from backend.mpa.ml import api as ml_mpa_api
    from backend.wpa.auto_analysis import api as wpa_auto_analysis_api
    from backend.wpa.modeling import api as wpa_modeling_api
    from backend.wpa.report_generation import api as wpa_report_generation_api
    from backend.wpa.db_ingestion import api as wpa_db_ingestion_api
    from backend.wpa.intelligent_merge import api as wpa_intelligent_merge_api
    from backend.routers.prompts_api import router as prompts_router
    from backend.routers.eda_recalculate_api import router as eda_recalculate_router
    from backend.routers.export_api import router as export_router
    from backend.routers.validation_api import router as validation_router
    from backend.routers.pipelines_api import router as pipelines_router

    # --- Add all experimental endpoints to the experimental router ---
    experimental_router.include_router(mcp_api.router)
    experimental_router.include_router(ingestion_mpa_api.router)
    experimental_router.include_router(eda_mpa_api.router)
    experimental_router.include_router(quality_mpa_api.router)
    experimental_router.include_router(ml_mpa_api.router)
    experimental_router.include_router(wpa_auto_analysis_api.router)
    experimental_router.include_router(wpa_modeling_api.router)
    experimental_router.include_router(wpa_report_generation_api.router)
    experimental_router.include_router(wpa_db_ingestion_api.router)
    experimental_router.include_router(wpa_intelligent_merge_api.router)
    experimental_router.include_router(prompts_router)
    experimental_router.include_router(eda_recalculate_router)
    experimental_router.include_router(export_router)
    experimental_router.include_router(validation_router)
    experimental_router.include_router(pipelines_router)

    # --- Main App Router Registration ---
    # Register the single experimental router with the main app.
    app.include_router(experimental_router)

    # --- Unified Interoperability Router ---
    # This is the NEW primary entry point for all stable, interoperable functionality.
    from backend.app.api import unified_router
    app.include_router(unified_router.router)

    # --- Legacy & Stable Routers ---
    app.include_router(core.router, prefix="/api/v1", tags=["Core (Legacy)"])
    app.include_router(ingestion_orchestrator.router, prefix="/api/v1", tags=["Ingestion Orchestrator"])

    return app
