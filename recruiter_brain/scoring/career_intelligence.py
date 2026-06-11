"""
Career Intelligence Engine
===========================

Analyzes a candidate's career history to identify promotion velocity,
leadership evolution, and career trajectory (growth vs stagnation).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class CareerIntelligence:
    """Evaluates the momentum and quality of a career trajectory."""

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except:
            return datetime.now()

    @staticmethod
    def calculate_promotion_velocity(career_history: list[Any]) -> float:
        """
        Calculates how fast a candidate gets promoted.
        Higher score (approaching 1.0) means faster upward mobility.
        """
        if not career_history or len(career_history) < 2:
            return 0.5  # Neutral for sparse data

        # Helper to get attr from dict or Pydantic model
        def _get(obj, key, default=""):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        # Sort history by start date (oldest first)
        try:
            sorted_history = sorted(
                career_history, 
                key=lambda x: CareerIntelligence._parse_date(_get(x, "start_date", "2000-01-01"))
            )
        except Exception:
            return 0.5

        promotions = 0
        total_months = 0

        # Simple heuristic: title changes within the same company are promotions
        for i in range(1, len(sorted_history)):
            prev = sorted_history[i-1]
            curr = sorted_history[i]
            
            # Same company, different title
            if str(_get(prev, "company", "")).lower() == str(_get(curr, "company", "")).lower():
                if str(_get(prev, "title", "")).lower() != str(_get(curr, "title", "")).lower():
                    promotions += 1
            
            total_months += int(_get(curr, "duration_months", 0))

        if total_months == 0:
            return 0.5

        # Promotion every ~24 months is stellar (1.0)
        # Promotion every ~48 months is good (0.75)
        # Stagnation for 8+ years is bad (0.2)
        velocity_ratio = promotions / (total_months / 12.0) if total_months > 0 else 0
        
        # Max out at 1 promotion per 1.5 years (0.66 ratio)
        normalized = min(1.0, velocity_ratio / 0.66)
        
        # Base bump for having multiple roles
        return max(0.2, min(1.0, normalized + 0.3))

    @staticmethod
    def calculate_leadership_evolution(career_history: list[Any]) -> float:
        """
        Identifies if the candidate is moving into leadership or architectural roles.
        """
        if not career_history:
            return 0.0

        def _get(obj, key, default=""):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)

        leadership_keywords = ["lead", "manager", "principal", "staff", "head", "director", "vp", "chief", "architect"]
        
        current_role = career_history[0]  # Assuming first is most recent in raw JSONL
        title = str(_get(current_role, "title", "")).lower()
        
        is_leader = any(kw in title for kw in leadership_keywords)
        if is_leader:
            return 1.0
            
        # Check past roles
        past_leadership = False
        for role in career_history[1:]:
            if any(kw in str(_get(role, "title", "")).lower() for kw in leadership_keywords):
                past_leadership = True
                break
                
        if past_leadership and not is_leader:
            return 0.4  # Stepped down from leadership
            
        return 0.2  # Individual Contributor trajectory
