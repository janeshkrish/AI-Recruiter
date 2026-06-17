"""
Recruiter Agent
================

Orchestrator for the Hackathon Winning Architecture.
Handles JD parsing and delegates ranking to the Multi-Agent Recruiter Jury.
"""

from __future__ import annotations

import json
import re
from typing import Any

from loguru import logger
from openai import AsyncOpenAI
from cachetools import cached, TTLCache
import hashlib

# Cache for JD Parsing to avoid repeated LLM calls (1 hour TTL)
jd_cache = TTLCache(maxsize=100, ttl=3600)
# Cache for FAISS Retrieval (1 hour TTL)
retrieval_cache = TTLCache(maxsize=100, ttl=3600)

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
        Uses LLM when available, falls back to intelligent heuristic parsing.
        """
        logger.info("Parsing Job Description for Hidden Intelligence...")
        jd_hash = hashlib.md5(jd_text.encode('utf-8')).hexdigest()
        
        if jd_hash in jd_cache:
            return jd_cache[jd_hash]
            
        if self.settings.llm.simulation_mode or not self.llm_client:
            res = self._heuristic_jd_parse(jd_text)
            jd_cache[jd_hash] = res
            return res

        prompt = f"""
        Act as an Elite Recruiter. Analyze this job description and extract:
        1. Exact skills required (list of strings)
        2. Minimum years of experience (float)
        3. Location (string)
        4. require_degree (boolean)
        5. Hidden behavioral traits needed (e.g. "ambiguity", "startup-fit") (list of strings)
        6. Anti-patterns to avoid (list of strings describing candidate types to reject)

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
            jd_cache[jd_hash] = parsed
            return parsed
        except Exception as e:
            logger.error(f"LLM Parsing failed: {e}. Falling back to heuristics.")
            return self._heuristic_jd_parse(jd_text)

    def _heuristic_jd_parse(self, jd_text: str) -> dict[str, Any]:
        """
        Intelligent heuristic JD parsing that actually reads the text.
        Extracts skills, experience, location, traits, and anti-patterns
        using NLP-style pattern matching.
        """
        jd_lower = jd_text.lower()
        
        # ─── 1. Extract years of experience ───
        years = 5.0  # Default
        # Match patterns like "5-9 years", "5+ years", "5–9 years"
        year_patterns = [
            r'(\d+)\s*[-–]\s*(\d+)\s*years?',  # "5-9 years"
            r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',  # "5+ years experience"
            r'experience\s*(?:required|needed)?[:\s]*(\d+)',  # "experience: 5"
        ]
        for pattern in year_patterns:
            match = re.search(pattern, jd_lower)
            if match:
                years = float(match.group(1))
                break
        
        # ─── 2. Extract skills from the actual JD text ───
        # Comprehensive skill keyword bank organized by category
        skill_banks = {
            "embeddings_retrieval": [
                "embeddings", "sentence-transformers", "openai", "bge", "e5",
                "word2vec", "doc2vec", "embedding drift", "dense retrieval",
                "hybrid retrieval", "semantic search", "neural retrieval"
            ],
            "vector_databases": [
                "vector databases", "pinecone", "weaviate", "qdrant", "milvus",
                "faiss", "chroma", "opensearch", "elasticsearch", "hybrid search"
            ],
            "llm_finetuning": [
                "llm", "llms", "fine-tuning", "fine tuning", "lora", "qlora",
                "peft", "rlhf", "gpt", "transformers", "huggingface",
                "prompt engineering", "langchain", "llamaindex", "rag"
            ],
            "ranking_evaluation": [
                "ranking", "learning-to-rank", "ndcg", "mrr", "map",
                "a/b testing", "evaluation", "recommendation", "re-ranking",
                "reranking", "bm25", "scoring", "relevance"
            ],
            "ml_frameworks": [
                "xgboost", "lightgbm", "catboost", "scikit-learn", "sklearn",
                "pytorch", "tensorflow", "keras", "jax"
            ],
            "programming": [
                "python", "sql", "golang", "rust", "java", "scala"
            ],
            "data_engineering": [
                "spark", "pyspark", "airflow", "kafka", "data engineering",
                "data pipelines", "etl", "dbt"
            ],
            "devops_cloud": [
                "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd",
                "mlops", "mlflow", "kubeflow", "sagemaker"
            ],
            "general_ai": [
                "machine learning", "deep learning", "neural networks",
                "nlp", "natural language processing", "computer vision",
                "data science", "feature engineering"
            ]
        }
        
        extracted_skills = []
        for category, skills in skill_banks.items():
            for skill in skills:
                # Check for the skill mention in the JD text
                if skill in jd_lower:
                    extracted_skills.append(skill)
        
        # Deduplicate while preserving order
        seen = set()
        unique_skills = []
        for s in extracted_skills:
            if s not in seen:
                seen.add(s)
                unique_skills.append(s)
        
        # If very few skills found, add defaults for AI engineering JDs
        if len(unique_skills) < 5:
            unique_skills = [
                "embeddings", "sentence-transformers", "vector databases",
                "python", "machine learning", "ranking", "evaluation",
                "llms", "fine-tuning", "faiss"
            ]
        
        # ─── 3. Extract location ───
        location = "Remote"
        location_patterns = [
            r'location[:\s]*([^\n,]+)',
            r'(?:based\s+in|located\s+in)\s+([^\n,]+)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, jd_lower)
            if match:
                location = match.group(1).strip().title()
                break
        
        # Check for known Indian cities
        indian_cities = ["pune", "noida", "hyderabad", "mumbai", "delhi", "bangalore", "chennai", "gurgaon"]
        mentioned_cities = [c.title() for c in indian_cities if c in jd_lower]
        if mentioned_cities:
            location = "/".join(mentioned_cities[:3])
        
        # ─── 4. Extract hidden behavioral traits ───
        hidden_traits = []
        trait_signals = {
            "startup-fit": ["early-stage", "startup", "founding", "series a", "series b", "scrappy"],
            "ambiguity-tolerance": ["ambiguity", "undefined", "changes every", "no prescribed"],
            "product-engineering": ["product", "ship", "shipper", "production", "real users"],
            "research-oriented": ["research", "papers", "published", "academic"],
            "async-first": ["async", "write a lot", "writing", "async-first"],
            "hands-on-coder": ["writes code", "hands-on", "production code"],
            "growth-mindset": ["learning", "evolving", "mentoring", "teaching"],
            "culture-fit": ["culture", "vibe", "disagree openly", "decide quickly"],
        }
        
        for trait, keywords in trait_signals.items():
            if any(kw in jd_lower for kw in keywords):
                hidden_traits.append(trait)
        
        # ─── 5. Detect anti-patterns (what NOT to hire) ───
        anti_patterns = []
        anti_pattern_signals = {
            "consulting-only": ["tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini", "consulting"],
            "title-chaser": ["title-chasers", "switching companies every"],
            "framework-enthusiast": ["framework enthusiasts", "langchain tutorials"],
            "pure-research": ["pure research", "academic labs", "research-only"],
            "no-recent-code": ["hasn't written production code", "architecture", "tech lead"],
            "cv-only": ["computer vision", "speech", "robotics"],
            "keyword-stuffer": ["all the AI keywords", "skill list looks", "not a fit"],
        }
        
        for pattern, keywords in anti_pattern_signals.items():
            if any(kw in jd_lower for kw in keywords):
                anti_patterns.append(pattern)
        
        # ─── 6. Detect degree requirement ───
        require_degree = True
        if any(phrase in jd_lower for phrase in [
            "degree not required", "no degree", "self-taught",
            "bootcamp", "non-traditional"
        ]):
            require_degree = False
        # The actual JD focuses on experience over degrees
        if "skills are teachable" in jd_lower or "not a requirement" in jd_lower:
            require_degree = False
        
        return {
            "skills": unique_skills,
            "years_experience": years,
            "location": location,
            "require_degree": require_degree,
            "hidden_traits": hidden_traits,
            "anti_patterns": anti_patterns,
        }

    async def run_pipeline(self, jd_text: str, custom_weights: dict[str, float] | None = None) -> dict[str, Any]:
        """
        Execute the full Recruiter Intelligence pipeline.
        Returns both ranked candidates and parsed JD for UI display.
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
        query_hash = hashlib.md5(jd_query.encode('utf-8')).hexdigest()
        
        if query_hash in retrieval_cache:
            retrieved_candidates = retrieval_cache[query_hash]
        else:
            retrieved_candidates = self.vector_store.search(query_embedding, top_k=fetch_k)
            retrieval_cache[query_hash] = retrieved_candidates
            
        logger.info(f"Retrieved top {len(retrieved_candidates)} candidates via FAISS.")

        # 4. Multi-Agent Jury Evaluation
        ranked = self.jury.rank_candidates(
            retrieved_candidates=retrieved_candidates,
            jd_skills=jd_parsed["skills"],
            jd_years=jd_parsed["years_experience"],
            jd_location=jd_parsed["location"],
            require_degree=jd_parsed.get("require_degree", False),
            custom_weights=custom_weights,
            anti_patterns=jd_parsed.get("anti_patterns", [])
        )

        # 5. Take Top K
        top_ranked = ranked[:self.settings.pipeline.top_k_results]
        
        # Clean up massive raw profiles but keep a structured dict for the UI
        for c in top_ranked:
            if "raw_profile" in c:
                c["candidate_details"] = c["raw_profile"].model_dump()
                del c["raw_profile"]

        logger.info(f"Pipeline complete. Returning {len(top_ranked)} thoroughly vetted candidates.")
        
        return {
            "ranked_candidates": top_ranked,
            "parsed_jd": jd_parsed,
            "pipeline_stats": {
                "total_indexed": self.vector_store.index.ntotal if self.vector_store.index else 0,
                "retrieved": len(retrieved_candidates),
                "scored": len(ranked),
                "returned": len(top_ranked)
            }
        }
