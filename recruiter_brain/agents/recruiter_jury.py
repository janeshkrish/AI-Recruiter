"""
Recruiter Jury Simulator
=========================

Replaces the flat ranking engine. 
Simulates 4 distinct specialized "Agents" (logic engines) that evaluate 
different dimensions of a candidate, mimicking a real hiring committee.
"""

from __future__ import annotations

from typing import Any

from loguru import logger

from recruiter_brain.config import get_settings
from recruiter_brain.data.feature_builder import FeatureBuilder
from recruiter_brain.scoring.skill_graph import SkillTransferGraph
from recruiter_brain.scoring.career_intelligence import CareerIntelligence
from recruiter_brain.scoring.potential_engine import PotentialEngine


class RecruiterJury:
    """Multi-Agent evaluation jury."""

    def __init__(self):
        self.settings = get_settings()
        self.skill_graph = SkillTransferGraph()

    def evaluate_candidate(
        self,
        candidate_meta: dict[str, Any],
        jd_skills: list[str],
        jd_years: float,
        jd_location: str,
        semantic_score: float,
        require_degree: bool = True,
        custom_weights: dict[str, float] | None = None
    ) -> dict[str, Any]:
        """
        Passes candidate through the 4-Agent Jury.
        """
        raw = candidate_meta["raw_profile"]
        
        # ---------------------------------------------------------
        # AGENT A: Technical Fit Agent
        # Uses Skill Transfer Graph and strict matching
        # ---------------------------------------------------------
        c_skill_names = [s["name"] for s in candidate_meta["normalized_skills"]]
        transfer_score, adjacencies = self.skill_graph.calculate_transferability(c_skill_names, jd_skills)
        
        # Blend strict feature builder with transfer graph
        strict_skill = FeatureBuilder.calculate_skill_match(candidate_meta["normalized_skills"], jd_skills)
        
        technical_score = max(strict_skill, transfer_score) * 100.0

        # ---------------------------------------------------------
        # AGENT B: Career Intelligence Agent
        # Analyzes promotions and experience depth
        # ---------------------------------------------------------
        velocity = CareerIntelligence.calculate_promotion_velocity(raw.career_history)
        leadership = CareerIntelligence.calculate_leadership_evolution(raw.career_history)
        exp_match = FeatureBuilder.calculate_experience_match(candidate_meta["years_of_experience"], jd_years)
        
        career_score = ((exp_match * 0.6) + (velocity * 0.3) + (leadership * 0.1)) * 100.0

        # ---------------------------------------------------------
        # AGENT C: Behavioral & Hiring Agent
        # Uses RedRob signals (response rate, location, etc)
        # ---------------------------------------------------------
        loc_match = FeatureBuilder.calculate_location_match(candidate_meta["location"], jd_location)
        redrob_penalty = FeatureBuilder.calculate_behavioral_modifier(raw)
        
        # Hiring probability is basically likelihood to accept and respond
        hiring_score = ((loc_match * 0.3) + (redrob_penalty * 0.7)) * 100.0

        # ---------------------------------------------------------
        # AGENT D: Potential Intelligence Agent
        # Analyzes Learning Velocity and semantic domain relevance
        # ---------------------------------------------------------
        learning_vel = PotentialEngine.calculate_learning_velocity(
            candidate_meta["years_of_experience"], 
            [{"proficiency": s.get("proficiency", "beginner") if isinstance(s, dict) else getattr(s, "proficiency", "beginner")} for s in raw.skills], 
            raw.certifications
        )
        
        # Semantic score acts as "Domain alignment potential"
        potential_score = ((learning_vel * 0.6) + (semantic_score * 0.4)) * 100.0

        # ---------------------------------------------------------
        # SYNTHESIS (Final Ranking)
        # ---------------------------------------------------------
        # Weighted combination mirroring the config but dynamically adjusted
        w = self.settings.weights.as_dict
        if custom_weights:
            w.update(custom_weights)
        
        # Map our 4 agents to the 5 standard weights
        base_score = (
            (technical_score * w["skill_match"]) +
            (career_score * w["experience_match"]) +
            (hiring_score * w["location_match"]) +
            (potential_score * w["semantic_similarity"])
        )
        
        # Education is treated as a flat multiplier
        edu_match = FeatureBuilder.calculate_education_match(candidate_meta["best_edu_tier"], require_degree)
        final_score = base_score + (edu_match * 100.0 * w["education_match"])
        
        # Construct Reasonings
        reasons = []
        if adjacencies:
            reasons.append(f"Technical Agent: Detected highly transferable skills ({', '.join(adjacencies[:2])}).")
        if velocity > 0.8:
            reasons.append("Career Agent: Exceptional promotion velocity detected in career history.")
        if learning_vel > 0.8:
            reasons.append("Potential Agent: Candidate exhibits extremely high learning velocity (rapid skill acquisition).")
        if redrob_penalty < 0.5:
            reasons.append(f"Behavioral Agent: High risk of non-response (Redrob penalty applied).")

        if not reasons:
            reasons.append(f"Solid candidate matching baseline requirements.")

        return {
            "candidate_id": candidate_meta["candidate_id"],
            "score": round(final_score, 2),
            "skill_match": round(technical_score, 2),
            "experience_match": round(career_score, 2),
            "semantic_similarity": round(semantic_score * 100.0, 2),
            "location_match": round(hiring_score, 2),
            "potential_score": round(potential_score, 2),
            "transferable_matches": len(adjacencies),
            "reasoning": "; ".join(reasons),
            "raw_profile": raw
        }

    def rank_candidates(
        self,
        retrieved_candidates: list[dict[str, Any]],
        jd_skills: list[str],
        jd_years: float,
        jd_location: str,
        require_degree: bool = True,
        custom_weights: dict[str, float] | None = None
    ) -> list[dict[str, Any]]:
        """Rank a batch using the Multi-Agent Jury."""
        results = []
        for item in retrieved_candidates:
            c_meta = item["metadata"]
            semantic = item["score"]
            
            score_card = self.evaluate_candidate(
                c_meta, jd_skills, jd_years, jd_location, semantic, require_degree, custom_weights
            )
            results.append(score_card)

        # Sort descending by final score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
