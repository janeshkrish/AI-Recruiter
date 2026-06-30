from __future__ import annotations

import csv
import hashlib
import heapq
import io
import json
import logging
import threading
from collections import OrderedDict
from pathlib import Path
from typing import Any

from backend.app.core.config import Settings
from backend.app.repositories.candidate_repository import CandidateRepository
from src.feature_engineering.features import (
    AI_TERMS,
    EMBEDDING_TERMS,
    EVALUATION_TERMS,
    LOCATION_TERMS,
    NON_TECH_TITLES,
    PRODUCT_TERMS,
    PRODUCTION_TERMS,
    PYTHON_TERMS,
    RANKING_TERMS,
    RECOMMENDATION_TERMS,
    RETRIEVAL_TERMS,
    SERVICE_COMPANIES,
    STARTUP_TERMS,
    VECTOR_DB_TERMS,
)
from src.parser.candidate_profile_parser import canonical
from src.parser.jd_analyzer import DEFAULT_REDROB_JD, JDAnalyzer
from src.ranking.ranker import OfflineRanker
from src.scoring.scoring_engine import DEFAULT_WEIGHTS
from src.validation.honeypot_detector import as_float


logger = logging.getLogger(__name__)

POOL_TERM_GROUPS = (
    ("production_ai", tuple(canonical(term) for term in AI_TERMS + PRODUCTION_TERMS), 18.0, 8),
    ("retrieval_embedding", tuple(canonical(term) for term in RETRIEVAL_TERMS + EMBEDDING_TERMS), 18.0, 6),
    ("ranking_recommendation", tuple(canonical(term) for term in RANKING_TERMS + RECOMMENDATION_TERMS), 16.0, 6),
    ("vector_db", tuple(canonical(term) for term in VECTOR_DB_TERMS), 15.0, 4),
    ("python", tuple(canonical(term) for term in PYTHON_TERMS), 10.0, 3),
    ("evaluation", tuple(canonical(term) for term in EVALUATION_TERMS), 12.0, 5),
    ("startup_product", tuple(canonical(term) for term in STARTUP_TERMS + PRODUCT_TERMS), 7.0, 5),
)
POOL_SERVICE_COMPANIES = tuple(canonical(company) for company in SERVICE_COMPANIES)
POOL_NON_TECH_TITLES = tuple(canonical(title) for title in NON_TECH_TITLES)
POOL_LOCATION_TERMS = tuple(canonical(location) for location in LOCATION_TERMS)
POOL_TEXT_TRANSLATION = str.maketrans({char: " " for char in "\r\n\t,;:()[]{}|\\-_*"})


