from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_DIR = REPO_ROOT / "[PUB] India_runs_data_and_ai_challenge" / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    app_name: str = "AI Recruiter Platform"
    app_version: str = "4.0.0"
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("AI_RECRUITER_APP_ENV", "AI_RECRUITER_ENVIRONMENT", "APP_ENV"),
    )
    api_prefix: str = "/api"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    dataset_path: Path = DEFAULT_DATASET_DIR
    candidates_file: str = "candidates.jsonl"
    default_jd_file: Path = REPO_ROOT / "jd.txt"
    default_ranking_csv: Path = REPO_ROOT / "redrob_senior_ai_engineer_ranking.csv"

    max_upload_bytes: int = 5 * 1024 * 1024
    ranking_cache_size: int = 16
    api_ranking_pool_size: int = 3000

    model_config = SettingsConfigDict(
        env_file=(REPO_ROOT / ".env", REPO_ROOT / "backend" / ".env"),
        env_prefix="AI_RECRUITER_",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def candidates_path(self) -> Path:
        return self.dataset_path / self.candidates_file


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
