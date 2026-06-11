"""
AI Recruiter Brain — Central Configuration
===========================================

All configuration is loaded from environment variables (.env file)
with sensible defaults for local development.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


# ---------------------------------------------------------------------------
# Resolve project root
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


class LLMSettings(BaseSettings):
    """LLM provider configuration."""

    provider: str = Field(default="openai", alias="LLM_PROVIDER")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1", alias="OPENAI_MODEL")
    deepseek_api_key: str = Field(default="", alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1", alias="DEEPSEEK_BASE_URL"
    )
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    simulation_mode: bool = Field(default=True, alias="SIMULATION_MODE")

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


class EmbeddingSettings(BaseSettings):
    """Embedding model configuration."""

    model_name: str = Field(
        default="BAAI/bge-large-en-v1.5", alias="EMBEDDING_MODEL"
    )
    dimension: int = Field(default=1024, alias="EMBEDDING_DIMENSION")
    batch_size: int = Field(default=64, alias="EMBEDDING_BATCH_SIZE")

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


class QdrantSettings(BaseSettings):
    """Qdrant vector database configuration."""

    host: str = Field(default="localhost", alias="QDRANT_HOST")
    port: int = Field(default=6333, alias="QDRANT_PORT")
    collection: str = Field(default="candidates", alias="QDRANT_COLLECTION")
    use_inmemory: bool = Field(default=True, alias="QDRANT_USE_INMEMORY")

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


class PipelineSettings(BaseSettings):
    """Pipeline stage thresholds."""

    stage1_top_k: int = Field(default=2000, alias="STAGE1_TOP_K")
    stage2_top_k: int = Field(default=500, alias="STAGE2_TOP_K")
    stage3_top_k: int = Field(default=200, alias="STAGE3_TOP_K")
    stage4_top_k: int = Field(default=25, alias="STAGE4_TOP_K")

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


class ScoringWeights(BaseSettings):
    """Agent score weights for final ranking."""

    technical: float = Field(default=0.35, alias="WEIGHT_TECHNICAL")
    career: float = Field(default=0.20, alias="WEIGHT_CAREER")
    behavioral: float = Field(default=0.15, alias="WEIGHT_BEHAVIORAL")
    potential: float = Field(default=0.15, alias="WEIGHT_POTENTIAL")
    recruiter: float = Field(default=0.15, alias="WEIGHT_RECRUITER")

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}

    @property
    def as_dict(self) -> dict[str, float]:
        return {
            "technical": self.technical,
            "career": self.career,
            "behavioral": self.behavioral,
            "potential": self.potential,
            "recruiter": self.recruiter,
        }


class LoggingSettings(BaseSettings):
    """Logging configuration."""

    level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_file: str = Field(default="recruiter_brain.log", alias="LOG_FILE")

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


class Settings:
    """Aggregated settings singleton."""

    _instance: Optional["Settings"] = None

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_settings()
        return cls._instance

    def _init_settings(self) -> None:
        self.llm = LLMSettings()
        self.embedding = EmbeddingSettings()
        self.qdrant = QdrantSettings()
        self.pipeline = PipelineSettings()
        self.weights = ScoringWeights()
        self.logging = LoggingSettings()
        self.project_root = PROJECT_ROOT
        self.data_dir = DATA_DIR


def get_settings() -> Settings:
    """Get the global settings instance."""
    return Settings()
