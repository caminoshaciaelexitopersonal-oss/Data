"""
File: unified_routes_def.py
Purpose: Centralizes the definition of the unified API router to avoid
         code duplication between the compatibility and canonical routers.
"""
from fastapi import APIRouter

def get_unified_router() -> APIRouter:
    """
    Builds and returns a single APIRouter containing all endpoints
    from all active architectures (legacy, MPA, WPA, etc.).
    """
    # --- Import all active routers from the application ---
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
    from backend.app.api import core as legacy_core_router
    from backend.app.api import ingestion_orchestrator as legacy_ingestion_router
    from backend.app.api import unified_router

    # --- Create the unified router ---
    unified_router_instance = APIRouter()

    # Include all routers
    unified_router_instance.include_router(mcp_api.router)
    unified_router_instance.include_router(ingestion_mpa_api.router)
    unified_router_instance.include_router(eda_mpa_api.router)
    unified_router_instance.include_router(quality_mpa_api.router)
    unified_router_instance.include_router(ml_mpa_api.router)
    unified_router_instance.include_router(wpa_auto_analysis_api.router)
    unified_router_instance.include_router(wpa_modeling_api.router)
    unified_router_instance.include_router(wpa_report_generation_api.router)
    unified_router_instance.include_router(wpa_db_ingestion_api.router)
    unified_router_instance.include_router(wpa_intelligent_merge_api.router)
    unified_router_instance.include_router(prompts_router)
    unified_router_instance.include_router(eda_recalculate_router)
    unified_router_instance.include_router(export_router)
    unified_router_instance.include_router(validation_router)
    unified_router_instance.include_router(pipelines_router)
    unified_router_instance.include_router(legacy_core_router.router)
    unified_router_instance.include_router(legacy_ingestion_router.router)
    unified_router_instance.include_router(unified_router.router)

    return unified_router_instance
