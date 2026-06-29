"""FastAPI wrapper for the offline Redrob ranker."""

from __future__ import annotations

import csv
from contextlib import asynccontextmanager
from io import StringIO
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from recruiter_brain.data.sqlite_store import SQLiteStore
from src.parser.jd_analyzer import DEFAULT_REDROB_JD, JDAnalyzer
from src.ranking.ranker import OfflineRanker


app_state: dict[str, Any] = {}
role_ranking_cache: dict[str, list[dict[str, Any]]] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_state["sqlite_store"] = SQLiteStore()
    yield
    app_state.clear()
    role_ranking_cache.clear()


app = FastAPI(
    title="AI Recruiter Offline API",
    description="Deterministic offline candidate ranking with no hosted LLM calls.",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RankRequest(BaseModel):
    job_description: str = Field(..., description="The raw JD text")
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


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "ranking_mode": "offline_deterministic",
        "network_required_for_ranking": False,
        "sqlite_initialized": "sqlite_store" in app_state,
    }


@app.post("/api/rank", response_model=RankResponse)
async def rank_candidates(request: RankRequest):
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")
    return _rank_response(request.job_description, request.custom_weights)


@app.post("/api/rank/role", response_model=RankResponse)
async def rank_role_candidates(request: RankRequest):
    if not request.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description is required")
    return _rank_response(request.job_description, request.custom_weights)


@app.get("/api/candidates")
async def get_candidates(
    page: int = 1,
    limit: int = 25,
    search: str = "",
    skills: str = "",
    min_experience: float = 0.0,
    current_role: str = "",
):
    sqlite_store = _store()
    filters = {"skills": skills, "min_experience": min_experience, "current_role": current_role}
    return sqlite_store.get_paginated_candidates(page=page, limit=limit, search=search, filters=filters)


@app.get("/api/candidates/role-ranking", response_model=RoleRankingResponse)
async def get_role_ranking(limit: int = 100):
    rows = _get_role_rows(DEFAULT_REDROB_JD, limit=limit)
    return {
        "role": "Senior AI Engineer - Founding Team",
        "source_documents": ["job_description.docx", "candidate_schema.json", "submission_spec.docx"],
        "total": len(rows),
        "rows": rows,
    }


@app.get("/api/candidates/role-ranking.csv")
async def download_role_ranking_csv(limit: int = 100):
    rows = _get_role_rows(DEFAULT_REDROB_JD, limit=100)
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["candidate_id", "rank", "score", "reasoning"])
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "candidate_id": row["candidate_id"],
                "rank": row["rank"],
                "score": f"{float(row['score']):.4f}",
                "reasoning": row["reasoning"],
            }
        )
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="redrob_senior_ai_engineer_ranking.csv"'},
    )


@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    data = _store().get_candidate_by_id(candidate_id)
    if not data:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return data


@app.get("/api/stats")
async def get_stats():
    return _store().get_stats()


@app.get("/api/jobs")
async def get_jobs():
    return {
        "jobs": [
            {
                "id": "JOB_001",
                "title": "Senior AI Engineer - Founding Team",
                "location": "Pune/Noida, India",
                "ranking_mode": "offline_deterministic",
            }
        ]
    }


@app.get("/api/pipeline/analytics")
async def get_pipeline_analytics():
    return {
        "ranking_mode": "offline_deterministic",
        "network_required_for_ranking": False,
        "feature_groups": [
            "production_ml_experience",
            "retrieval_ranking_experience",
            "vector_databases",
            "python_engineering",
            "evaluation_frameworks",
            "startup_product_mindset",
            "behavioral_signals",
            "career_progression",
            "location_relocation",
            "open_source_github",
        ],
    }


def _store() -> SQLiteStore:
    sqlite_store: SQLiteStore | None = app_state.get("sqlite_store")
    if not sqlite_store:
        raise HTTPException(status_code=503, detail="Database not ready")
    return sqlite_store


def _get_role_rows(jd_text: str, limit: int = 100, weights: dict[str, float] | None = None) -> list[dict[str, Any]]:
    safe_limit = max(1, min(limit, 500))
    cache_key = f"{hash(jd_text)}:{safe_limit}:{weights}"
    if cache_key not in role_ranking_cache:
        role_ranking_cache[cache_key] = OfflineRanker(jd_text=jd_text, weights=weights).rank_records(
            _store().iter_candidates(),
            top_n=safe_limit,
        )
    return role_ranking_cache[cache_key]


def _rank_response(jd_text: str, weights: dict[str, float] | None = None) -> dict[str, Any]:
    rows = _get_role_rows(jd_text, limit=100, weights=weights)
    stats = _store().get_stats()
    return {
        "ranked_candidates": [_row_to_candidate_score(row) for row in rows],
        "parsed_jd": JDAnalyzer().to_dict(JDAnalyzer().analyze(jd_text)),
        "pipeline_stats": {
            "total_indexed": stats.get("total_applicants", 0),
            "retrieved": stats.get("total_applicants", 0),
            "scored": stats.get("total_applicants", 0),
            "returned": len(rows),
        },
    }


def _row_to_candidate_score(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": row["candidate_id"],
        "rank": row["rank"],
        "score": row["overall_score"],
        "skill_match": row["skill_match"],
        "experience_match": row["experience_match"],
        "semantic_similarity": row["semantic_similarity"],
        "location_match": row["location_match"],
        "potential_score": row["potential_score"],
        "behavioral_score": row["behavioral_score"],
        "transferable_matches": row["transferable_matches"],
        "reasoning": row["reasoning"],
        "behavioral_insights": row["behavioral_insights"],
        "anti_pattern_flags": row["anti_pattern_flags"],
        "anti_pattern_penalty": row["anti_pattern_penalty"],
        "candidate_details": row["candidate_details"],
        "overall_score": row["overall_score"],
        "hiring_recommendation": row["hiring_recommendation"],
        "top_matching_evidence": row["top_matching_evidence"],
        "missing_requirements": row["missing_requirements"],
        "risk_factors": row["risk_factors"],
        "production_evidence": row["production_evidence"],
        "behavioral_evidence": row["behavioral_evidence"],
        "jd_alignment_score": row["jd_alignment_score"],
        "score_breakdown": row["score_breakdown"],
        "scoring_weights": row["scoring_weights"],
    }
