from fastapi import FastAPI
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
        allow_origins=["https://tudominio.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Instrument for Prometheus
    Instrumentator().instrument(app).expose(app)

    # Initialize MLflow tracking URI
    mlflow.set_tracking_uri("http://mlflow:5000")

    # --- Unified Interoperability Router ---
    # This is now the ONLY entry point for all stable, interoperable functionality.
    # All other routers have been removed to eliminate conflicts.
    from backend.app.api import unified_router
    app.include_router(unified_router.router)

    return app
