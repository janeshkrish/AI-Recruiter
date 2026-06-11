"""
Learning Potential Engine
==========================

Estimates how quickly a candidate acquires new skills based on 
skill density relative to their years of experience.
"""

from __future__ import annotations

from typing import Any


class PotentialEngine:
    """Predicts a candidate's learning velocity and long-term potential."""

    @staticmethod
    def calculate_learning_velocity(
        total_experience_years: float, 
        skills: list[Any], 
        certifications: list[Any]
    ) -> float:
        """
        Learning Velocity = (Complex Skills + Certs) / Years of Experience
        Rewards Junior/Mid engineers who have acquired a massive toolkit quickly.
        """
        if total_experience_years <= 0.5:
            # Prevent division by zero, assume high potential for very juniors with skills
            return min(1.0, len(skills) * 0.1)

        # Helper to get attr from dict or Pydantic model
        def _get(obj, key, default=""):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        # Count "advanced" or "expert" skills as heavy weight
        weighted_skills = 0.0
        for s in skills:
            prof = str(_get(s, "proficiency", "beginner")).lower()
            if prof == "expert":
                weighted_skills += 1.5
            elif prof == "advanced":
                weighted_skills += 1.0
            elif prof == "intermediate":
                weighted_skills += 0.5
            else:
                weighted_skills += 0.2

        # Add certification bumps
        cert_bump = len(certifications) * 0.5

        total_weight = weighted_skills + cert_bump
        
        # Velocity ratio: expecting ~2 advanced/intermediate skills per year
        expected = total_experience_years * 2.0
        
        velocity_ratio = total_weight / expected if expected > 0 else 0
        
        # Normalize to 0-1
        return min(1.0, velocity_ratio / 1.5)  # 1.5x expected rate is a 1.0 score
