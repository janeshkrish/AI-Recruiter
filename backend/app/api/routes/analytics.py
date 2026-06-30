from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_analytics_service
from backend.app.services.analytics_service import AnalyticsService


router = APIRouter()


@router.get("/analytics")
async def pipeline_analytics(service: AnalyticsService = Depends(get_analytics_service)) -> dict:
    return service.pipeline_analytics()
