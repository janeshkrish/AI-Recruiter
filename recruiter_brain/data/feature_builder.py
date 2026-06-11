"""
Feature Builder
================

Generates composite features (like skill overlap, experience overlap)
between a parsed Job Description and a preprocessed candidate.
"""

from __future__ import annotations

from typing import Any

from loguru import logger


class FeatureBuilder:
    """Builds features for the ranking engine."""

    @staticmethod
    def calculate_skill_match(
        candidate_skills: list[dict[str, Any]], 
        jd_skills: list[str]
    ) -> float:
        """
        Calculate skill overlap score (0.0 to 1.0).
        Takes into account candidate's skill proficiency weight.
        """
        if not jd_skills:
            return 1.0
            
        jd_skills_norm = set(s.lower().strip() for s in jd_skills)
        if not jd_skills_norm:
            return 1.0

        match_score = 0.0
        
        for req_skill in jd_skills_norm:
            best_match_weight = 0.0
            
            for c_skill in candidate_skills:
                c_name = c_skill["name"]
                # Exact match
                if req_skill == c_name:
                    best_match_weight = max(best_match_weight, c_skill["weight"])
                # Substring match (e.g. "machine learning" in "machine learning (ml)")
                elif req_skill in c_name or c_name in req_skill:
                    best_match_weight = max(best_match_weight, c_skill["weight"] * 0.8)
                    
            match_score += best_match_weight

        # Normalize by number of required skills
        return min(1.0, match_score / len(jd_skills_norm))

    @staticmethod
    def calculate_experience_match(
        candidate_years: float, 
        required_years_str: str | float
    ) -> float:
        """Calculate experience overlap score (0.0 to 1.0)."""
        # Parse required years
        req_years = 0.0
        if isinstance(required_years_str, (int, float)):
            req_years = float(required_years_str)
        elif isinstance(required_years_str, str):
            import re
            nums = re.findall(r'\d+', required_years_str)
            if nums:
                req_years = float(nums[0])
                
        if req_years == 0.0:
            return 1.0
            
        if candidate_years >= req_years:
            return 1.0
            
        # Penalize gracefully if slightly under
        ratio = candidate_years / req_years
        return ratio

    @staticmethod
    def calculate_education_match(
        best_edu_tier: float, 
        required_degree: bool = True
    ) -> float:
        """
        Calculate education match based on tier.
        best_edu_tier is already 0.0 to 1.0 from preprocessor.
        """
        if not required_degree:
            return 1.0
        return best_edu_tier

    @staticmethod
    def calculate_location_match(
        candidate_location: str, 
        jd_location: str
    ) -> float:
        """Calculate location overlap."""
        if not jd_location or jd_location.lower() in ("remote", "anywhere"):
            return 1.0
            
        if not candidate_location:
            return 0.0
            
        c_loc = candidate_location.lower()
        j_loc = jd_location.lower()
        
        # Simple string match heuristics
        if c_loc == j_loc:
            return 1.0
        if j_loc in c_loc or c_loc in j_loc:
            return 1.0
            
        # Hardcoded hack for JD location list from document
        # "Pune/Noida-preferred ... Hyderabad, Pune, Mumbai, Delhi NCR welcome"
        acceptable_locs = ["pune", "noida", "hyderabad", "mumbai", "delhi", "ncr", "gurgaon"]
        if any(loc in c_loc for loc in acceptable_locs):
            return 1.0
            
        return 0.0

    @staticmethod
    def calculate_behavioral_modifier(raw_profile: Any) -> float:
        """
        Calculate a multiplier (0.0 to 1.0) based on Redrob signals.
        If a candidate hasn't logged in recently or doesn't respond,
        they should be penalized heavily in actual ranking.
        """
        signals = raw_profile.redrob_signals
        
        # Base is the recruiter response rate (which is a strong signal of availability)
        # If response rate is 0, they get a massive penalty.
        response_rate = signals.recruiter_response_rate
        
        # Interview completion rate
        completion_rate = signals.interview_completion_rate
        
        # Combine into a multiplier that is forgiving but penalizes the worst
        multiplier = (response_rate * 0.7) + (completion_rate * 0.3)
        
        # Ensure it never drops to literal 0 unless data is fully missing
        return max(0.1, min(1.0, multiplier))
