"""
Recruiter Jury Simulator
=========================

Replaces the flat ranking engine. 
Simulates 5 distinct specialized "Agents" (logic engines) that evaluate 
different dimensions of a candidate, mimicking a real hiring committee.

Agent A: Technical Fit (Skill Transfer Graph + strict matching)
Agent B: Career Intelligence (Promotions, trajectory, company quality)
Agent C: Behavioral Intelligence (Full 23-signal Redrob analysis)
Agent D: Potential Intelligence (Learning velocity, domain alignment)
Agent E: Anti-Pattern Detection (Consulting-only, title-hopping, keyword-stuffing)

Memory-safe design: Full candidate profiles are fetched from SQLite on demand
rather than stored in memory as Pydantic models.
"""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from recruiter_brain.config import get_settings
from recruiter_brain.data.feature_builder import FeatureBuilder
from recruiter_brain.scoring.skill_graph import SkillTransferGraph
from recruiter_brain.scoring.career_intelligence import CareerIntelligence
from recruiter_brain.scoring.potential_engine import PotentialEngine


# Known large Indian IT consulting companies (anti-pattern from JD)
CONSULTING_COMPANIES = {
    "tcs", "tata consultancy", "infosys", "wipro", "accenture",
    "cognizant", "capgemini", "hcl", "tech mahindra", "mphasis",
    "mindtree", "l&t infotech", "lti", "ltimindtree", "hexaware",
    "cyient", "persistent systems", "zensar", "niit technologies",
    "birlasoft",
}


def _get(obj: Any, key: str, default: Any = "") -> Any:
    """Safely get a field from dict or Pydantic model."""
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


