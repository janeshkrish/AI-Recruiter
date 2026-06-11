"""
Explainability Engine
======================

Generates recruiter-friendly explanations for shortlisted candidates.

For each candidate:
- Why they matched
- Strengths
- Risks
- Missing skills
- Growth potential
"""

from __future__ import annotations

from loguru import logger

from recruiter_brain.agents.potential_agent import PotentialIntelligenceAgent
from recruiter_brain.data.models import (
    AgentScores,
    CandidateProfile,
    Explanation,
    RoleParsedOutput,
)


class ExplainabilityEngine:
    """
    Generates human-readable explanations for candidate rankings.

    Uses agent sub-scores and skill graph paths to produce
    recruiter-friendly insights.
    """

    def __init__(
        self, potential_agent: PotentialIntelligenceAgent | None = None
    ) -> None:
        self._potential_agent = potential_agent or PotentialIntelligenceAgent()
        logger.info("ExplainabilityEngine initialized")

    def explain(
        self,
        candidate: CandidateProfile,
        scores: AgentScores,
        parsed_role: RoleParsedOutput,
    ) -> Explanation:
        """
        Generate a comprehensive explanation for a ranked candidate.

        Args:
            candidate: The candidate profile.
            scores: Agent scores for this candidate.
            parsed_role: Parsed JD requirements.

        Returns:
            Explanation with strengths, risks, missing skills, etc.
        """
        strengths = self._identify_strengths(candidate, scores, parsed_role)
        risks = self._identify_risks(candidate, scores, parsed_role)
        missing = self._find_missing_skills(candidate, parsed_role)
        growth = self._assess_growth_potential(candidate, scores, parsed_role)
        why = self._generate_match_reason(candidate, scores, parsed_role)

        # Confidence based on score agreement
        score_values = [
            scores.technical_fit_score,
            scores.career_fit_score,
            scores.behavioral_fit_score,
            scores.potential_score,
        ]
        if scores.recruiter_reasoning_score > 0:
            score_values.append(scores.recruiter_reasoning_score)

        # Higher agreement = higher confidence
        import numpy as np
        std = float(np.std(score_values))
        confidence = max(0.3, 1.0 - std * 2)

        return Explanation(
            candidate_id=candidate.candidate_id,
            candidate_name=candidate.name,
            why_matched=why,
            strengths=strengths,
            risks=risks,
            missing_skills=missing,
            growth_potential=growth,
            recruiter_notes=scores.recruiter_reasoning_text,
            confidence=round(confidence, 2),
        )

    def explain_batch(
        self,
        candidates: list[CandidateProfile],
        scores_list: list[AgentScores],
        parsed_role: RoleParsedOutput,
    ) -> list[Explanation]:
        """Generate explanations for multiple candidates."""
        return [
            self.explain(c, s, parsed_role)
            for c, s in zip(candidates, scores_list)
        ]

    def _generate_match_reason(
        self,
        candidate: CandidateProfile,
        scores: AgentScores,
        parsed_role: RoleParsedOutput,
    ) -> str:
        """Generate a concise match summary."""
        parts = []

        # Technical match
        if scores.technical_fit_score >= 0.7:
            matching_skills = self._get_matching_skills(candidate, parsed_role)
            if matching_skills:
                parts.append(
                    f"Strong technical alignment with {len(matching_skills)} "
                    f"matching skills ({', '.join(matching_skills[:5])})"
                )
        elif scores.technical_fit_score >= 0.4:
            parts.append("Moderate technical fit with relevant experience")

        # Career match
        if scores.career_fit_score >= 0.7:
            parts.append(
                f"Impressive career trajectory with "
                f"{candidate.total_experience_years:.0f} years experience"
            )

        # Potential
        if scores.potential_score >= 0.7:
            parts.append("High potential through adjacent skill expertise")

        # Behavioral
        if scores.behavioral_fit_score >= 0.7:
            parts.append("Highly engaged candidate with strong platform signals")

        if not parts:
            parts.append(
                f"Candidate shows overall fit based on combined assessment "
                f"across technical, career, and behavioral dimensions"
            )

        return ". ".join(parts) + "."

    def _identify_strengths(
        self,
        candidate: CandidateProfile,
        scores: AgentScores,
        parsed_role: RoleParsedOutput,
    ) -> list[str]:
        """Identify top strengths from sub-scores."""
        strengths = []

        # Technical strengths
        if scores.cosine_similarity >= 0.7:
            strengths.append(
                f"High semantic similarity to job requirements "
                f"({scores.cosine_similarity:.0%})"
            )
        if scores.skill_overlap >= 0.5:
            matching = self._get_matching_skills(candidate, parsed_role)
            strengths.append(
                f"Direct skill match: {', '.join(matching[:5])}"
            )

        # Career strengths
        if scores.promotion_score >= 0.7:
            strengths.append("Rapid career progression with consistent promotions")
        if scores.leadership_score >= 0.6:
            strengths.append("Proven leadership experience")
        if scores.stability_score >= 0.7:
            strengths.append("Strong tenure stability — committed team player")

        # Company quality
        top_companies = [
            e.company for e in candidate.career_history
            if e.company_tier == 1
        ]
        if top_companies:
            strengths.append(
                f"Experience at top-tier companies: {', '.join(set(top_companies[:3]))}"
            )

        # Education
        top_edu = [
            e for e in candidate.education
            if e.tier == 1
        ]
        if top_edu:
            strengths.append(
                f"{top_edu[0].degree} from {top_edu[0].institution}"
            )

        # Certifications
        if candidate.certifications:
            cert_names = [c.name for c in candidate.certifications[:3]]
            strengths.append(f"Certified: {', '.join(cert_names)}")

        # Behavioral
        bs = candidate.behavioral_signals
        if bs.recruiter_response_rate >= 0.8:
            strengths.append("Highly responsive to recruiters")
        if bs.profile_completeness >= 0.9:
            strengths.append("Comprehensive profile — detail-oriented")

        return strengths[:8]  # Cap at 8 strengths

    def _identify_risks(
        self,
        candidate: CandidateProfile,
        scores: AgentScores,
        parsed_role: RoleParsedOutput,
    ) -> list[str]:
        """Identify potential risks or concerns."""
        risks = []

        # Technical gaps
        if scores.technical_fit_score < 0.4:
            risks.append("Significant gaps in required technical skills")
        if scores.skill_overlap < 0.2:
            risks.append("Low direct skill overlap with job requirements")

        # Career concerns
        if scores.stability_score < 0.3:
            short_stints = sum(
                1 for e in candidate.career_history
                if e.duration_months < 12
                and e.seniority_level != "intern"
            )
            if short_stints > 0:
                risks.append(
                    f"Job-hopping concern: {short_stints} positions under 1 year"
                )

        if scores.career_growth_score < 0.3:
            risks.append("Limited career progression — potential growth plateau")

        # Industry mismatch
        if scores.industry_match_score < 0.2:
            risks.append("No prior experience in the target industry")

        # Behavioral red flags
        bs = candidate.behavioral_signals
        if bs.recruiter_response_rate < 0.3:
            risks.append("Low recruiter response rate — may be hard to engage")
        if bs.offer_acceptance_rate < 0.3:
            risks.append("History of declining offers — retention risk")
        if bs.last_active_days_ago > 90:
            risks.append(
                f"Inactive for {bs.last_active_days_ago} days — may not be looking"
            )

        # Experience level mismatch
        target_seniority = parsed_role.seniority.lower()
        if target_seniority in ("senior", "staff", "principal"):
            if candidate.total_experience_years < 4:
                risks.append(
                    f"Only {candidate.total_experience_years:.0f} years experience "
                    f"for a {target_seniority}-level role"
                )

        return risks[:6]  # Cap at 6 risks

    def _find_missing_skills(
        self,
        candidate: CandidateProfile,
        parsed_role: RoleParsedOutput,
    ) -> list[str]:
        """Find required skills the candidate is missing."""
        cand_skills_lower = {s.lower().strip() for s in candidate.skills}
        missing = []

        for skill in parsed_role.must_have_skills:
            skill_lower = skill.lower().strip()
            # Check exact and fuzzy match
            if skill_lower not in cand_skills_lower:
                has_fuzzy = any(
                    skill_lower in cs or cs in skill_lower
                    for cs in cand_skills_lower
                )
                if not has_fuzzy:
                    missing.append(skill)

        return missing

    def _assess_growth_potential(
        self,
        candidate: CandidateProfile,
        scores: AgentScores,
        parsed_role: RoleParsedOutput,
    ) -> str:
        """Assess and describe growth potential."""
        parts = []

        # Adjacent skills
        if scores.adjacent_skill_strength >= 0.7:
            parts.append(
                "Strong adjacent skill base suggesting rapid skill acquisition"
            )
        elif scores.adjacent_skill_strength >= 0.4:
            parts.append(
                "Moderate adjacent expertise — could bridge skill gaps "
                "with mentorship"
            )

        # Find specific skill transfer paths
        missing = self._find_missing_skills(candidate, parsed_role)
        if missing and self._potential_agent:
            for missing_skill in missing[:3]:
                for cand_skill in candidate.skills[:10]:
                    paths = self._potential_agent.get_skill_paths(
                        cand_skill, missing_skill
                    )
                    if paths:
                        path_str = " → ".join(paths[0])
                        parts.append(
                            f"Transfer path: {path_str}"
                        )
                        break

        # Learning indicators
        if candidate.certifications:
            recent_certs = [
                c for c in candidate.certifications if c.year >= 2023
            ]
            if recent_certs:
                parts.append(
                    f"Active learner: {len(recent_certs)} recent certifications"
                )

        # Career growth rate
        if scores.career_growth_score >= 0.7:
            parts.append(
                "Demonstrated ability to grow rapidly into new responsibilities"
            )

        if not parts:
            parts.append("Standard growth trajectory with no exceptional indicators")

        return " | ".join(parts)

    def _get_matching_skills(
        self,
        candidate: CandidateProfile,
        parsed_role: RoleParsedOutput,
    ) -> list[str]:
        """Get skills that match between candidate and JD."""
        cand_skills_lower = {s.lower().strip(): s for s in candidate.skills}
        matching = []

        all_required = (
            parsed_role.must_have_skills + parsed_role.nice_to_have_skills
        )
        for skill in all_required:
            skill_lower = skill.lower().strip()
            if skill_lower in cand_skills_lower:
                matching.append(skill)
            else:
                # Fuzzy match
                for cs_lower, cs_orig in cand_skills_lower.items():
                    if skill_lower in cs_lower or cs_lower in skill_lower:
                        matching.append(cs_orig)
                        break

        return matching