class RankingService:
    """Coordinates deterministic offline ranking for API consumers."""

    def __init__(self, repository: CandidateRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings
        self._cache: OrderedDict[str, tuple[list[dict[str, Any]], int]] = OrderedDict()
        self._lock = threading.Lock()

    def rank(self, jd_text: str | None, *, top_n: int = 100, weights: dict[str, float] | None = None) -> list[dict[str, Any]]:
        rows, _ = self.rank_with_metadata(jd_text, top_n=top_n, weights=weights)
        return rows

    def rank_with_metadata(
        self,
        jd_text: str | None,
        *,
        top_n: int = 100,
        weights: dict[str, float] | None = None,
    ) -> tuple[list[dict[str, Any]], int]:
        text = jd_text.strip() if jd_text and jd_text.strip() else self.default_jd_text()
        top_n = max(1, min(top_n, 500))
        cache_key = self._cache_key(text, top_n, weights)
        with self._lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                self._cache.move_to_end(cache_key)
                return cached

        logger.info("Ranking candidates top_n=%s", top_n)
        rows = None
        scored_count = 0
        if weights is None and self._is_default_jd(text):
            rows = self._rank_from_submission_csv(text, top_n=top_n)
            scored_count = len(rows or [])
        if rows is None:
            pool = self._candidate_pool(text, top_n=top_n)
            scored_count = len(pool)
            logger.info("Ranking candidate pool pool_size=%s top_n=%s", len(pool), top_n)
            rows = OfflineRanker(jd_text=text, weights=weights).rank_records(pool, top_n=top_n)

        with self._lock:
            self._cache[cache_key] = (rows, scored_count)
            self._cache.move_to_end(cache_key)
            while len(self._cache) > self.settings.ranking_cache_size:
                self._cache.popitem(last=False)
        return rows, scored_count

    def rank_response(self, jd_text: str, weights: dict[str, float] | None = None) -> dict[str, Any]:
        rows, scored_count = self.rank_with_metadata(jd_text, top_n=100, weights=weights)
        stats = self.repository.stats()
        return {
            "ranked_candidates": [self.to_candidate_score(row) for row in rows],
            "parsed_jd": JDAnalyzer().to_dict(JDAnalyzer().analyze(jd_text)),
            "pipeline_stats": {
                "total_indexed": stats["total_applicants"],
                "retrieved": scored_count,
                "scored": scored_count,
                "returned": len(rows),
            },
        }

    def role_ranking_response(self, *, limit: int = 100) -> dict[str, Any]:
        rows = self.rank(self.default_jd_text(), top_n=limit)
        return {
            "role": "Senior AI Engineer - Founding Team",
            "source_documents": ["job_description.docx", "candidate_schema.json", "submission_spec.docx"],
            "total": len(rows),
            "rows": rows,
        }

    def role_ranking_csv(self, *, limit: int = 100) -> str:
        rows = self.rank(self.default_jd_text(), top_n=limit)
        output = io.StringIO(newline="")
        writer = csv.DictWriter(output, fieldnames=["candidate_id", "rank", "score", "reasoning"])
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
        return output.getvalue()

    def default_jd_text(self) -> str:
        path = self.settings.default_jd_file
        if path.exists():
            return path.read_text(encoding="utf-8")
        return DEFAULT_REDROB_JD

    def weights(self) -> dict[str, float]:
        return dict(DEFAULT_WEIGHTS)

    def to_candidate_score(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "candidate_id": row["candidate_id"],
            "rank": row["rank"],
            "score": row["overall_score"],
            "skill_match": row["skill_match"],
            "experience_match": row["experience_match"],
            "semantic_similarity": row["semantic_similarity"],
            "location_match": row["location_match"],
            "potential_score": row["potential_score"],
            "behavioral_score": row["behavioral_score"],
            "transferable_matches": row["transferable_matches"],
            "reasoning": row["reasoning"],
            "behavioral_insights": row["behavioral_insights"],
            "anti_pattern_flags": row["anti_pattern_flags"],
            "anti_pattern_penalty": row["anti_pattern_penalty"],
            "candidate_details": row["candidate_details"],
            "overall_score": row["overall_score"],
            "hiring_recommendation": row["hiring_recommendation"],
            "top_matching_evidence": row["top_matching_evidence"],
            "missing_requirements": row["missing_requirements"],
            "risk_factors": row["risk_factors"],
            "production_evidence": row["production_evidence"],
            "behavioral_evidence": row["behavioral_evidence"],
            "jd_alignment_score": row["jd_alignment_score"],
            "score_breakdown": row["score_breakdown"],
            "scoring_weights": row["scoring_weights"],
        }

    def _cache_key(self, jd_text: str, top_n: int, weights: dict[str, float] | None) -> str:
        payload = json.dumps({"jd": jd_text, "top_n": top_n, "weights": weights or {}}, sort_keys=True)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _is_default_jd(self, jd_text: str) -> bool:
        return jd_text.strip() == self.default_jd_text().strip()

    def _rank_from_submission_csv(self, jd_text: str, *, top_n: int) -> list[dict[str, Any]] | None:
        path = Path(self.settings.default_ranking_csv)
        if not path.exists():
            return None

        csv_rows: list[dict[str, str]] = []
        try:
            with path.open("r", encoding="utf-8", newline="") as handle:
                reader = csv.DictReader(handle)
                for row in reader:
                    candidate_id = (row.get("candidate_id") or "").strip()
                    if candidate_id:
                        csv_rows.append(row)
                    if len(csv_rows) >= top_n:
                        break
        except OSError:
            logger.warning("Could not read default ranking CSV at %s", path, exc_info=True)
            return None

        if len(csv_rows) < top_n:
            return None

        candidate_ids = [(row.get("candidate_id") or "").strip() for row in csv_rows]
        records = self.repository.get_many_by_id(candidate_ids)
        if len(records) < len(candidate_ids):
            return None

        ranked_rows = OfflineRanker(jd_text=jd_text).rank_records(records, top_n=len(records))
        ranked_by_id = {row["candidate_id"]: row for row in ranked_rows}
        ordered_rows: list[dict[str, Any]] = []
        for fallback_rank, csv_row in enumerate(csv_rows, start=1):
            candidate_id = (csv_row.get("candidate_id") or "").strip()
            row = ranked_by_id.get(candidate_id)
            if row is None:
                return None
            score = as_float(csv_row.get("score"), row["score"])
            rank = int(as_float(csv_row.get("rank"), fallback_rank))
            row["rank"] = rank
            row["score"] = round(score, 4)
            row["overall_score"] = round(score * 100.0, 1)
            row["jd_alignment_score"] = row["overall_score"]
            ordered_rows.append(row)
        logger.info("Hydrated %s ranking rows from %s", len(ordered_rows), path)
        return ordered_rows

    def _candidate_pool(self, jd_text: str, *, top_n: int) -> list[dict[str, Any]]:
        requirements = JDAnalyzer().analyze(jd_text)
        pool_size = max(top_n, min(max(self.settings.api_ranking_pool_size, top_n * 20), 50000))
        jd_terms = tuple(canonical(term) for term in requirements.must_have + requirements.nice_to_have)
        heap: list[tuple[float, int, int, dict[str, Any]]] = []
        sequence = 0

        for record in self.repository.iter_candidates():
            candidate_id = str(record.get("candidate_id", ""))
            if not candidate_id:
                continue
            score = self._candidate_pool_score(record, requirements.years_min, requirements.years_max, jd_terms)
            candidate_number = self._candidate_numeric_id(candidate_id)
            item = (score, -candidate_number, sequence, record)
            sequence += 1
            if len(heap) < pool_size:
                heapq.heappush(heap, item)
            elif item[:2] > heap[0][:2]:
                heapq.heapreplace(heap, item)

        return [item[3] for item in sorted(heap, key=lambda item: (-item[0], str(item[3].get("candidate_id", ""))))[:pool_size]]

    def _candidate_pool_score(
        self,
        record: dict[str, Any],
        years_min: float,
        years_max: float,
        jd_terms: tuple[str, ...],
    ) -> float:
        profile = record.get("profile") if isinstance(record.get("profile"), dict) else {}
        signals = record.get("redrob_signals") if isinstance(record.get("redrob_signals"), dict) else {}
        career_history = record.get("career_history") if isinstance(record.get("career_history"), list) else []
        skills = record.get("skills") if isinstance(record.get("skills"), list) else []
        projects = record.get("projects") if isinstance(record.get("projects"), list) else []

        title = self._pool_text(profile.get("current_title"))
        location = self._pool_text(profile.get("location"))
        country = self._pool_text(profile.get("country"))
        skill_text = self._pool_text(
            " ".join(
                str(skill.get("name", "")) if isinstance(skill, dict) else str(skill)
                for skill in skills
                if isinstance(skill, (dict, str))
            )
        )
        profile_text = self._pool_text(
            " ".join(
                str(profile.get(key, ""))
                for key in ("headline", "summary", "current_title", "current_company", "current_industry")
            )
        )
        career_text = self._pool_text(
            " ".join(
                str(job.get(key, ""))
                for job in career_history
                if isinstance(job, dict)
                for key in ("title", "company", "industry")
            )
        )
        project_text = self._pool_text(
            " ".join(
                str(project.get(key, ""))
                for project in projects
                if isinstance(project, dict)
                for key in ("name",)
            )
        )
        all_text = f"{profile_text} {career_text} {skill_text} {project_text}"

        years = as_float(profile.get("years_of_experience"), 0.0)
        score = 0.0
        if years_min <= years <= years_max:
            score += 12.0
        elif years >= max(0.0, years_min - 1.5):
            score += 7.0
        elif years >= 3.0:
            score += 3.0

        for _, terms, weight, cap in POOL_TERM_GROUPS:
            all_hits = sum(1 for term in terms if term in all_text)
            score += min(all_hits / cap, 1.0) * weight

        if jd_terms:
            jd_hits = sum(1 for term in jd_terms if term in all_text)
            score += min(jd_hits / max(1, len(jd_terms)), 1.0) * 10.0

        if any(term in title for term in ("senior", "lead", "staff", "principal", "architect")):
            score += 4.0
        if any(term in location for term in POOL_LOCATION_TERMS) or "india" in country:
            score += 3.0
        if signals.get("willing_to_relocate"):
            score += 2.0
        if signals.get("open_to_work_flag"):
            score += 2.0
        score += min(max(as_float(signals.get("github_activity_score"), 0.0), 0.0) / 100.0, 1.0) * 3.0
        score += min(max(as_float(signals.get("recruiter_response_rate"), 0.0), 0.0), 1.0) * 3.0

        service_roles = 0
        for job in career_history:
            if not isinstance(job, dict):
                continue
            company = self._pool_text(job.get("company"))
            industry = self._pool_text(job.get("industry"))
            if any(service in company for service in POOL_SERVICE_COMPANIES) or "it services" in industry or "consulting" in industry:
                service_roles += 1
        if career_history and service_roles == len([job for job in career_history if isinstance(job, dict)]):
            score -= 14.0
        if any(term in title for term in POOL_NON_TECH_TITLES):
            score -= 18.0

        return score

    def _pool_text(self, value: Any) -> str:
        return " ".join(str(value or "").lower().replace("&", " and ").translate(POOL_TEXT_TRANSLATION).split())

    def _candidate_numeric_id(self, candidate_id: str) -> int:
        try:
            return int(candidate_id.rsplit("_", 1)[1])
        except (IndexError, ValueError):
            return 10**12
