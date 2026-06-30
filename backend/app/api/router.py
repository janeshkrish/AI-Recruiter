from __future__ import annotations

from fastapi import APIRouter

from backend.app.api.routes import analytics, candidates, copilot, health, ranking, resumes


api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(ranking.router, tags=["ranking"])
api_router.include_router(analytics.router, prefix="/pipeline", tags=["analytics"])
api_router.include_router(copilot.router, prefix="/copilot", tags=["copilot"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
