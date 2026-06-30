from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CopilotRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    totalCandidates: int | None = None


class CopilotResponse(BaseModel):
    answer: str
