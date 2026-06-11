"""
AI Recruiter Brain — FastAPI Backend
======================================

REST API endpoints for the recruitment ranking system.

Endpoints:
    POST /api/rank         — Submit JD, trigger full pipeline
    GET  /api/candidates/{id}       — Get candidate detail
    GET  /api/candidates/{id}/explain  — Get explainability report
    POST /api/jd/parse     — Parse JD only (Agent 1)
    GET  /api/status       — Health check and pipeline status
"""

from __future__ import annotations

import asyncio
import time
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from recruiter_brain.config import get_settings
from recruiter_brain.data.models import (
    CandidateProfile,
    CandidateRanking,
    Explanation,
    HealthResponse,
    RankRequest,
    RankResponse,
    RoleParsedOutput,
)
from recruiter_brain.scoring.explainability import ExplainabilityEngine
from recruiter_brain.scoring.ranking_engine import HybridRankingEngine


# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------

engine: Optional[HybridRankingEngine] = None
explainer: Optional[ExplainabilityEngine] = None
last_rank_result: Optional[RankResponse] = None
pipeline_status: dict = {"state": "idle", "message": "Ready"}


async def initialize_engine(num_candidates: int = 1000) -> None:
    """Initialize the ranking engine and index candidates."""
    global engine, explainer

    from recruiter_brain.data.generate_synthetic_data import load_candidates

    logger.info("Initializing ranking engine...")
    engine = HybridRankingEngine()
    explainer = ExplainabilityEngine(engine.potential_agent)

    # Load and index candidates
    candidates = load_candidates(limit=num_candidates)
    engine.index_candidates(candidates)
    logger.info(f"✓ Engine ready with {len(candidates):,} candidates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting AI Recruiter Brain API...")
    await initialize_engine(num_candidates=1000)
    yield
    # Shutdown
    logger.info("Shutting down AI Recruiter Brain API...")


# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="AI Recruiter Brain",
    description=(
        "Multi-Agent Recruitment Intelligence System — "
        "Ranks candidates using 6 specialized AI agents."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS for Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/status", response_model=HealthResponse)
async def health_check():
    """Health check and system status."""
    return HealthResponse(
        status="healthy" if engine else "initializing",
        version="1.0.0",
        qdrant_connected=engine is not None and engine.vector_store.get_count() > 0,
        model_loaded=engine is not None,
        candidates_indexed=engine.vector_store.get_count() if engine else 0,
    )


@app.post("/api/jd/parse", response_model=RoleParsedOutput)
async def parse_job_description(request: RankRequest):
    """Parse a job description using Agent 1 (Role Understanding)."""
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    parsed = await engine.role_agent.parse(request.job_description)
    return parsed


@app.post("/api/rank", response_model=RankResponse)
async def rank_candidates(request: RankRequest):
    """
    Execute the full ranking pipeline.

    Triggers all 4 stages and returns top-K ranked candidates
    with scores and pipeline statistics.
    """
    global last_rank_result, pipeline_status

    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    pipeline_status = {"state": "running", "message": "Pipeline in progress..."}

    try:
        start = time.time()

        result = await engine.rank(
            job_description=request.job_description,
            job_title=request.job_title,
            top_k=request.top_k,
            custom_weights=request.weights,
        )

        elapsed = time.time() - start
        pipeline_status = {
            "state": "complete",
            "message": f"Pipeline completed in {elapsed:.1f}s",
            "elapsed_seconds": elapsed,
        }

        last_rank_result = result
        return result

    except Exception as e:
        pipeline_status = {"state": "error", "message": str(e)}
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Get detailed candidate profile with all scores."""
    if engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    candidate = engine.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    scores = engine.get_candidate_scores(candidate_id)

    return {
        "candidate": candidate.model_dump(),
        "scores": scores.model_dump() if scores else None,
    }


@app.get("/api/candidates/{candidate_id}/explain", response_model=Explanation)
async def explain_candidate(candidate_id: str):
    """Get explainability report for a candidate."""
    if engine is None or explainer is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    if last_rank_result is None:
        raise HTTPException(
            status_code=400,
            detail="Run /api/rank first to generate rankings",
        )

    candidate = engine.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")

    scores = engine.get_candidate_scores(candidate_id)
    if scores is None:
        raise HTTPException(
            status_code=400,
            detail="Candidate has not been scored yet",
        )

    explanation = explainer.explain(
        candidate=candidate,
        scores=scores,
        parsed_role=last_rank_result.parsed_role,
    )

    return explanation


@app.get("/api/pipeline/status")
async def get_pipeline_status():
    """Get current pipeline execution status."""
    return pipeline_status


@app.get("/api/rankings")
async def get_last_rankings():
    """Get the last ranking results."""
    if last_rank_result is None:
        return {"message": "No rankings available. Run /api/rank first."}
    return last_rank_result


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "recruiter_brain.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
