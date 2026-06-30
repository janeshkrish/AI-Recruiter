from __future__ import annotations

from pydantic import BaseModel, Field


class ResumeUploadResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    text_preview: str
    extracted_skills: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
