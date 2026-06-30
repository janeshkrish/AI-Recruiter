from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RankRequest(BaseModel):
    job_description: str = Field(..., min_length=1)
    custom_weights: dict[str, float] | None = None


class CandidateScore(BaseModel):
    candidate_id: str
    rank: int | None = None
    score: float
    skill_match: float
    experience_match: float
    semantic_similarity: float
    location_match: float
    potential_score: float = 0.0
    behavioral_score: float = 0.0
    transferable_matches: int = 0
    reasoning: str
    behavioral_insights: list[str] = Field(default_factory=list)
    anti_pattern_flags: list[str] = Field(default_factory=list)
    anti_pattern_penalty: float = 1.0
    candidate_details: dict[str, Any] = Field(default_factory=dict)
    overall_score: float | None = None
    hiring_recommendation: str | None = None
    top_matching_evidence: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    production_evidence: list[str] = Field(default_factory=list)
    behavioral_evidence: list[str] = Field(default_factory=list)
    jd_alignment_score: float | None = None
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    scoring_weights: dict[str, float] = Field(default_factory=dict)


class RankResponse(BaseModel):
    ranked_candidates: list[CandidateScore]
    parsed_jd: dict[str, Any] = Field(default_factory=dict)
    pipeline_stats: dict[str, Any] = Field(default_factory=dict)


class RoleRankingRow(BaseModel):
    candidate_id: str
    rank: int
    score: float
    reasoning: str
    candidate: dict[str, Any] = Field(default_factory=dict)
    overall_score: float | None = None
    hiring_recommendation: str | None = None
    top_matching_evidence: list[str] = Field(default_factory=list)
    missing_requirements: list[str] = Field(default_factory=list)
    risk_factors: list[str] = Field(default_factory=list)
    production_evidence: list[str] = Field(default_factory=list)
    behavioral_evidence: list[str] = Field(default_factory=list)
    jd_alignment_score: float | None = None
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    scoring_weights: dict[str, float] = Field(default_factory=dict)


class RoleRankingResponse(BaseModel):
    role: str
    source_documents: list[str]
    total: int
    rows: list[RoleRankingRow]
