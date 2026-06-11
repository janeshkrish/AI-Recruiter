"""
Dataset Preprocessor
=====================

Cleans and normalizes candidate and JD data for downstream processing.
"""

from __future__ import annotations

import re
from typing import Any

from recruiter_brain.data.models import CandidateProfile


class DatasetPreprocessor:
    """Preprocesses raw candidate text and data fields."""

    @staticmethod
    def clean_text(text: str | None) -> str:
        """Basic text cleaning."""
        if not text:
            return ""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove HTML-like tags if any exist
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()

    @staticmethod
    def normalize_skill(skill: str) -> str:
        """Normalize skill names to lowercase, stripped."""
        if not skill:
            return ""
        return skill.lower().strip()

    @staticmethod
    def map_education_tier(tier: str | None) -> float:
        """Map categorical education tier to a numerical weight (0.0 - 1.0)."""
        if not tier:
            return 0.5
            
        tier_map = {
            "tier_1": 1.0,
            "tier_2": 0.85,
            "tier_3": 0.70,
            "tier_4": 0.55,
            "unknown": 0.50
        }
        return tier_map.get(tier.lower(), 0.50)
        
    @staticmethod
    def map_skill_proficiency(prof: str | None) -> float:
        """Map skill proficiency to a numerical weight."""
        if not prof:
            return 0.5
            
        prof_map = {
            "expert": 1.0,
            "advanced": 0.8,
            "intermediate": 0.5,
            "beginner": 0.2
        }
        return prof_map.get(prof.lower(), 0.5)

    def preprocess_candidate(self, candidate: CandidateProfile) -> dict[str, Any]:
        """
        Extract a flattened, cleaned dictionary of candidate features
        suitable for embeddings and scoring.
        """
        # Clean textual fields
        clean_headline = self.clean_text(candidate.profile.headline)
        clean_summary = self.clean_text(candidate.profile.summary)
        
        # Combine recent career descriptions
        recent_career = candidate.career_history[:3] if candidate.career_history else []
        career_text = " | ".join(
            f"{c.title} at {c.company}: {self.clean_text(c.description)}"
            for c in recent_career
        )
        
        # Extract and normalize skills
        norm_skills = []
        for s in candidate.skills:
            norm_name = self.normalize_skill(s.name)
            weight = self.map_skill_proficiency(s.proficiency)
            # Boost weight slightly based on duration and endorsements (capped)
            dur_boost = min(s.duration_months / 60.0, 0.2)  # up to +0.2 for 5 yrs
            end_boost = min(s.endorsements / 50.0, 0.1)    # up to +0.1 for 50+ endorsements
            
            final_weight = min(1.0, weight + dur_boost + end_boost)
            norm_skills.append({
                "name": norm_name,
                "original": s.name,
                "weight": final_weight,
                "duration": s.duration_months
            })
            
        # Get highest education tier
        best_edu_tier = 0.0
        edu_text = ""
        for e in candidate.education:
            tier_val = self.map_education_tier(e.tier)
            if tier_val > best_edu_tier:
                best_edu_tier = tier_val
            edu_text += f"{e.degree} in {e.field_of_study} from {e.institution}. "

        # Create a single unified document for the FAISS embedding
        # This string must contain the essence of the candidate.
        embedding_doc = (
            f"[TITLE] {candidate.profile.current_title} "
            f"[SUMMARY] {clean_summary} "
            f"[SKILLS] {', '.join(s['original'] for s in norm_skills)} "
            f"[EXPERIENCE] {career_text} "
            f"[EDUCATION] {edu_text}"
        ).strip()

        return {
            "candidate_id": candidate.candidate_id,
            "name": candidate.profile.anonymized_name,
            "years_of_experience": candidate.profile.years_of_experience,
            "location": self.clean_text(candidate.profile.location),
            "normalized_skills": norm_skills,
            "best_edu_tier": best_edu_tier,
            "embedding_doc": embedding_doc,
            "raw_profile": candidate
        }

    def preprocess_batch(self, candidates: list[CandidateProfile]) -> list[dict[str, Any]]:
        """Preprocess a batch of candidates."""
        return [self.preprocess_candidate(c) for c in candidates]
