"""
Agent 3 — Career Intelligence Agent
=====================================

Analyzes career progression, promotion velocity, company quality,
industry relevance, role evolution, and leadership growth.

Returns: career_fit_score (0–1) with sub-scores.
"""

from __future__ import annotations

from loguru import logger

from recruiter_brain.data.models import (
    CandidateProfile,
    CareerEntry,
    RoleParsedOutput,
    Seniority,
)


# Numerical ordering for seniority
SENIORITY_RANK = {
    Seniority.INTERN: 0,
    Seniority.JUNIOR: 1,
    Seniority.MID: 2,
    Seniority.SENIOR: 3,
    Seniority.STAFF: 4,
    Seniority.PRINCIPAL: 5,
    Seniority.LEAD: 4,
    Seniority.MANAGER: 5,
    Seniority.DIRECTOR: 6,
    Seniority.VP: 7,
    Seniority.C_LEVEL: 8,
}


class CareerIntelligenceAgent:
    """
    Agent 3: Evaluates career trajectory quality and relevance.

    Features computed:
    - promotion_score: How fast/far the candidate has progressed
    - career_growth_score: Quality of career growth trajectory
    - industry_match_score: Overlap with target industry
    - leadership_score: Leadership experience depth
    - stability_score: Job tenure patterns
    """

    def __init__(self) -> None:
        logger.info("CareerIntelligenceAgent initialized")

    def score(
        self,
        candidate: CandidateProfile,
        parsed_role: RoleParsedOutput,
    ) -> dict[str, float]:
        """
        Score a candidate's career trajectory.

        Args:
            candidate: The candidate profile.
            parsed_role: Parsed JD requirements.

        Returns:
            Dict with career_fit_score and sub-scores.
        """
        career = candidate.career_history

        if not career:
            return {
                "career_fit_score": 0.1,
                "promotion_score": 0.0,
                "career_growth_score": 0.0,
                "industry_match_score": 0.0,
                "leadership_score": 0.0,
                "stability_score": 0.5,
            }

        promo = self._promotion_score(career)
        growth = self._career_growth_score(career, candidate.total_experience_years)
        industry = self._industry_match_score(career, parsed_role)
        leadership = self._leadership_score(career, candidate.total_experience_years)
        stability = self._stability_score(career)

        # Weighted combination
        career_fit = (
            0.25 * promo
            + 0.20 * growth
            + 0.20 * industry
            + 0.20 * leadership
            + 0.15 * stability
        )

        return {
            "career_fit_score": round(min(1.0, max(0.0, career_fit)), 4),
            "promotion_score": round(promo, 4),
            "career_growth_score": round(growth, 4),
            "industry_match_score": round(industry, 4),
            "leadership_score": round(leadership, 4),
            "stability_score": round(stability, 4),
        }

    def score_batch(
        self,
        candidates: list[CandidateProfile],
        parsed_role: RoleParsedOutput,
    ) -> list[dict[str, float]]:
        """Score multiple candidates."""
        return [self.score(c, parsed_role) for c in candidates]

    # ------------------------------------------------------------------
    # Sub-score computations
    # ------------------------------------------------------------------

    def _promotion_score(self, career: list[CareerEntry]) -> float:
        """
        Measure career title progression.

        IC → Senior → Lead → Manager → Director → VP
        Normalized by number of roles.
        """
        if len(career) < 2:
            # Single role — score based on absolute level
            rank = SENIORITY_RANK.get(career[0].seniority_level, 2)
            return min(1.0, rank / 7.0)

        ranks = [SENIORITY_RANK.get(e.seniority_level, 2) for e in career]

        # Count promotions (rank increases)
        promotions = sum(
            1 for i in range(1, len(ranks)) if ranks[i] > ranks[i - 1]
        )
        demotions = sum(
            1 for i in range(1, len(ranks)) if ranks[i] < ranks[i - 1]
        )

        # Total level advancement
        level_gain = ranks[-1] - ranks[0]

        # Promotion rate: promotions per role transition
        transitions = len(career) - 1
        promo_rate = promotions / transitions if transitions > 0 else 0

        # Combine: rate + absolute gain, penalize demotions
        score = (
            0.4 * promo_rate
            + 0.4 * min(1.0, level_gain / 5.0)
            + 0.2 * min(1.0, ranks[-1] / 7.0)
            - 0.2 * (demotions / max(transitions, 1))
        )

        return max(0.0, min(1.0, score))

    def _career_growth_score(
        self, career: list[CareerEntry], total_years: float
    ) -> float:
        """
        Evaluate quality of career growth trajectory.

        Factors:
        - Speed of advancement relative to years of experience
        - Company tier progression (moving to better companies)
        - Increasing responsibility
        """
        if not career or total_years <= 0:
            return 0.0

        # Current seniority relative to experience
        current_rank = SENIORITY_RANK.get(
            career[-1].seniority_level, 2
        )
        # Expected rank for years of experience
        expected_rank = min(7, total_years / 3)
        advancement_rate = min(1.0, current_rank / max(expected_rank, 1))

        # Company tier progression
        tiers = [e.company_tier for e in career]
        tier_improvement = 0.5
        if len(tiers) >= 2:
            # Lower tier number = better company
            tier_change = tiers[0] - tiers[-1]  # positive = improvement
            tier_improvement = min(1.0, max(0.0, 0.5 + tier_change * 0.25))

        # Responsibility growth (leadership appearances over time)
        leadership_entries = [e for e in career if e.is_leadership]
        leadership_ratio = len(leadership_entries) / len(career)

        score = (
            0.5 * advancement_rate
            + 0.3 * tier_improvement
            + 0.2 * leadership_ratio
        )

        return max(0.0, min(1.0, score))

    def _industry_match_score(
        self, career: list[CareerEntry], parsed_role: RoleParsedOutput
    ) -> float:
        """
        Score industry relevance against JD target industry.

        Recent roles weighted more heavily.
        """
        target_industry = parsed_role.target_industry.lower().strip()
        target_domains = [d.lower().strip() for d in parsed_role.domain_expertise]

        if not target_industry and not target_domains:
            return 0.5  # No industry preference → neutral

        # Weight recent roles more
        total_weight = 0.0
        match_weight = 0.0

        for i, entry in enumerate(career):
            weight = 1.0 + i * 0.5  # More recent = higher weight
            total_weight += weight

            entry_industry = entry.industry.lower().strip()
            if (
                entry_industry == target_industry
                or entry_industry in target_domains
                or target_industry in entry_industry
                or any(d in entry_industry for d in target_domains)
            ):
                match_weight += weight

        return match_weight / total_weight if total_weight > 0 else 0.0

    def _leadership_score(
        self, career: list[CareerEntry], total_years: float
    ) -> float:
        """
        Evaluate leadership experience depth.

        Years in leadership roles / total years, with bonus for
        managing larger teams (inferred from title).
        """
        if not career:
            return 0.0

        leadership_months = sum(
            e.duration_months for e in career if e.is_leadership
        )
        total_months = max(1, sum(e.duration_months for e in career))

        leadership_ratio = leadership_months / total_months

        # Bonus for high-level leadership
        max_leadership_rank = max(
            (
                SENIORITY_RANK.get(e.seniority_level, 0)
                for e in career
                if e.is_leadership
            ),
            default=0,
        )
        level_bonus = min(1.0, max_leadership_rank / 7.0) * 0.3

        return min(1.0, leadership_ratio + level_bonus)

    def _stability_score(self, career: list[CareerEntry]) -> float:
        """
        Score job tenure stability.

        Penalize frequent short stints (<12 months).
        Reward 2-4 year tenures.
        Slight penalty for extremely long single-company tenure (>8yr)
        as it may indicate stagnation.
        """
        if not career:
            return 0.5

        durations = [e.duration_months for e in career]

        # Count short stints (<12 months, excluding internships)
        non_intern = [
            e for e in career
            if e.seniority_level != Seniority.INTERN
        ]
        short_stints = sum(
            1 for e in non_intern if e.duration_months < 12
        )
        total_roles = len(non_intern) if non_intern else 1

        short_ratio = short_stints / total_roles

        # Average tenure
        avg_tenure = sum(durations) / len(durations) if durations else 24

        # Ideal tenure: 24-48 months
        if 24 <= avg_tenure <= 48:
            tenure_score = 1.0
        elif avg_tenure < 24:
            tenure_score = avg_tenure / 24.0
        else:
            # Slight penalty for very long tenures (potential stagnation)
            tenure_score = max(0.6, 1.0 - (avg_tenure - 48) / 96)

        stability = tenure_score * (1.0 - 0.5 * short_ratio)
        return max(0.0, min(1.0, stability))
