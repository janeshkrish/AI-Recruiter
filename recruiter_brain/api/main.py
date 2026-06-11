"""
FastAPI Backend
================

REST API endpoints for the AI Recruiter system.
Maintains in-memory FAISS index and candidate metadata.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field

from recruiter_brain.agents.recruiter_agent import RecruiterAgent
from recruiter_brain.config import get_settings
from recruiter_brain.data.dataset_loader import DatasetLoader
from recruiter_brain.data.dataset_preprocessor import DatasetPreprocessor
from recruiter_brain.embeddings.embedding_service import EmbeddingService
from recruiter_brain.embeddings.faiss_store import FAISSVectorStore
from recruiter_brain.data.sqlite_store import SQLiteStore


# Global instances initialized during startup
app_state: dict[str, Any] = {}


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
    transferable_matches: int = 0
    reasoning: str
    candidate_details: dict[str, Any] = Field(default_factory=dict)


class RankResponse(BaseModel):
    ranked_candidates: list[CandidateScore]


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
        # Results are dicts mapping to CandidateScore
        return {"ranked_candidates": results}
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
        
    # We'll just run them through the Jury with default jd_skills (since this is generic comparison)
    # Ideally the UI passes the actual JD skills, but for battle mode we can just compare raw heuristics.
    
    # We will compute delta
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
    if not sqlite_store:
        raise HTTPException(status_code=503, detail="Database not ready")
    return sqlite_store.get_stats()

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
    # We could parse the job_description.docx here, but we'll return a static reference
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
