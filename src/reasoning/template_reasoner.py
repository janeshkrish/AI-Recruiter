from __future__ import annotations

from src.feature_engineering.features import FeatureSet
from src.parser.candidate_profile_parser import ParsedCandidate
from src.scoring.scoring_engine import ScoreCard


class TemplateReasoningGenerator:
    """Generates non-LLM reasoning from computed evidence only."""

    def generate(self, candidate: ParsedCandidate, features: FeatureSet, scorecard: ScoreCard) -> str:
        profile = candidate.profile
        title = profile.get("current_title") or "Candidate"
        company = profile.get("current_company") or "current company not listed"
        years = features.values.get("total_years_experience", 0.0)
        core_hits = self._core_hits(scorecard)
        evidence = self.top_matching_evidence(features, scorecard)
        weaknesses = self.missing_requirements(scorecard)
        risks = scorecard.risks[:3]

        parts = [
            f"{scorecard.recommendation}: {title} at {company} with {years:.1f} yrs",
            f"{core_hits}/5 core production AI/retrieval groups are evidenced",
        ]
        if evidence:
            parts.append("evidence: " + ", ".join(evidence[:4]))
        if weaknesses:
            parts.append("missing/weak: " + ", ".join(weaknesses[:3]))
        if risks:
            parts.append("risk: " + "; ".join(risks[:2]))

        response = features.values.get("recruiter_response_rate", 0.0)
        active_days = features.values.get("recent_activity_days", 999.0)
        notice = features.values.get("notice_period_days", 90.0)
        parts.append(f"signals: response {response:.2f}, active {active_days:.0f}d ago, notice {notice:.0f}d")
        return "; ".join(parts)[:900]

    def top_matching_evidence(self, features: FeatureSet, scorecard: ScoreCard) -> list[str]:
        evidence: list[str] = []
        for key, label in (
            ("production_ai", "production AI"),
            ("retrieval", "retrieval"),
            ("ranking", "ranking"),
            ("recommendation_systems", "recommendation systems"),
            ("search_systems", "search systems"),
            ("embeddings", "embeddings"),
            ("vector_db", "vector DB"),
            ("python", "Python"),
            ("evaluation_metrics", "evaluation metrics"),
            ("startup", "startup"),
            ("product", "product"),
            ("open_source", "open source"),
        ):
            terms = features.evidence.get(key, [])
            if terms:
                evidence.append(f"{label} via {', '.join(terms[:3])}")

        for component in scorecard.strengths:
            label = component.replace("_", " ")
            if not any(label in item for item in evidence):
                evidence.append(label)
        return evidence[:8]

    def missing_requirements(self, scorecard: ScoreCard) -> list[str]:
        names = {
            "production_ml_experience": "clear production ML ownership",
            "retrieval_ranking_experience": "retrieval/ranking depth",
            "vector_databases": "vector database or hybrid search operations",
            "python_engineering": "strong Python evidence",
            "evaluation_frameworks": "ranking evaluation metrics",
            "startup_product_mindset": "startup/product shipping mindset",
            "behavioral_signals": "responsive/recent Redrob signals",
            "career_progression": "stable senior career progression",
            "location_relocation": "preferred location or relocation signal",
            "open_source_github": "external validation or GitHub signal",
        }
        return [names.get(name, name) for name in scorecard.weaknesses]

    def production_evidence(self, features: FeatureSet) -> list[str]:
        evidence = []
        for key in ("production_ai", "retrieval", "ranking", "search_systems", "recommendation_systems"):
            terms = features.evidence.get(key, [])
            if terms:
                evidence.append(f"{key.replace('_', ' ')} terms: {', '.join(terms[:4])}")
        if features.values.get("production_ai_months", 0.0) > 0:
            evidence.append(f"{features.values['production_ai_months'] / 12.0:.1f} inferred years in production AI-adjacent roles")
        return evidence or ["No explicit production ML deployment evidence found"]

    def behavioral_evidence(self, features: FeatureSet) -> list[str]:
        values = features.values
        evidence = [
            f"response rate {values.get('recruiter_response_rate', 0.0):.2f}",
            f"active {values.get('recent_activity_days', 999.0):.0f} days ago",
            f"notice {values.get('notice_period_days', 90.0):.0f} days",
        ]
        if values.get("open_to_work_flag", 0.0):
            evidence.append("open to work")
        if values.get("willing_to_relocate", 0.0):
            evidence.append("willing to relocate")
        if values.get("github_linked_flag", 0.0):
            evidence.append(f"GitHub score {values.get('github_activity_score', 0.0):.0f}")
        return evidence

    def _core_hits(self, scorecard: ScoreCard) -> int:
        return sum(
            1
            for component in (
                "production_ml_experience",
                "retrieval_ranking_experience",
                "vector_databases",
                "python_engineering",
                "evaluation_frameworks",
            )
            if scorecard.components.get(component, 0.0) >= 56.0
        )
