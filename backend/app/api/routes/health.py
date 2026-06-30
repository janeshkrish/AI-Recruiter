from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.core.config import Settings
from backend.app.dependencies import get_app_settings


router = APIRouter()


@router.get("/health")
@router.get("/status")
async def health(settings: Settings = Depends(get_app_settings)) -> dict:
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "ranking_mode": "offline_deterministic",
        "network_required_for_ranking": False,
    }
