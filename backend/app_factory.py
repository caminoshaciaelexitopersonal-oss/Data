import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
import mlflow
from backend.middleware.hardening_middleware import HardeningMiddleware

def create_app():
    app = FastAPI()

    # Add Hardening Middleware first to process requests early
    app.add_middleware(HardeningMiddleware)

    # Configure CORS using environment variables for flexibility
    origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Instrument for Prometheus
    Instrumentator().instrument(app).expose(app)

    # Initialize MLflow tracking URI
    mlflow.set_tracking_uri("http://mlflow:5000")

 
    # --- Routers ---
    # Unified Interoperability Router (MCP, core MPAs)
    from backend.app.api import unified_router
    app.include_router(unified_router.router)

    # Automated Analysis Workflow Router (WPA)
    from backend.wpa.auto_analysis import api as auto_analysis_api
    app.include_router(auto_analysis_api.router)


 
    # Startup event to log all registered routes for easier debugging
    @app.on_event("startup")
    async def startup_event():
        print("--- Registered Routes ---")
        for route in app.routes:
            if hasattr(route, "methods"):
                print(f"Path: {route.path}, Methods: {list(route.methods)}")
        print("-------------------------")


    return app
