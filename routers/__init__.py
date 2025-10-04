"""
routers package: Contains all FastAPI router modules for the JV Dashboard API.
Easy to change: Add new routers here (e.g., from routers.products import router).
Import in backend.py like: from routers import deals, outreaches, etc.
"""

# Import all routers to make them available at package level
# (e.g., routers.deals.router or from routers import deals)
from .deals import router as deals_router
from .outreaches import router as outreaches_router
from .meetings import router as meetings_router
from .analytics import router as analytics_router

# Optional: Create a combined router for all endpoints (useful for mounting)
# Uncomment if you want a single entry point
# from fastapi import APIRouter
# combined_router = APIRouter()
# combined_router.include_router(deals_router)
# combined_router.include_router(outreaches_router)
# combined_router.include_router(meetings_router)
# combined_router.include_router(analytics_router)

# Make individual routers available directly (e.g., routers.deals_router)
__all__ = [
    'deals_router',
    'outreaches_router',
    'meetings_router',
    'analytics_router',
    # 'combined_router',  # Uncomment if using combined
]