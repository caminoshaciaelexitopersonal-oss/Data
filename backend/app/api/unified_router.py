# backend/app/api/unified_router.py

"""
The Unified API Router for SADI.

This router serves as the single, stable entry point for all frontend operations
and consolidates all functional backend modules (MCP, MPA, WPA).
"""

from fastapi import APIRouter
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
from backend.app.api.core import router as core_router # For chat agent
from backend.app.api.ingestion_orchestrator import router as ingestion_orchestrator_router

router = APIRouter(prefix="/unified/v1", tags=["Unified Stable Endpoints"])

# Include all functional routers from the new architecture
router.include_router(mcp_api.router)
router.include_router(ingestion_mpa_api.router)
router.include_router(eda_mpa_api.router)
router.include_router(quality_mpa_api.router)
router.include_router(ml_mpa_api.router)
router.include_router(wpa_auto_analysis_api.router)
router.include_router(wpa_modeling_api.router)
router.include_router(wpa_report_generation_api.router)
router.include_router(wpa_db_ingestion_api.router)
router.include_router(wpa_intelligent_merge_api.router)
router.include_router(prompts_router)
router.include_router(eda_recalculate_router)
router.include_router(export_router)
router.include_router(validation_router)
router.include_router(pipelines_router)
router.include_router(core_router)
router.include_router(ingestion_orchestrator_router)
