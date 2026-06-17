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
"""

from __future__ import annotations

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
    "mchp", "birlasoft",
}


class RecruiterJury:
    """Multi-Agent evaluation jury with 5 specialized agents."""

    def __init__(self):
        self.settings = get_settings()
        self.skill_graph = SkillTransferGraph()

    def _detect_anti_patterns(self, raw_profile: Any, anti_patterns: list[str]) -> tuple[float, list[str]]:
        """
        Agent E: Anti-Pattern Detection.
        Returns a penalty multiplier (0.5 to 1.0) and list of detected flags.
        """
        flags = []
        penalty = 1.0
        
        career = raw_profile.career_history
        
        if not career:
            return 1.0, []
        
        # Helper to get attr from dict or Pydantic model
        def _get(obj, key, default=""):
            if isinstance(obj, dict): return obj.get(key, default)
            return getattr(obj, key, default)
        
        # ─── 1. Consulting-only career check ───
        if "consulting-only" in anti_patterns:
            companies = [str(_get(c, "company", "")).lower() for c in career]
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
            durations = [int(_get(c, "duration_months", 24)) for c in career]
            avg_tenure = sum(durations) / len(durations) if durations else 24
            if avg_tenure < 15:
                flags.append(f"Frequent job changes (avg tenure: {avg_tenure:.0f} months)")
                penalty *= 0.7
            elif avg_tenure < 18:
                flags.append(f"Short average tenure ({avg_tenure:.0f} months)")
                penalty *= 0.85
        
        # ─── 3. Role-skill mismatch (keyword stuffer) ───
        if "keyword-stuffer" in anti_patterns:
            current_title = str(_get(raw_profile.profile, "current_title", "")).lower()
            non_technical_roles = [
                "marketing", "sales", "hr", "recruiter", "manager",
                "business analyst", "project manager", "scrum master",
                "product owner", "account manager"
            ]
            if any(role in current_title for role in non_technical_roles):
                flags.append(f"Non-technical current role: {current_title}")
                penalty *= 0.5
        
        return max(0.4, penalty), flags

    def _calculate_behavioral_score(self, raw_profile: Any) -> tuple[float, list[str]]:
        """
        Agent C: Enhanced Behavioral Intelligence using ALL 23 Redrob signals.
        Returns a score (0-100) and list of behavioral insights.
        """
        signals = raw_profile.redrob_signals
        insights = []
        
        # ─── Core Availability Signals (40% of behavioral score) ───
        # Recruiter response rate (0-1)
        response_rate = signals.recruiter_response_rate
        if response_rate > 0.8:
            insights.append(f"Highly responsive ({response_rate*100:.0f}% response rate)")
        elif response_rate < 0.2:
            insights.append(f"⚠ Very low response rate ({response_rate*100:.0f}%)")
        
        # Open to work flag (major positive signal)
        open_to_work = 1.0 if signals.open_to_work_flag else 0.3
        if signals.open_to_work_flag:
            insights.append("Actively seeking new opportunities")
        
        # Notice period (shorter is better for urgent roles)
        notice_days = signals.notice_period_days
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
        
        # ─── Engagement & Activity Signals (30% of behavioral score) ───
        # Profile completeness
        completeness = signals.profile_completeness_score
        
        # Recent activity (applications in last 30d, profile views)
        apps_30d = min(signals.applications_submitted_30d / 10.0, 1.0)  # cap at 10
        views_30d = min(signals.profile_views_received_30d / 20.0, 1.0)  # cap at 20
        saved_by_recruiters = min(signals.saved_by_recruiters_30d / 5.0, 1.0)  # cap at 5
        
        if saved_by_recruiters > 0.5:
            insights.append(f"Market-validated: saved by {signals.saved_by_recruiters_30d} recruiters recently")
        
        engagement_score = (
            completeness * 0.3 +
            apps_30d * 0.2 +
            views_30d * 0.2 +
            saved_by_recruiters * 0.3
        )
        
        # ─── Quality & Credibility Signals (20% of behavioral score) ───
        # Interview completion rate
        completion_rate = signals.interview_completion_rate
        if completion_rate > 0.8:
            insights.append("Strong interview follow-through")
        elif completion_rate < 0.3 and completion_rate > 0:
            insights.append("⚠ Low interview completion rate")
        
        # GitHub activity
        github_score = max(0, min(signals.github_activity_score / 100.0, 1.0)) if signals.github_activity_score >= 0 else 0.5
        if signals.github_activity_score > 50:
            insights.append(f"Active GitHub presence (score: {signals.github_activity_score:.0f})")
        
        # Verification signals
        verified = 0.0
        if signals.verified_email:
            verified += 0.3
        if signals.verified_phone:
            verified += 0.3
        if signals.linkedin_connected:
            verified += 0.4
            
        quality_score = (
            completion_rate * 0.35 +
            github_score * 0.35 +
            verified * 0.3
        )
        
        # ─── Network & Social Signals (10% of behavioral score) ───
        connections = min(signals.connection_count / 500.0, 1.0)  # cap at 500
        endorsements = min(signals.endorsements_received / 50.0, 1.0)  # cap at 50
        
        network_score = connections * 0.5 + endorsements * 0.5
        
        # ─── Willingness Signals ───
        relocation_bonus = 0.05 if signals.willing_to_relocate else 0.0
        
        # ─── Final Behavioral Score ───
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
        # Analyzes promotions, experience depth, and company quality
        # ---------------------------------------------------------
        velocity = CareerIntelligence.calculate_promotion_velocity(raw.career_history)
        leadership = CareerIntelligence.calculate_leadership_evolution(raw.career_history)
        exp_match = FeatureBuilder.calculate_experience_match(candidate_meta["years_of_experience"], jd_years)
        
        career_score = ((exp_match * 0.6) + (velocity * 0.3) + (leadership * 0.1)) * 100.0

        # ---------------------------------------------------------
        # AGENT C: Behavioral Intelligence Agent (Enhanced)
        # Uses ALL 23 Redrob signals
        # ---------------------------------------------------------
        behavioral_score, behavioral_insights = self._calculate_behavioral_score(raw)

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
        # AGENT E: Anti-Pattern Detection
        # ---------------------------------------------------------
        anti_penalty = 1.0
        anti_flags = []
        if anti_patterns:
            anti_penalty, anti_flags = self._detect_anti_patterns(raw, anti_patterns)

        # ---------------------------------------------------------
        # SYNTHESIS (Final Ranking)
        # ---------------------------------------------------------
        w = self.settings.weights.as_dict
        if custom_weights:
            w.update(custom_weights)
        
        # Map our agents to the weighted dimensions
        base_score = (
            (technical_score * w["skill_match"]) +
            (career_score * w["experience_match"]) +
            (behavioral_score * w.get("location_match", 0.05) * 2) +  # Behavioral gets boosted weight
            (potential_score * w["semantic_similarity"])
        )
        
        # Education is treated as a flat addition
        edu_match = FeatureBuilder.calculate_education_match(candidate_meta["best_edu_tier"], require_degree)
        final_score = base_score + (edu_match * 100.0 * w["education_match"])
        
        # Apply anti-pattern penalty
        final_score *= anti_penalty
        
        # Location match still factors in
        loc_match = FeatureBuilder.calculate_location_match(candidate_meta["location"], jd_location)
        location_score = loc_match * 100.0

        # Construct Reasonings
        reasons = []
        if adjacencies:
            reasons.append(f"Technical Agent: Transferable skills detected ({', '.join(adjacencies[:3])}).")
        if technical_score > 70:
            reasons.append(f"Technical Agent: Strong skill alignment ({technical_score:.0f}%).")
        if velocity > 0.8:
            reasons.append("Career Agent: Exceptional promotion velocity in career history.")
        if exp_match > 0.9:
            reasons.append(f"Career Agent: Experience level meets requirements ({candidate_meta['years_of_experience']:.1f}y).")
        if learning_vel > 0.8:
            reasons.append("Potential Agent: Extremely high learning velocity (rapid skill acquisition).")
        for insight in behavioral_insights[:2]:
            if not insight.startswith("⚠"):
                reasons.append(f"Behavioral Agent: {insight}.")
        for flag in anti_flags:
            reasons.append(f"⚠ Risk: {flag}.")

        if not reasons:
            reasons.append("Solid candidate matching baseline requirements.")

        return {
            "candidate_id": candidate_meta["candidate_id"],
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
            "raw_profile": raw
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
            
            score_card = self.evaluate_candidate(
                c_meta, jd_skills, jd_years, jd_location, semantic,
                require_degree, custom_weights, anti_patterns
            )
            results.append(score_card)

        # Sort descending by final score
        results.sort(key=lambda x: x["score"], reverse=True)
        return results
