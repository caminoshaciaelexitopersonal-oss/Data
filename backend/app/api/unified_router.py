from fastapi import APIRouter
from backend.mcp.api import router as mcp_router
from backend.mpa.ingestion.api import router as ingestion_router
from backend.mpa.quality.api import router as quality_router
from backend.agent.api import router as agent_router

router = APIRouter()

# Current stable and final architecture
unified_router = APIRouter(prefix="/unified/v1")
unified_router.include_router(mcp_router, prefix="/mcp", tags=["Main Control Plane"])
unified_router.include_router(ingestion_router, prefix="/mpa/ingestion", tags=["Modular Process Architecture"])
unified_router.include_router(quality_router, prefix="/mpa/quality", tags=["Modular Process Architecture"])
unified_router.include_router(agent_router, tags=["Intelligent Agent"])

router.include_router(unified_router)
