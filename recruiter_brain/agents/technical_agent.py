"""
Agent 2 — Technical Capability Agent
======================================

Generates candidate and JD embeddings using BAAI/bge-large-en-v1.5,
then scores candidates on technical fit via cosine similarity,
semantic skill overlap, and exact skill overlap.

Returns: technical_fit_score (0–1)
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from loguru import logger

from recruiter_brain.data.models import CandidateProfile, RoleParsedOutput


class TechnicalCapabilityAgent:
    """
    Agent 2: Scores technical fit between candidates and job requirements.

    Uses:
    - Cosine similarity of unified embeddings (50%)
    - Semantic skill overlap via per-skill embeddings (30%)
    - Exact/fuzzy skill overlap via Jaccard distance (20%)
    """

    def __init__(self, embedding_service=None) -> None:
        """
        Args:
            embedding_service: An EmbeddingService instance. If None,
                one will be created on first use.
        """
        self._embedding_service = embedding_service
        self._jd_embedding: Optional[np.ndarray] = None
        self._jd_skill_embeddings: Optional[np.ndarray] = None
        self._jd_skills: list[str] = []
        logger.info("TechnicalCapabilityAgent initialized")

    @property
    def embedding_service(self):
        if self._embedding_service is None:
            from recruiter_brain.embeddings.embedding_service import EmbeddingService
            self._embedding_service = EmbeddingService()
        return self._embedding_service

    def prepare_jd(
        self, jd_text: str, parsed_role: RoleParsedOutput
    ) -> None:
        """
        Pre-compute JD embeddings for reuse across candidates.

        Args:
            jd_text: Raw job description text.
            parsed_role: Parsed role requirements from Agent 1.
        """
        logger.info("Computing JD embeddings...")
        self._jd_embedding = self.embedding_service.encode([jd_text])[0]

        # Embed individual skills for semantic overlap
        all_skills = parsed_role.must_have_skills + parsed_role.nice_to_have_skills
        self._jd_skills = all_skills
        if all_skills:
            self._jd_skill_embeddings = self.embedding_service.encode(all_skills)
        else:
            self._jd_skill_embeddings = np.array([])

        logger.info(
            f"JD prepared: {len(all_skills)} skills embedded, "
            f"embedding dim={self._jd_embedding.shape[0]}"
        )

    def score_candidate(
        self,
        candidate: CandidateProfile,
        candidate_embedding: Optional[np.ndarray] = None,
    ) -> dict[str, float]:
        """
        Score a single candidate's technical fit.

        Args:
            candidate: The candidate profile.
            candidate_embedding: Pre-computed embedding (optional).

        Returns:
            Dict with technical_fit_score and sub-scores.
        """
        if self._jd_embedding is None:
            raise RuntimeError("Call prepare_jd() before scoring candidates")

        # --- 1. Cosine Similarity (unified text) ---
        if candidate_embedding is None:
            candidate_embedding = self.embedding_service.encode(
                [candidate.unified_text]
            )[0]

        cosine_sim = self._cosine_similarity(
            candidate_embedding, self._jd_embedding
        )
        # Normalize from [-1,1] to [0,1]
        cosine_score = (cosine_sim + 1.0) / 2.0

        # --- 2. Semantic Skill Overlap ---
        semantic_overlap = self._compute_semantic_overlap(candidate)

        # --- 3. Exact Skill Overlap (Jaccard-like) ---
        skill_overlap = self._compute_skill_overlap(candidate)

        # --- Weighted combination ---
        technical_fit = (
            0.50 * cosine_score
            + 0.30 * semantic_overlap
            + 0.20 * skill_overlap
        )

        return {
            "technical_fit_score": round(float(np.clip(technical_fit, 0, 1)), 4),
            "cosine_similarity": round(float(cosine_score), 4),
            "semantic_overlap": round(float(semantic_overlap), 4),
            "skill_overlap": round(float(skill_overlap), 4),
        }

    def score_batch(
        self,
        candidates: list[CandidateProfile],
        embeddings: Optional[np.ndarray] = None,
    ) -> list[dict[str, float]]:
        """
        Score multiple candidates efficiently.

        Args:
            candidates: List of candidate profiles.
            embeddings: Pre-computed embeddings matrix (N x dim).

        Returns:
            List of score dicts.
        """
        if embeddings is None:
            texts = [c.unified_text for c in candidates]
            embeddings = self.embedding_service.encode(texts)

        results = []
        for i, candidate in enumerate(candidates):
            emb = embeddings[i] if embeddings is not None else None
            scores = self.score_candidate(candidate, emb)
            results.append(scores)

        return results

    def _compute_semantic_overlap(self, candidate: CandidateProfile) -> float:
        """
        Compute semantic overlap between candidate skills and JD skills.

        For each JD skill, find the maximum cosine similarity with any
        candidate skill embedding. Average across all JD skills.
        """
        if (
            self._jd_skill_embeddings is None
            or len(self._jd_skill_embeddings) == 0
            or not candidate.skills
        ):
            return 0.0

        # Embed candidate skills
        cand_skill_embeddings = self.embedding_service.encode(candidate.skills)

        # For each JD skill, find best match among candidate skills
        similarities = []
        for jd_skill_emb in self._jd_skill_embeddings:
            # Cosine similarity with all candidate skills
            sims = np.dot(cand_skill_embeddings, jd_skill_emb) / (
                np.linalg.norm(cand_skill_embeddings, axis=1)
                * np.linalg.norm(jd_skill_emb)
                + 1e-8
            )
            best_sim = float(np.max(sims))
            # Normalize to [0,1]
            similarities.append((best_sim + 1.0) / 2.0)

        return float(np.mean(similarities)) if similarities else 0.0

    def _compute_skill_overlap(self, candidate: CandidateProfile) -> float:
        """
        Compute fuzzy Jaccard overlap between candidate and JD skills.

        Uses case-insensitive substring matching for flexibility.
        """
        if not self._jd_skills or not candidate.skills:
            return 0.0

        cand_skills_lower = {s.lower().strip() for s in candidate.skills}
        jd_skills_lower = {s.lower().strip() for s in self._jd_skills}

        # Exact matches
        exact_matches = cand_skills_lower & jd_skills_lower

        # Fuzzy matches (substring containment)
        fuzzy_matches = set()
        for jd_skill in jd_skills_lower:
            for cand_skill in cand_skills_lower:
                if (
                    jd_skill in cand_skill
                    or cand_skill in jd_skill
                ) and jd_skill not in exact_matches:
                    fuzzy_matches.add(jd_skill)
                    break

        total_matches = len(exact_matches) + 0.5 * len(fuzzy_matches)
        # Jaccard-like: matches / union
        union_size = len(cand_skills_lower | jd_skills_lower)
        return float(total_matches / union_size) if union_size > 0 else 0.0

    @staticmethod
    def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
