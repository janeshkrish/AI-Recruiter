from __future__ import annotations

from fastapi import APIRouter, Depends

from backend.app.dependencies import get_copilot_service
from backend.app.schemas.copilot import CopilotRequest, CopilotResponse
from backend.app.services.copilot_service import CopilotService


router = APIRouter()


@router.post("", response_model=CopilotResponse)
async def copilot(request: CopilotRequest, service: CopilotService = Depends(get_copilot_service)) -> dict:
    return {
        "answer": service.answer(
            request.question,
            request.candidates,
            request.totalCandidates,
        )
    }
