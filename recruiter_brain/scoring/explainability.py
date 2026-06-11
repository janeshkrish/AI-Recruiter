"""
Explainability Engine
======================

Generates dataset-driven, recruiter-style reasoning for candidate rankings.
Does not use generic LLM hallucinated text — relies strictly on calculated features.
"""

from __future__ import annotations

from typing import Any


class ExplainabilityEngine:
    """Generates reasoning for candidate scores."""

    @staticmethod
    def generate_reasoning(score_card: dict[str, Any], jd_skills: list[str]) -> list[str]:
        """
        Generate bullet points explaining why the candidate received their score.
        """
        reasons = []
        
        # 1. Skills
        skill_score = score_card["skill_match"]
        if skill_score >= 90:
            reasons.append(f"Matches nearly all required skills (Score: {skill_score}%).")
        elif skill_score >= 70:
            reasons.append(f"Strong skill match (Score: {skill_score}%).")
        elif skill_score < 40:
            reasons.append(f"Significant skill gaps identified (Score: {skill_score}%).")

        # 2. Experience
        raw_profile = score_card["raw_profile"]
        years = raw_profile.profile.years_of_experience
        exp_score = score_card["experience_match"]
        if exp_score == 100:
            reasons.append(f"Has {years} years of experience, meeting/exceeding requirements.")
        else:
            reasons.append(f"Has {years} years of experience (Short of ideal requirements).")

        # 3. Semantic Similarity (Context/Industry match)
        sem_score = score_card["semantic_similarity"]
        if sem_score >= 85:
            reasons.append(f"High semantic similarity ({sem_score}%) indicates highly relevant past roles and industry background.")
        elif sem_score >= 70:
            reasons.append(f"Good semantic alignment ({sem_score}%) with JD responsibilities.")

        # 4. Education
        edu_score = score_card["education_match"]
        if edu_score >= 80:
            reasons.append("Top-tier educational background.")
        
        # 5. Location
        if score_card["location_match"] == 100:
            reasons.append(f"Location aligned ({raw_profile.profile.location}).")

        # 6. Behavioral Modifiers (Redrob Signals)
        modifier = score_card.get("behavior_modifier", 1.0)
        signals = raw_profile.redrob_signals
        
        if modifier < 0.5:
            reasons.append(f"WARNING: Ranked down due to low recruiter response rate ({signals.recruiter_response_rate*100:.0f}%).")
        elif signals.recruiter_response_rate > 0.8:
            reasons.append(f"Highly responsive candidate (Response rate: {signals.recruiter_response_rate*100:.0f}%).")

        return reasons
