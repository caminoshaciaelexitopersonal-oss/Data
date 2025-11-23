"""
File: sadi_router.py
Purpose: Provides the canonical /sadi/v1 router by sourcing its definition
         from the centralized unified_routes_def.py to avoid duplication.
"""
from backend.app.api.unified_routes_def import get_unified_router

# The router is now built and imported from a single source of truth
router = get_unified_router()
