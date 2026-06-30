from __future__ import annotations

from fastapi import APIRouter, Depends
from starlette.concurrency import run_in_threadpool

from backend.app.dependencies import get_candidate_repository, get_ranking_service
from backend.app.repositories.candidate_repository import CandidateRepository
from backend.app.schemas.ranking import RankRequest, RankResponse
from backend.app.services.ranking_service import RankingService


router = APIRouter()


@router.get("/stats")
async def stats(repository: CandidateRepository = Depends(get_candidate_repository)) -> dict:
    return repository.stats()


@router.post("/rank", response_model=RankResponse)
@router.post("/rank/role", response_model=RankResponse)
async def rank_candidates(
    request: RankRequest,
    ranking_service: RankingService = Depends(get_ranking_service),
) -> dict:
    return await run_in_threadpool(
        ranking_service.rank_response,
        request.job_description,
        request.custom_weights,
    )
