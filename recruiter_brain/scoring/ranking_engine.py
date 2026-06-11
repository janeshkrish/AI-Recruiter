"""
Hybrid Ranking Engine
======================

Implements the 5-dimensional scoring model defined by the requirements.
Weights:
- Skill Match: 40%
- Experience Match: 25%
- Semantic Similarity: 20%
- Education Match: 10%
- Location Match: 5%
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from recruiter_brain.config import get_settings
from recruiter_brain.data.feature_builder import FeatureBuilder


class RankingEngine:
    """Calculates the final 0-100 score for candidates."""

    def __init__(self):
        self.settings = get_settings()
        self.weights = self.settings.weights.as_dict
        
        # Verify weights sum to 1.0
        total_weight = sum(self.weights.values())
        if abs(total_weight - 1.0) > 0.01:
            logger.warning(f"Weights do not sum to 1.0! Total: {total_weight}")

    def score_candidate(
        self,
        candidate_meta: dict[str, Any],
        jd_skills: list[str],
        jd_years: float,
        jd_location: str,
        semantic_score: float,
        require_degree: bool = True
    ) -> dict[str, Any]:
        """
        Score a single candidate against the JD criteria.
        
        Args:
            candidate_meta: The dictionary produced by DatasetPreprocessor.
            jd_skills: Required skills extracted from JD.
            jd_years: Required years of experience.
            jd_location: Job location.
            semantic_score: FAISS cosine similarity score (0.0 to 1.0).
            
        Returns:
            Dictionary containing individual component scores (0-100) and the final score.
        """
        # 1. Skill Match (40%)
        skill_match_raw = FeatureBuilder.calculate_skill_match(
            candidate_meta["normalized_skills"], 
            jd_skills
        )
        skill_score = skill_match_raw * 100.0

        # 2. Experience Match (25%)
        exp_match_raw = FeatureBuilder.calculate_experience_match(
            candidate_meta["years_of_experience"], 
            jd_years
        )
        exp_score = exp_match_raw * 100.0

        # 3. Education Match (10%)
        edu_match_raw = FeatureBuilder.calculate_education_match(
            candidate_meta["best_edu_tier"],
            require_degree
        )
        edu_score = edu_match_raw * 100.0

        # 4. Semantic Similarity (20%)
        semantic_score_100 = semantic_score * 100.0

        # 5. Location Match (5%)
        loc_match_raw = FeatureBuilder.calculate_location_match(
            candidate_meta["location"], 
            jd_location
        )
        loc_score = loc_match_raw * 100.0

        # Calculate base weighted score
        base_score = (
            (skill_score * self.weights["skill_match"]) +
            (exp_score * self.weights["experience_match"]) +
            (edu_score * self.weights["education_match"]) +
            (semantic_score_100 * self.weights["semantic_similarity"]) +
            (loc_score * self.weights["location_match"])
        )

        # Apply Behavioral Penalty / Modifier
        # Redrob signals heavily impact actual ranking.
        behavior_modifier = FeatureBuilder.calculate_behavioral_modifier(candidate_meta["raw_profile"])
        
        final_score = base_score * behavior_modifier

        return {
            "candidate_id": candidate_meta["candidate_id"],
            "score": round(final_score, 2),
            "skill_match": round(skill_score, 2),
            "experience_match": round(exp_score, 2),
            "education_match": round(edu_score, 2),
            "semantic_similarity": round(semantic_score_100, 2),
            "location_match": round(loc_score, 2),
            "behavior_modifier": round(behavior_modifier, 2)
        }

    def rank_candidates(
        self,
        retrieved_candidates: list[dict[str, Any]],
        jd_skills: list[str],
        jd_years: float,
        jd_location: str,
        require_degree: bool = True
    ) -> list[dict[str, Any]]:
        """
        Score and rank a batch of retrieved candidates.
        
        Args:
            retrieved_candidates: List of dicts from FAISS search `{"metadata": {...}, "score": 0.95}`
        """
        results = []
        for item in retrieved_candidates:
            c_meta = item["metadata"]
            semantic = item["score"]
            
            score_card = self.score_candidate(
                candidate_meta=c_meta,
                jd_skills=jd_skills,
                jd_years=jd_years,
                jd_location=jd_location,
                semantic_score=semantic,
                require_degree=require_degree
            )
            # Inject raw profile for explainability later
            score_card["raw_profile"] = c_meta["raw_profile"]
            results.append(score_card)

        # Sort descending by final score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
