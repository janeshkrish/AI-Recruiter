from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from backend.app.core.errors import AppError
from backend.app.dependencies import get_candidate_repository, get_ranking_service
from backend.app.repositories.candidate_repository import CandidateRepository
from backend.app.schemas.ranking import RoleRankingResponse
from backend.app.services.ranking_service import RankingService


router = APIRouter()


@router.get("")
async def list_candidates(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=500),
    search: str = "",
    skills: str = "",
    min_experience: float = 0.0,
    current_role: str = "",
    repository: CandidateRepository = Depends(get_candidate_repository),
) -> dict:
    return repository.list_candidates(
        page=page,
        limit=limit,
        search=search,
        skills=skills,
        min_experience=min_experience,
        current_role=current_role,
    )


@router.get("/role-ranking", response_model=RoleRankingResponse)
async def role_ranking(
    limit: int = Query(100, ge=1, le=500),
    ranking_service: RankingService = Depends(get_ranking_service),
) -> dict:
    return await run_in_threadpool(lambda: ranking_service.role_ranking_response(limit=limit))


@router.get("/role-ranking.csv")
async def role_ranking_csv(
    limit: int = Query(100, ge=1, le=500),
    ranking_service: RankingService = Depends(get_ranking_service),
) -> StreamingResponse:
    content = await run_in_threadpool(lambda: ranking_service.role_ranking_csv(limit=limit))
    return StreamingResponse(
        iter([content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="redrob_senior_ai_engineer_ranking.csv"'},
    )


@router.get("/{candidate_id}")
async def get_candidate(
    candidate_id: str,
    repository: CandidateRepository = Depends(get_candidate_repository),
) -> dict:
    candidate = repository.get_by_id(candidate_id)
    if not candidate:
        raise AppError("Candidate not found.", status_code=404, code="CANDIDATE_NOT_FOUND")
    return candidate
