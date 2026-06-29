"""
Configuration
==============

Centralized settings for the AI Recruiter Brain using Pydantic BaseSettings.
Configurable via environment variables or .env file.
"""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatasetSettings(BaseSettings):
    """Dataset configuration settings."""

    # Path to the dataset directory
    path: str = r"C:\Users\THIVAKAR\AI-Recruiter\[PUB] India_runs_data_and_ai_challenge\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge"
    candidates_file: str = "candidates.jsonl"
    cache_dir: str = ".cache"
    
    # Batch processing
    chunk_size: int = 5000

    model_config = SettingsConfigDict(
        env_prefix="DATASET_", env_file=".env", extra="ignore"
    )


class ScoringWeights(BaseSettings):
    """
    Weights for the 5-dimensional scoring model.
    Must sum to 1.0 (or 100%).
    """

    skill_match: float = 0.40
    experience_match: float = 0.25
    education_match: float = 0.10
    semantic_similarity: float = 0.20
    location_match: float = 0.05

    @property
    def as_dict(self) -> dict[str, float]:
        return {
            "skill_match": self.skill_match,
            "experience_match": self.experience_match,
            "education_match": self.education_match,
            "semantic_similarity": self.semantic_similarity,
            "location_match": self.location_match,
        }

    model_config = SettingsConfigDict(
        env_prefix="WEIGHT_", env_file=".env", extra="ignore"
    )


class PipelineSettings(BaseSettings):
    """Pipeline configuration."""
    
    top_k_results: int = 100

    model_config = SettingsConfigDict(
        env_prefix="PIPELINE_", env_file=".env", extra="ignore"
    )


class Settings(BaseSettings):
    """Global application settings."""

    dataset: DatasetSettings = DatasetSettings()
    weights: ScoringWeights = ScoringWeights()
    pipeline: PipelineSettings = PipelineSettings()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings singleton.
    Cached to prevent re-reading the .env file on every call.
    """
    # Ensure cache dir exists
    settings = Settings()
    os.makedirs(settings.dataset.cache_dir, exist_ok=True)
    return settings