class RecruiterJury:
    """Multi-Agent evaluation jury with 5 specialized agents."""

    def __init__(self):
        self.settings = get_settings()
        self.skill_graph = SkillTransferGraph()
        self._sqlite_store = None  # Lazy-loaded

    def _get_sqlite_store(self):
        """Lazy-load SQLite store to avoid circular imports."""
        if self._sqlite_store is None:
            from recruiter_brain.data.sqlite_store import SQLiteStore
            self._sqlite_store = SQLiteStore()
        return self._sqlite_store

    def _fetch_full_profile(self, candidate_id: str) -> dict[str, Any] | None:
        """Fetch full candidate profile from SQLite by ID."""
        try:
            store = self._get_sqlite_store()
            return store.get_candidate_by_id(candidate_id)
        except Exception as e:
            logger.warning(f"Could not fetch profile for {candidate_id}: {e}")
            return None

    def _detect_anti_patterns(self, profile_data: dict, anti_patterns: list[str]) -> tuple[float, list[str]]:
        """
        Agent E: Anti-Pattern Detection.
        Returns a penalty multiplier (0.5 to 1.0) and list of detected flags.
        """
        flags = []
        penalty = 1.0

        career = profile_data.get("career_history", [])
        if not career:
            return 1.0, []

        # ─── 1. Consulting-only career check ───
        if "consulting-only" in anti_patterns:
            companies = [str(c.get("company", "")).lower() for c in career]
            consulting_count = sum(
                1 for c in companies
                if any(cc in c for cc in CONSULTING_COMPANIES)
            )
            if len(companies) > 0 and consulting_count == len(companies):
                flags.append("Career exclusively at large IT consulting firms")
                penalty *= 0.6
            elif consulting_count > len(companies) * 0.7:
                flags.append("Predominantly consulting-firm career")
                penalty *= 0.8

        # ─── 2. Title-hopping check (< 18 months average tenure) ───
        if "title-chaser" in anti_patterns and len(career) >= 3:
            durations = [int(c.get("duration_months", 24)) for c in career]
            avg_tenure = sum(durations) / len(durations) if durations else 24
            if avg_tenure < 15:
                flags.append(f"Frequent job changes (avg tenure: {avg_tenure:.0f} months)")
                penalty *= 0.7
            elif avg_tenure < 18:
                flags.append(f"Short average tenure ({avg_tenure:.0f} months)")
                penalty *= 0.85

        # ─── 3. Role-skill mismatch (keyword stuffer) ───
        if "keyword-stuffer" in anti_patterns:
            profile = profile_data.get("profile", {})
            current_title = str(profile.get("current_title", "")).lower()
            non_technical_roles = [
                "marketing", "sales", "hr", "recruiter", "manager",
                "business analyst", "project manager", "scrum master",
                "product owner", "account manager"
            ]
            if any(role in current_title for role in non_technical_roles):
                flags.append(f"Non-technical current role: {current_title}")
                penalty *= 0.5

        return max(0.4, penalty), flags

    def _calculate_behavioral_score(self, signals: dict) -> tuple[float, list[str]]:
        """
        Agent C: Enhanced Behavioral Intelligence using ALL 23 Redrob signals.
        Returns a score (0-100) and list of behavioral insights.
        """
        if not signals:
            return 50.0, []

        insights = []

        # ─── Core Availability Signals (40%) ───
        response_rate = float(signals.get("recruiter_response_rate", 0.5))
        if response_rate > 0.8:
            insights.append(f"Highly responsive ({response_rate*100:.0f}% response rate)")
        elif response_rate < 0.2:
            insights.append(f"⚠ Very low response rate ({response_rate*100:.0f}%)")

        open_to_work = 1.0 if signals.get("open_to_work_flag", False) else 0.3
        if signals.get("open_to_work_flag", False):
            insights.append("Actively seeking new opportunities")

        notice_days = int(signals.get("notice_period_days", 60))
        if notice_days <= 30:
            notice_score = 1.0
            insights.append(f"Short notice period ({notice_days} days)")
        elif notice_days <= 60:
            notice_score = 0.7
        elif notice_days <= 90:
            notice_score = 0.4
        else:
            notice_score = 0.2
            insights.append(f"⚠ Long notice period ({notice_days} days)")

        availability_score = (
            response_rate * 0.4 +
            open_to_work * 0.35 +
            notice_score * 0.25
        )

        # ─── Engagement & Activity Signals (30%) ───
        completeness = float(signals.get("profile_completeness_score", 0.5))
        apps_30d = min(float(signals.get("applications_submitted_30d", 0)) / 10.0, 1.0)
        views_30d = min(float(signals.get("profile_views_received_30d", 0)) / 20.0, 1.0)
        saved_by = float(signals.get("saved_by_recruiters_30d", 0))
        saved_score = min(saved_by / 5.0, 1.0)

        if saved_by >= 2:
            insights.append(f"Market-validated: saved by {saved_by:.0f} recruiters recently")

        engagement_score = (
            completeness * 0.3 +
            apps_30d * 0.2 +
            views_30d * 0.2 +
            saved_score * 0.3
        )

        # ─── Quality & Credibility Signals (20%) ───
        completion_rate = float(signals.get("interview_completion_rate", 0.5))
        if completion_rate > 0.8:
            insights.append("Strong interview follow-through")
        elif completion_rate < 0.3:
            insights.append("⚠ Low interview completion rate")

        github_raw = float(signals.get("github_activity_score", -1))
        github_score = max(0, min(github_raw / 100.0, 1.0)) if github_raw >= 0 else 0.5
        if github_raw > 50:
            insights.append(f"Active GitHub presence (score: {github_raw:.0f})")

        verified = (
            (0.3 if signals.get("verified_email", False) else 0.0) +
            (0.3 if signals.get("verified_phone", False) else 0.0) +
            (0.4 if signals.get("linkedin_connected", False) else 0.0)
        )

        quality_score = (
            completion_rate * 0.35 +
            github_score * 0.35 +
            verified * 0.3
        )

        # ─── Network Signals (10%) ───
        connections = min(float(signals.get("connection_count", 0)) / 500.0, 1.0)
        endorsements = min(float(signals.get("endorsements_received", 0)) / 50.0, 1.0)
        network_score = connections * 0.5 + endorsements * 0.5

        # Relocation bonus
        relocation_bonus = 0.05 if signals.get("willing_to_relocate", False) else 0.0

        behavioral_score = (
            availability_score * 0.40 +
            engagement_score * 0.30 +
            quality_score * 0.20 +
            network_score * 0.10 +
            relocation_bonus
        ) * 100.0

        return min(100.0, behavioral_score), insights

    def evaluate_candidate(
        self,
        candidate_meta: dict[str, Any],
        jd_skills: list[str],
        jd_years: float,
        jd_location: str,
        semantic_score: float,
        require_degree: bool = True,
        custom_weights: dict[str, float] | None = None,
        anti_patterns: list[str] | None = None
    ) -> dict[str, Any]:
        """
        Passes candidate through the 5-Agent Jury.
        Fetches full profile from SQLite — only lightweight meta is in FAISS.
        """
        candidate_id = candidate_meta["candidate_id"]

        # Fetch full profile from SQLite
        profile_data = self._fetch_full_profile(candidate_id) or {}

        # ---------------------------------------------------------
        # AGENT A: Technical Fit Agent
        # ---------------------------------------------------------
        c_skill_names = [s["name"] for s in candidate_meta.get("normalized_skills", [])]
        transfer_score, adjacencies = self.skill_graph.calculate_transferability(c_skill_names, jd_skills)
        strict_skill = FeatureBuilder.calculate_skill_match(candidate_meta.get("normalized_skills", []), jd_skills)
        technical_score = max(strict_skill, transfer_score) * 100.0

        # ---------------------------------------------------------
        # AGENT B: Career Intelligence Agent
        # ---------------------------------------------------------
        career_history = profile_data.get("career_history", [])
        velocity = CareerIntelligence.calculate_promotion_velocity(career_history)
        leadership = CareerIntelligence.calculate_leadership_evolution(career_history)
        exp_match = FeatureBuilder.calculate_experience_match(
            candidate_meta.get("years_of_experience", 0), jd_years
        )
        career_score = ((exp_match * 0.6) + (velocity * 0.3) + (leadership * 0.1)) * 100.0

        # ---------------------------------------------------------
        # AGENT C: Behavioral Intelligence Agent (23 Signals)
        # ---------------------------------------------------------
        signals = profile_data.get("redrob_signals", {})
        behavioral_score, behavioral_insights = self._calculate_behavioral_score(signals)

        # ---------------------------------------------------------
        # AGENT D: Potential Intelligence Agent
        # ---------------------------------------------------------
        raw_skills = profile_data.get("skills", [])
        skill_dicts = [{"proficiency": s.get("proficiency", "beginner") if isinstance(s, dict) else "beginner"} for s in raw_skills]
        certifications = profile_data.get("certifications", [])

        learning_vel = PotentialEngine.calculate_learning_velocity(
            candidate_meta.get("years_of_experience", 0),
            skill_dicts,
            certifications
        )
        potential_score = ((learning_vel * 0.6) + (semantic_score * 0.4)) * 100.0

        # ---------------------------------------------------------
        # AGENT E: Anti-Pattern Detection
        # ---------------------------------------------------------
        anti_penalty = 1.0
        anti_flags = []
        if anti_patterns:
            anti_penalty, anti_flags = self._detect_anti_patterns(profile_data, anti_patterns)

        # ---------------------------------------------------------
        # SYNTHESIS (Final Ranking)
        # ---------------------------------------------------------
        w = self.settings.weights.as_dict
        if custom_weights:
            w.update(custom_weights)

        base_score = (
            (technical_score * w["skill_match"]) +
            (career_score * w["experience_match"]) +
            (behavioral_score * 0.10) +
            (potential_score * w["semantic_similarity"])
        )

        edu_tier = candidate_meta.get("best_edu_tier", 0.5)
        edu_match = FeatureBuilder.calculate_education_match(edu_tier, require_degree)
        final_score = base_score + (edu_match * 100.0 * w["education_match"])
        final_score *= anti_penalty

        loc_match = FeatureBuilder.calculate_location_match(
            candidate_meta.get("location", ""), jd_location
        )
        location_score = loc_match * 100.0

        # Build reasoning
        reasons = []
        if adjacencies:
            reasons.append(f"Technical Agent: Transferable skills ({', '.join(adjacencies[:3])}).")
        if technical_score > 70:
            reasons.append(f"Technical Agent: Strong alignment ({technical_score:.0f}%).")
        if velocity > 0.8:
            reasons.append("Career Agent: Exceptional promotion velocity.")
        if exp_match > 0.9:
            reasons.append(f"Career Agent: Experience meets requirements ({candidate_meta.get('years_of_experience', 0):.1f}y).")
        if learning_vel > 0.8:
            reasons.append("Potential Agent: High learning velocity.")
        for insight in behavioral_insights[:2]:
            if not insight.startswith("⚠"):
                reasons.append(f"Behavioral Agent: {insight}.")
        for flag in anti_flags:
            reasons.append(f"⚠ Risk: {flag}.")

        if not reasons:
            reasons.append("Solid candidate matching baseline requirements.")

        # Build candidate_details for the UI (lightweight, from profile_data)
        candidate_details = {
            "profile": profile_data.get("profile", {}),
            "skills": profile_data.get("skills", []),
            "career_history": career_history,
            "education": profile_data.get("education", []),
            "certifications": certifications,
            "redrob_signals": signals,
            "normalized_skills": candidate_meta.get("normalized_skills", []),
        }

        return {
            "candidate_id": candidate_id,
            "score": round(final_score, 2),
            "skill_match": round(technical_score, 2),
            "experience_match": round(career_score, 2),
            "semantic_similarity": round(semantic_score * 100.0, 2),
            "location_match": round(location_score, 2),
            "potential_score": round(potential_score, 2),
            "behavioral_score": round(behavioral_score, 2),
            "transferable_matches": len(adjacencies),
            "reasoning": "; ".join(reasons),
            "behavioral_insights": behavioral_insights,
            "anti_pattern_flags": anti_flags,
            "anti_pattern_penalty": round(anti_penalty, 2),
            "candidate_details": candidate_details,
        }

    def rank_candidates(
        self,
        retrieved_candidates: list[dict[str, Any]],
        jd_skills: list[str],
        jd_years: float,
        jd_location: str,
        require_degree: bool = True,
        custom_weights: dict[str, float] | None = None,
        anti_patterns: list[str] | None = None
    ) -> list[dict[str, Any]]:
        """Rank a batch using the Multi-Agent Jury."""
        results = []
        for item in retrieved_candidates:
            c_meta = item["metadata"]
            semantic = item["score"]

            try:
                score_card = self.evaluate_candidate(
                    c_meta, jd_skills, jd_years, jd_location, semantic,
                    require_degree, custom_weights, anti_patterns
                )
                results.append(score_card)
            except Exception as e:
                logger.warning(f"Scoring failed for {c_meta.get('candidate_id', '?')}: {e}")

        results.sort(key=lambda x: x["score"], reverse=True)
        return results
