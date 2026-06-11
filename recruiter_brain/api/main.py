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


class CandidateScore(BaseModel):
    candidate_id: str
    score: float
    skill_match: float
    experience_match: float
    education_match: float
    semantic_similarity: float
    location_match: float
    reasoning: str


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
        results = await agent.run_pipeline(request.job_description)
        # Results are dicts mapping to CandidateScore
        return {"ranked_candidates": results}
    except Exception as e:
        logger.exception("Ranking failed")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/candidates")
async def get_candidates(limit: int = 100):
    """Return dataset candidates (metadata)."""
    vs: FAISSVectorStore = app_state.get("vector_store")
    if not vs or not vs.metadata:
        return {"candidates": []}
        
    return {"candidates": [m for m in vs.metadata[:limit]]}


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
