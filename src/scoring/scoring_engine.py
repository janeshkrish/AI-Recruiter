from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.feature_engineering.features import FeatureSet


DEFAULT_WEIGHTS = {
    "production_ml_experience": 0.25,
    "retrieval_ranking_experience": 0.20,
    "vector_databases": 0.15,
    "python_engineering": 0.10,
    "evaluation_frameworks": 0.10,
    "startup_product_mindset": 0.08,
    "behavioral_signals": 0.05,
    "career_progression": 0.03,
    "location_relocation": 0.02,
    "open_source_github": 0.02,
}


@dataclass
class ScoreCard:
    candidate_id: str
    raw_score: float
    final_score: float
    recommendation: str
    components: dict[str, float]
    weights: dict[str, float]
    penalties: dict[str, float] = field(default_factory=dict)
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


class WeightedScoringEngine:
    """Configurable normalized weighted scoring with deterministic penalties."""

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        self.weights = self._normalize_weights(weights or DEFAULT_WEIGHTS)

    def score(self, features: FeatureSet) -> ScoreCard:
        v = features.values
        components = {
            "production_ml_experience": self._production_ml(v),
            "retrieval_ranking_experience": self._retrieval_ranking(v),
            "vector_databases": self._vector_db(v),
            "python_engineering": self._python(v),
            "evaluation_frameworks": self._evaluation(v),
            "startup_product_mindset": self._startup_product(v),
            "behavioral_signals": self._behavioral(v),
            "career_progression": self._career_progression(v),
            "location_relocation": self._location(v),
            "open_source_github": self._open_source(v),
        }
        raw_score = sum(components[name] * self.weights[name] for name in self.weights)
        penalties = self._penalties(v)
        penalty_multiplier = 1.0
        for multiplier in penalties.values():
            penalty_multiplier *= multiplier
        penalty_multiplier *= v.get("honeypot_penalty", 1.0)
        final_score = max(0.0, min(1.0, raw_score * penalty_multiplier))

        strengths = [name for name, value in components.items() if value >= 0.72]
        weaknesses = [name for name, value in components.items() if value < 0.45]

        return ScoreCard(
            candidate_id=features.candidate_id,
            raw_score=raw_score,
            final_score=final_score,
            recommendation=self._recommendation(final_score),
            components={name: round(value * 100.0, 1) for name, value in components.items()},
            weights={name: round(weight * 100.0, 1) for name, weight in self.weights.items()},
            penalties=penalties,
            strengths=strengths,
            weaknesses=weaknesses,
            risks=features.risks,
        )

    def _normalize_weights(self, weights: dict[str, float]) -> dict[str, float]:
        merged = dict(DEFAULT_WEIGHTS)
        merged.update({key: value for key, value in weights.items() if key in merged})
        total = sum(merged.values())
        if total <= 0:
            return DEFAULT_WEIGHTS
        return {key: value / total for key, value in merged.items()}

    def _production_ml(self, v: dict[str, float]) -> float:
        return self._clamp(
            self._years_score(v.get("production_ai_months", 0.0), 48)
            * 0.42
            + self._term_score(v, "production_ai")
            * 0.22
            + self._years_score(v.get("ai_months", 0.0), 48)
            * 0.16
            + self._clamp(v.get("product_company_months", 0.0) / 48.0)
            * 0.10
            + v.get("senior_title_flag", 0.0)
            * 0.10
        )

    def _retrieval_ranking(self, v: dict[str, float]) -> float:
        retrieval = max(self._years_score(v.get("retrieval_months", 0.0), 36), self._term_score(v, "retrieval"))
        ranking = max(self._years_score(v.get("ranking_months", 0.0), 36), self._term_score(v, "ranking"))
        recommendation = max(self._years_score(v.get("recommendation_months", 0.0), 30), self._term_score(v, "recommendation_systems"))
        search = max(self._years_score(v.get("search_months", 0.0), 36), self._term_score(v, "search_systems"))
        embeddings = max(self._years_score(v.get("embeddings_months", 0.0), 24), self._term_score(v, "embeddings"))
        return self._clamp((retrieval * 0.28) + (ranking * 0.28) + (recommendation * 0.14) + (search * 0.16) + (embeddings * 0.14))

    def _vector_db(self, v: dict[str, float]) -> float:
        return self._clamp(
            self._years_score(v.get("vector_db_months", 0.0), 24) * 0.35
            + self._term_score(v, "vector_db") * 0.45
            + max(v.get("skill_vector_db_weighted_proficiency", 0.0), v.get("skill_vector_db_present", 0.0) * 0.55) * 0.20
        )

    def _python(self, v: dict[str, float]) -> float:
        return self._clamp(
            self._term_score(v, "python") * 0.36
            + max(v.get("skill_python_weighted_proficiency", 0.0), v.get("skill_python_present", 0.0) * 0.55) * 0.44
            + self._years_score(v.get("skill_python_months", 0.0), 36) * 0.20
        )

    def _evaluation(self, v: dict[str, float]) -> float:
        return self._clamp(
            self._years_score(v.get("evaluation_months", 0.0), 24) * 0.35
            + self._term_score(v, "evaluation_metrics") * 0.40
            + v.get("has_ab_testing", 0.0) * 0.18
            + v.get("skill_evaluation_weighted_proficiency", 0.0) * 0.07
        )

    def _startup_product(self, v: dict[str, float]) -> float:
        return self._clamp(
            self._term_score(v, "startup") * 0.25
            + self._term_score(v, "product") * 0.26
            + self._years_score(v.get("startup_months", 0.0), 24) * 0.16
            + self._years_score(v.get("product_months", 0.0), 36) * 0.18
            + self._years_score(v.get("product_company_months", 0.0), 48) * 0.15
        )

    def _behavioral(self, v: dict[str, float]) -> float:
        notice_score = 1.0 if v.get("notice_period_days", 90.0) <= 30 else 0.76 if v.get("notice_period_days", 90.0) <= 60 else 0.48 if v.get("notice_period_days", 90.0) <= 90 else 0.22
        activity_score = 1.0 if v.get("recent_activity_days", 999.0) <= 14 else 0.86 if v.get("recent_activity_days", 999.0) <= 45 else 0.62 if v.get("recent_activity_days", 999.0) <= 90 else 0.28
        return self._clamp(
            v.get("recruiter_response_rate", 0.0) * 0.24
            + activity_score * 0.18
            + v.get("open_to_work_flag", 0.0) * 0.12
            + notice_score * 0.14
            + v.get("profile_completeness", 0.0) * 0.10
            + min(v.get("saved_by_recruiters_30d", 0.0) / 8.0, 1.0) * 0.08
            + v.get("interview_completion_rate", 0.0) * 0.08
            + v.get("github_activity_score", 0.0) / 100.0 * 0.06
        )

    def _career_progression(self, v: dict[str, float]) -> float:
        tenure_score = 1.0 if v.get("avg_tenure_months", 0.0) >= 24 else 0.78 if v.get("avg_tenure_months", 0.0) >= 18 else 0.45 if v.get("avg_tenure_months", 0.0) >= 12 else 0.20
        exp_score = 1.0 if v.get("experience_in_target_band", 0.0) else self._clamp(v.get("total_years_experience", 0.0) / 7.0)
        return self._clamp(exp_score * 0.38 + tenure_score * 0.24 + v.get("senior_title_flag", 0.0) * 0.18 + min(v.get("long_tenure_role_count", 0.0) / 2.0, 1.0) * 0.10 + (1.0 - min(v.get("short_tenure_role_count", 0.0) / 3.0, 1.0)) * 0.10)

    def _location(self, v: dict[str, float]) -> float:
        return self._clamp(v.get("location_or_relocation_fit", 0.0))

    def _open_source(self, v: dict[str, float]) -> float:
        return self._clamp(
            v.get("github_activity_score", 0.0) / 100.0 * 0.58
            + v.get("github_linked_flag", 0.0) * 0.16
            + self._term_score(v, "open_source") * 0.26
        )

    def _penalties(self, v: dict[str, float]) -> dict[str, float]:
        penalties: dict[str, float] = {}
        rules = {
            "consulting_only": ("consulting_only_flag", 0.58),
            "mostly_service": ("mostly_service_flag", 0.84),
            "non_technical_title": ("non_technical_title_flag", 0.45),
            "framework_enthusiast": ("framework_enthusiast_flag", 0.62),
            "langchain_only": ("langchain_only_flag", 0.52),
            "cv_only": ("computer_vision_only_flag", 0.68),
            "speech_only": ("speech_only_flag", 0.68),
            "robotics_only": ("robotics_only_flag", 0.68),
            "research_only": ("research_only_flag", 0.60),
            "title_chaser": ("title_chaser_flag", 0.74),
            "manager_only": ("manager_only_flag", 0.64),
            "keyword_stuffer": ("keyword_stuffer_flag", 0.72),
            "no_recent_code": ("no_recent_code_flag", 0.72),
        }
        for name, (feature, multiplier) in rules.items():
            if v.get(feature, 0.0) > 0:
                penalties[name] = multiplier
        return penalties

    def _term_score(self, v: dict[str, float], prefix: str) -> float:
        profile = min(v.get(f"{prefix}_profile_term_count", 0.0) / 3.0, 1.0)
        career = min(v.get(f"{prefix}_career_term_count", 0.0) / 4.0, 1.0)
        skills = min(v.get(f"{prefix}_skill_term_count", 0.0) / 3.0, 1.0)
        all_text = min(v.get(f"{prefix}_all_term_count", 0.0) / 6.0, 1.0)
        return self._clamp(career * 0.42 + skills * 0.28 + profile * 0.18 + all_text * 0.12)

    def _years_score(self, months: float, target_months: float) -> float:
        return self._clamp(months / target_months)

    def _recommendation(self, score: float) -> str:
        if score >= 0.84:
            return "Strong Hire"
        if score >= 0.72:
            return "Hire"
        if score >= 0.56:
            return "Maybe"
        return "Reject"

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, value))
