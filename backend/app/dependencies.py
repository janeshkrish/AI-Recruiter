from __future__ import annotations

from functools import lru_cache

from backend.app.core.config import Settings, get_settings
from backend.app.repositories.candidate_repository import CandidateRepository
from backend.app.services.analytics_service import AnalyticsService
from backend.app.services.copilot_service import CopilotService
from backend.app.services.ranking_service import RankingService
from backend.app.services.resume_service import ResumeService


@lru_cache(maxsize=1)
def get_candidate_repository() -> CandidateRepository:
    settings = get_settings()
    return CandidateRepository(settings.candidates_path)


@lru_cache(maxsize=1)
def get_ranking_service() -> RankingService:
    return RankingService(get_candidate_repository(), get_settings())


@lru_cache(maxsize=1)
def get_analytics_service() -> AnalyticsService:
    return AnalyticsService(get_candidate_repository(), get_ranking_service())


@lru_cache(maxsize=1)
def get_copilot_service() -> CopilotService:
    return CopilotService()


@lru_cache(maxsize=1)
def get_resume_service() -> ResumeService:
    return ResumeService(get_settings().max_upload_bytes)


def get_app_settings() -> Settings:
    return get_settings()
