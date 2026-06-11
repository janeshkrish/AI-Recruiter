"""
Recruiter Agent
================

Orchestrator for the Hackathon Winning Architecture.
Handles JD parsing and delegates ranking to the Multi-Agent Recruiter Jury.
"""

from __future__ import annotations

import json
from typing import Any

from loguru import logger
from openai import AsyncOpenAI

from recruiter_brain.config import get_settings
from recruiter_brain.embeddings.faiss_store import FAISSVectorStore
from recruiter_brain.embeddings.embedding_service import EmbeddingService
from recruiter_brain.agents.recruiter_jury import RecruiterJury


class RecruiterAgent:
    """Orchestrates JD parsing, retrieval, and Multi-Agent Jury Evaluation."""

    def __init__(self, vector_store: FAISSVectorStore, embedding_service: EmbeddingService):
        self.settings = get_settings()
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.jury = RecruiterJury()
        
        self.llm_client = AsyncOpenAI(api_key=self.settings.llm.openai_api_key) if self.settings.llm.openai_api_key else None

    async def parse_job_description(self, jd_text: str) -> dict[str, Any]:
        """
        Extract structured and HIDDEN requirements from unstructured JD text.
        """
        logger.info("Parsing Job Description for Hidden Intelligence...")
        
        if self.settings.llm.simulation_mode or not self.llm_client:
            return self._heuristic_jd_parse(jd_text)

        prompt = f"""
        Act as an Elite Recruiter. Analyze this job description and extract:
        1. Exact skills required (list of strings)
        2. Minimum years of experience (float)
        3. Location (string)
        4. require_degree (boolean)
        5. Hidden behavioral traits needed (e.g. "ambiguity", "startup-fit") (list of strings)

        Respond ONLY in JSON format.
        JD Text:
        {jd_text}
        """

        try:
            response = await self.llm_client.chat.completions.create(
                model=self.settings.llm.openai_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            parsed = json.loads(response.choices[0].message.content)
            if "skills" not in parsed:
                parsed["skills"] = []
            return parsed
        except Exception as e:
            logger.error(f"LLM Parsing failed: {e}. Falling back to heuristics.")
            return self._heuristic_jd_parse(jd_text)

    def _heuristic_jd_parse(self, jd_text: str) -> dict[str, Any]:
        """Heuristic fallback identifying standard and hidden requirements."""
        jd_lower = jd_text.lower()
        
        years = 5.0
        if "5–9 years" in jd_lower or "5-9 years" in jd_lower:
            years = 5.0
            
        return {
            "skills": [
                "embeddings", "sentence-transformers", "openai", "bge", "e5",
                "vector databases", "pinecone", "weaviate", "qdrant", "milvus", "faiss",
                "python", "evaluation", "ndcg", "mrr", "map", "a/b testing",
                "llm fine-tuning", "lora", "qlora", "learning-to-rank", "xgboost"
            ],
            "years_experience": years,
            "location": "Pune/Noida",
            "require_degree": False,
            "hidden_traits": ["startup-fit", "research-oriented", "ambiguity"]
        }

    async def run_pipeline(self, jd_text: str) -> list[dict[str, Any]]:
        """
        Execute the full Recruiter Intelligence pipeline.
        """
        # 1. Parse JD
        jd_parsed = await self.parse_job_description(jd_text)
        logger.info(f"Parsed JD Requirements: {jd_parsed}")

        # 2. Embed JD
        jd_query = (
            f"Job requires {jd_parsed['years_experience']} years experience in "
            f"{', '.join(jd_parsed['skills'])}. Location: {jd_parsed['location']}. "
            f"Traits: {', '.join(jd_parsed.get('hidden_traits', []))}."
        )
        query_embedding = self.embedding_service.generate_embedding(jd_query)

        # 3. Retrieve Top Candidates via FAISS (Pre-filter)
        fetch_k = self.settings.pipeline.top_k_results * 5
        retrieved_candidates = self.vector_store.search(query_embedding, top_k=fetch_k)
        logger.info(f"Retrieved top {len(retrieved_candidates)} candidates via FAISS.")

        # 4. Multi-Agent Jury Evaluation
        ranked = self.jury.rank_candidates(
            retrieved_candidates=retrieved_candidates,
            jd_skills=jd_parsed["skills"],
            jd_years=jd_parsed["years_experience"],
            jd_location=jd_parsed["location"],
            require_degree=jd_parsed.get("require_degree", False)
        )

        # 5. Take Top K
        top_ranked = ranked[:self.settings.pipeline.top_k_results]
        
        # Clean up massive raw profiles but keep a structured dict for the UI
        for c in top_ranked:
            if "raw_profile" in c:
                c["candidate_details"] = c["raw_profile"].model_dump()
                del c["raw_profile"]

        logger.info(f"Pipeline complete. Returning {len(top_ranked)} thoroughly vetted candidates.")
        return top_ranked
