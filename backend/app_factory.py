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
    from backend.app.api import ingestion, etl, core
    app.include_router(ingestion.router, prefix="/api/v1")
    app.include_router(etl.router, prefix="/api/v1")
    app.include_router(core.router, prefix="/api/v1")

    return app
