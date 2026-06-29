from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Iterator

from src.feature_engineering.features import FeatureEngineer
from src.parser.candidate_profile_parser import CandidateProfileParser, ParsedCandidate
from src.parser.jd_analyzer import DEFAULT_REDROB_JD, JDAnalyzer
from src.reasoning.template_reasoner import TemplateReasoningGenerator
from src.scoring.scoring_engine import WeightedScoringEngine


class OfflineRanker:
    """End-to-end deterministic offline ranking pipeline."""

    def __init__(self, jd_text: str | None = None, weights: dict[str, float] | None = None) -> None:
        self.jd_analyzer = JDAnalyzer()
        self.jd = self.jd_analyzer.analyze(jd_text or DEFAULT_REDROB_JD)
        self.parser = CandidateProfileParser()
        self.feature_engineer = FeatureEngineer()
        self.scorer = WeightedScoringEngine(weights=weights)
        self.reasoner = TemplateReasoningGenerator()

    def rank_jsonl(self, candidates_path: str | Path, top_n: int = 100) -> list[dict[str, Any]]:
        candidates = self.parser.parse_jsonl(candidates_path)
        return self.rank_candidates(candidates, top_n=top_n)

    def rank_records(self, records: Iterable[dict[str, Any]], top_n: int = 100) -> list[dict[str, Any]]:
        return self.rank_candidates(self.parser.parse_records(iter(records)), top_n=top_n)

    def rank_candidates(self, candidates: Iterable[ParsedCandidate], top_n: int = 100) -> list[dict[str, Any]]:
        scored: list[dict[str, Any]] = []
        for candidate in candidates:
            if not candidate.candidate_id:
                continue
            features = self.feature_engineer.transform(candidate, self.jd)
            scorecard = self.scorer.score(features)
            reasoning = self.reasoner.generate(candidate, features, scorecard)
            row = self._row(candidate, features, scorecard, reasoning)
            scored.append(row)

        scored.sort(key=lambda row: (-round(float(row["score"]), 4), str(row["candidate_id"])))
        top = scored[:top_n]
        for rank, row in enumerate(top, start=1):
            row["rank"] = rank
        return top

    def write_submission_csv(self, rows: list[dict[str, Any]], output_path: str | Path) -> None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["candidate_id", "rank", "score", "reasoning"])
            writer.writeheader()
            for row in rows:
                writer.writerow(
                    {
                        "candidate_id": row["candidate_id"],
                        "rank": row["rank"],
                        "score": f"{float(row['score']):.4f}",
                        "reasoning": row["reasoning"],
                    }
                )

    def jd_dict(self) -> dict[str, Any]:
        return self.jd_analyzer.to_dict(self.jd)

    def _row(self, candidate: ParsedCandidate, features, scorecard, reasoning: str) -> dict[str, Any]:
        profile = candidate.profile
        values = features.values
        top_matching_evidence = self.reasoner.top_matching_evidence(features, scorecard)
        missing_requirements = self.reasoner.missing_requirements(scorecard)
        production_evidence = self.reasoner.production_evidence(features)
        behavioral_evidence = self.reasoner.behavioral_evidence(features)
        anti_flags = [risk for risk in scorecard.risks if "no major" not in risk.lower()]

        return {
            "candidate_id": candidate.candidate_id,
            "rank": 0,
            "score": round(scorecard.final_score, 4),
            "reasoning": reasoning,
            "candidate": {
                "name": profile.get("anonymized_name", ""),
                "current_title": profile.get("current_title", ""),
                "years_of_experience": values.get("total_years_experience", 0.0),
                "location": profile.get("location", ""),
                "current_company": profile.get("current_company", ""),
                "core_hits": self.reasoner._core_hits(scorecard),
            },
            "overall_score": round(scorecard.final_score * 100.0, 1),
            "hiring_recommendation": scorecard.recommendation,
            "top_matching_evidence": top_matching_evidence,
            "missing_requirements": missing_requirements,
            "risk_factors": scorecard.risks or ["No major risk factors detected"],
            "production_evidence": production_evidence,
            "behavioral_evidence": behavioral_evidence,
            "jd_alignment_score": round(scorecard.final_score * 100.0, 1),
            "score_breakdown": scorecard.components,
            "scoring_weights": scorecard.weights,
            "feature_count": len(values),
            "features": values,
            "skill_match": self._avg_components(scorecard, ["retrieval_ranking_experience", "vector_databases", "python_engineering", "evaluation_frameworks"]),
            "experience_match": scorecard.components.get("production_ml_experience", 0.0),
            "semantic_similarity": round(scorecard.final_score * 100.0, 1),
            "location_match": scorecard.components.get("location_relocation", 0.0),
            "potential_score": scorecard.components.get("startup_product_mindset", 0.0),
            "behavioral_score": scorecard.components.get("behavioral_signals", 0.0),
            "transferable_matches": len(top_matching_evidence),
            "behavioral_insights": behavioral_evidence,
            "anti_pattern_flags": anti_flags,
            "anti_pattern_penalty": self._penalty_product(scorecard),
            "candidate_details": candidate.raw,
        }

    def _avg_components(self, scorecard, names: list[str]) -> float:
        return round(sum(scorecard.components.get(name, 0.0) for name in names) / len(names), 1)

    def _penalty_product(self, scorecard) -> float:
        product = 1.0
        for value in scorecard.penalties.values():
            product *= value
        return round(product, 3)


def iter_jsonl(path: str | Path) -> Iterator[dict[str, Any]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)
