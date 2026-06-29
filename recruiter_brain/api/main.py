"""
FastAPI Backend
================

REST API endpoints for the AI Recruiter system.
Maintains in-memory FAISS index and candidate metadata.
"""

from __future__ import annotations

import os
import csv
from contextlib import asynccontextmanager
from io import StringIO
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from loguru import logger
from pydantic import BaseModel, Field
from cachetools import TTLCache

from recruiter_brain.agents.recruiter_agent import RecruiterAgent
from recruiter_brain.config import get_settings
from recruiter_brain.data.dataset_loader import DatasetLoader
from recruiter_brain.data.dataset_preprocessor import DatasetPreprocessor
from recruiter_brain.embeddings.embedding_service import EmbeddingService
from recruiter_brain.embeddings.faiss_store import FAISSVectorStore
from recruiter_brain.data.sqlite_store import SQLiteStore
from recruiter_brain.scoring.document_ranker import DocumentInformedRanker


# Global instances initialized during startup
app_state: dict[str, Any] = {}
role_ranking_cache = TTLCache(maxsize=8, ttl=900)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initialize models and load dataset into memory/FAISS."""
    logger.info("Initializing AI Recruiter Engine...")
    settings = get_settings()
    
    # 1. Initialize core services
    embedding_service = EmbeddingService()
    vector_store = FAISSVectorStore()
    
    # 1.5 Initialize SQLite Cache
    logger.info("Initializing SQLite Cache...")
    sqlite_store = SQLiteStore()
    app_state["sqlite_store"] = sqlite_store
    
    # 2. If FAISS is empty, build it from the dataset
    if vector_store.is_empty():
        logger.info("FAISS index empty. Building from dataset...")
        loader = DatasetLoader()
        preprocessor = DatasetPreprocessor()
        
        # Load batch of candidates (chunking is better but we load all if limit=-1)
        candidates = loader.load_candidates_batch(limit=settings.dataset.chunk_size)
        preprocessed = preprocessor.preprocess_batch(candidates)
        
        if not preprocessed:
            logger.warning("No candidates loaded to index!")
        else:
            embeddings = embedding_service.generate_candidate_embeddings(preprocessed)
            vector_store.add_embeddings(embeddings, preprocessed)
            vector_store.save()
            
    # 3. Initialize Agent
    agent = RecruiterAgent(vector_store=vector_store, embedding_service=embedding_service)
    
    # Store in global state
    app_state["agent"] = agent
    app_state["vector_store"] = vector_store
    
    logger.info("AI Recruiter Engine Ready.")
    
    yield
    
    # Cleanup
    logger.info("Shutting down engine...")
    app_state.clear()


app = FastAPI(
    title="AI Recruiter Brain API",
    description="Multi-dimensional candidate ranking system using FAISS and real datasets.",
    version="2.0.0",
    lifespan=lifespan
)

# Allow CORS for UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/Response Models ---

class RankRequest(BaseModel):
    job_description: str = Field(..., description="The raw JD text")
    custom_weights: dict[str, float] | None = None

class CopilotRequest(BaseModel):
    question: str
    candidates: list[dict[str, Any]]

class BattleRequest(BaseModel):
    candidate1_id: str
    candidate2_id: str


class CandidateScore(BaseModel):
    candidate_id: str
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


class RoleRankingResponse(BaseModel):
    role: str
    source_documents: list[str]
    total: int
    rows: list[RoleRankingRow]


# --- Endpoints ---

@app.get("/api/health")
async def health_check():
    """Service health status."""
    return {"status": "healthy", "vector_store_initialized": "vector_store" in app_state}


@app.post("/api/rank", response_model=RankResponse)
async def rank_candidates(request: RankRequest):
    """Execute the full ranking pipeline for the given Job Description."""
    agent: RecruiterAgent = app_state.get("agent")
    if not agent:
        raise HTTPException(status_code=503, detail="Agent not initialized")
        
    try:
        results = await agent.run_pipeline(request.job_description, custom_weights=request.custom_weights)
        return results
    except Exception as e:
        logger.exception("Ranking failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/landscape")
async def get_talent_landscape(limit: int = 200):
    """Run PCA to compress FAISS embeddings into 2D coordinates for the UI Scatter Plot."""
    vs: FAISSVectorStore = app_state.get("vector_store")
    if not vs or not vs.metadata or vs.is_empty():
        return {"points": []}
    
    try:
        import numpy as np
        from sklearn.decomposition import PCA
        
        # Get up to 'limit' vectors
        vectors = vs.index.reconstruct_n(0, min(limit, vs.index.ntotal))
        
        # We need a fallback if we don't have enough data
        if len(vectors) < 3:
            return {"points": []}
            
        pca = PCA(n_components=3)
        coords = pca.fit_transform(vectors)
        
        points = []
        for i, coord in enumerate(coords):
            # Normalize to 0-100 scale for UI
            points.append({
                "candidate_id": vs.metadata[i]["candidate_id"],
                "x": float(coord[0]) * 10,
                "y": float(coord[1]) * 10,
                "z": float(coord[2]) * 10
            })
            
        return {"points": points}
    except ImportError:
        logger.warning("scikit-learn not installed, returning empty landscape")
        return {"points": []}
    except Exception as e:
        logger.exception("Landscape generation failed")
        return {"points": []}

@app.post("/api/copilot")
async def copilot_chat(request: CopilotRequest):
    """Heuristic explanation engine returning natural language about candidates."""
    q = request.question.lower()
    cands = request.candidates
    
    if not cands:
        return {"answer": "I need candidate data to provide insights."}
        
    c1 = cands[0]
    
    if "why" in q and "rank" in q:
        reasons = c1.get("reasoning", "Strong overall match.")
        return {"answer": f"Candidate {c1['candidate_id']} ranked highly because: {reasons}. Their potential score is {c1.get('potential_score', 0)}%."}
        
    if "compare" in q and len(cands) >= 2:
        c2 = cands[1]
        c1_tech = c1.get("skill_match", 0)
        c2_tech = c2.get("skill_match", 0)
        better_tech = c1['candidate_id'] if c1_tech > c2_tech else c2['candidate_id']
        diff = abs(c1_tech - c2_tech)
        return {"answer": f"Comparing the top two: {better_tech} has a {diff:.1f}% higher technical score. However, look at their Potential Score and Transferable Skills to make the final call."}
        
    if "hidden gem" in q:
        gems = [c for c in cands if c.get("potential_score", 0) > 85 and c.get("experience_match", 100) < 60]
        if gems:
            return {"answer": f"Yes! Look at {gems[0]['candidate_id']}. They have massive learning potential ({gems[0]['potential_score']}%) despite lower traditional experience."}
        return {"answer": "No obvious hidden gems in this immediate batch. Try adjusting the What-If weights!"}
    
    if "risk" in q or "flag" in q:
        flagged = [c for c in cands if c.get("anti_pattern_flags")]
        if flagged:
            flags = flagged[0].get("anti_pattern_flags", [])
            return {"answer": f"⚠ {flagged[0]['candidate_id']} has flags: {', '.join(flags)}. Consider these carefully."}
        return {"answer": "No significant risk flags detected in the current shortlist."}
    
    if "behavioral" in q or "respond" in q or "available" in q:
        best_behavioral = max(cands, key=lambda c: c.get("behavioral_score", 0))
        insights = best_behavioral.get("behavioral_insights", [])
        return {"answer": f"Most engaged candidate: {best_behavioral['candidate_id']} (Behavioral: {best_behavioral.get('behavioral_score', 0):.0f}%). Key signals: {'; '.join(insights[:3])}"}
        
    return {"answer": "Based on the Multi-Agent evaluation, these candidates represent the absolute top tier for your specific JD requirements. Is there a specific metric you'd like me to explain?"}


@app.post("/api/battle")
async def candidate_battle(request: BattleRequest):
    """Battle mode: Compares two candidates and predicts a winner."""
    vs: FAISSVectorStore = app_state.get("vector_store")
    if not vs or not vs.metadata:
        raise HTTPException(status_code=503, detail="Index not ready")
        
    c1 = next((m for m in vs.metadata if m["candidate_id"] == request.candidate1_id), None)
    c2 = next((m for m in vs.metadata if m["candidate_id"] == request.candidate2_id), None)
    
    if not c1 or not c2:
        raise HTTPException(status_code=404, detail="Candidate not found")
        
    return {
        "candidate1": request.candidate1_id,
        "candidate2": request.candidate2_id,
        "winner": request.candidate1_id if c1.get("years_of_experience", 0) > c2.get("years_of_experience", 0) else request.candidate2_id,
        "reasoning": f"In a direct matchup, {request.candidate1_id} shows different strengths. (Full logic implemented in Agent)."
    }

@app.get("/api/stats")
async def get_stats():
    """Return dataset statistics."""
    sqlite_store: SQLiteStore = app_state.get("sqlite_store")
    vs: FAISSVectorStore = app_state.get("vector_store")
    
    if not sqlite_store:
        raise HTTPException(status_code=503, detail="Database not ready")
    
    stats = sqlite_store.get_stats()
    
    # Add FAISS stats
    if vs and vs.index:
        stats["indexed_candidates"] = vs.index.ntotal
    else:
        stats["indexed_candidates"] = 0
        
    return stats

@app.get("/api/candidates")
async def get_candidates(
    page: int = 1, 
    limit: int = 25, 
    search: str = "",
    skills: str = "",
    min_experience: float = 0.0,
    current_role: str = ""
):
    """Return dataset candidates with server-side pagination."""
    sqlite_store: SQLiteStore = app_state.get("sqlite_store")
    if not sqlite_store:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    filters = {
        "skills": skills,
        "min_experience": min_experience,
        "current_role": current_role
    }
    return sqlite_store.get_paginated_candidates(page=page, limit=limit, search=search, filters=filters)


def _get_role_ranking(limit: int = 100) -> list[dict[str, Any]]:
    sqlite_store: SQLiteStore = app_state.get("sqlite_store")
    if not sqlite_store:
        raise HTTPException(status_code=503, detail="Database not ready")

    safe_limit = max(1, min(limit, 500))
    cache_key = f"redrob-senior-ai-engineer:{safe_limit}"
    if cache_key not in role_ranking_cache:
        ranker = DocumentInformedRanker()
        role_ranking_cache[cache_key] = ranker.rank(
            sqlite_store.iter_role_ranking_candidates(pool_limit=3000),
            top_n=safe_limit,
        )
    return role_ranking_cache[cache_key]


@app.get("/api/candidates/role-ranking", response_model=RoleRankingResponse)
async def get_role_ranking(limit: int = 100):
    """Return document-informed candidate ranking rows for the attached Redrob role."""
    rows = _get_role_ranking(limit=limit)
    return {
        "role": "Senior AI Engineer - Founding Team",
        "source_documents": [
            "job_description.docx",
            "submission_spec.docx",
            "redrob_signals_doc.docx",
        ],
        "total": len(rows),
        "rows": rows,
    }


@app.get("/api/candidates/role-ranking.csv")
async def download_role_ranking_csv(limit: int = 100):
    """Download the document-informed ranking as submission-spec CSV."""
    rows = _get_role_ranking(limit=limit)
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=["candidate_id", "rank", "score", "reasoning"])
    writer.writeheader()
    for row in rows:
        writer.writerow(
            {
                "candidate_id": row["candidate_id"],
                "rank": row["rank"],
                "score": row["score"],
                "reasoning": row["reasoning"],
            }
        )
    output.seek(0)
    filename = "redrob_senior_ai_engineer_ranking.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/candidates/{candidate_id}")
async def get_candidate(candidate_id: str):
    """Return full raw data for a specific candidate."""
    sqlite_store: SQLiteStore = app_state.get("sqlite_store")
    if not sqlite_store:
        raise HTTPException(status_code=503, detail="Database not ready")
        
    data = sqlite_store.get_candidate_by_id(candidate_id)
    if not data:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return data


@app.get("/api/jobs")
async def get_jobs():
    """Return available jobs. For this challenge, we just have the one JD file."""
    return {
        "jobs": [
            {
                "id": "JOB_001",
                "title": "Senior AI Engineer — Founding Team",
                "location": "Pune/Noida, India",
                "file": "job_description.docx"
            }
        ]
    }

@app.get("/api/pipeline/analytics")
async def get_pipeline_analytics():
    """Return analytics data for the Pipeline Analytics page."""
    from recruiter_brain.scoring.skill_graph import SkillTransferGraph
    
    graph = SkillTransferGraph()
    graph_stats = graph.get_graph_stats()
    
    vs: FAISSVectorStore = app_state.get("vector_store")
    
    return {
        "skill_graph": graph_stats,
        "vector_store": {
            "total_indexed": vs.index.ntotal if vs and vs.index else 0,
            "dimension": vs.dimension if vs else 0,
        },
        "agents": [
            {"name": "Technical Fit", "id": "agent_a", "description": "Skill Transfer Graph + strict matching"},
            {"name": "Career Intelligence", "id": "agent_b", "description": "Promotion velocity + experience depth"},
            {"name": "Behavioral Intelligence", "id": "agent_c", "description": "23 Redrob signals analysis"},
            {"name": "Potential Intelligence", "id": "agent_d", "description": "Learning velocity + domain alignment"},
            {"name": "Anti-Pattern Detection", "id": "agent_e", "description": "Consulting-only, title-hopping, keyword-stuffing"},
        ],
        "weights": get_settings().weights.as_dict
    }
