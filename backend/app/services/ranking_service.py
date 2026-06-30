from __future__ import annotations

import csv
import hashlib
import heapq
import io
import json
import logging
import re
import threading
from collections import OrderedDict
from dataclasses import dataclass
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

GENERIC_STOP_WORDS = {
    "a",
    "an",
    "and",
    "any",
    "are",
    "as",
    "at",
    "be",
    "by",
    "can",
    "candidate",
    "candidates",
    "company",
    "description",
    "do",
    "experience",
    "for",
    "from",
    "good",
    "have",
    "hiring",
    "in",
    "is",
    "job",
    "knowledge",
    "looking",
    "must",
    "need",
    "of",
    "on",
    "or",
    "our",
    "required",
    "requirements",
    "responsibilities",
    "role",
    "should",
    "skills",
    "strong",
    "team",
    "the",
    "to",
    "type",
    "we",
    "with",
    "work",
    "year",
    "years",
}
GENERIC_ROLE_WORDS = {
    "accountant",
    "administrator",
    "analyst",
    "architect",
    "associate",
    "backend",
    "business",
    "civil",
    "cloud",
    "content",
    "customer",
    "data",
    "designer",
    "developer",
    "devops",
    "engineer",
    "executive",
    "frontend",
    "full",
    "fullstack",
    "graphic",
    "hr",
    "java",
    "manager",
    "marketing",
    "mechanical",
    "mobile",
    "net",
    "operations",
    "product",
    "project",
    "qa",
    "sales",
    "scientist",
    "software",
    "stack",
    "support",
    "writer",
}
GENERIC_SENIORITY_WORDS = {"associate", "junior", "lead", "mid", "principal", "senior", "staff"}
GENERIC_BROAD_ROLE_WORDS = {"developer", "engineer", "manager", "specialist", "lead", "senior", "staff"}
GENERIC_LOCATION_EXTRAS = {"remote", "hybrid", "onsite", "india"}


@dataclass(frozen=True)
class GenericJDSpec:
    raw_text: str
    normalized_text: str
    role_title: str
    role_terms: list[str]
    skills: list[str]
    important_terms: list[str]
    years_min: float | None
    years_max: float | None
    locations: list[str]
    anti_patterns: list[str]
    require_degree: bool


class RankingService:
    """Coordinates deterministic offline ranking for API consumers."""

    def __init__(self, repository: CandidateRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings
        self._cache: OrderedDict[str, tuple[list[dict[str, Any]], int]] = OrderedDict()
        self._lock = threading.Lock()
        self._generic_index: list[dict[str, Any]] | None = None
        self._generic_skill_vocabulary: tuple[str, ...] = ()
        self._generic_title_vocabulary: tuple[str, ...] = ()
        self._generic_location_vocabulary: tuple[str, ...] = ()
        self._generic_index_lock = threading.Lock()

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
            rows, scored_count = self._rank_generic_jd(text, top_n=top_n)

        with self._lock:
            self._cache[cache_key] = (rows, scored_count)
            self._cache.move_to_end(cache_key)
            while len(self._cache) > self.settings.ranking_cache_size:
                self._cache.popitem(last=False)
        return rows, scored_count

    def rank_response(self, jd_text: str, weights: dict[str, float] | None = None) -> dict[str, Any]:
        rows, scored_count = self.rank_with_metadata(jd_text, top_n=100, weights=weights)
        stats = self.repository.stats()
        parsed_jd = (
            JDAnalyzer().to_dict(JDAnalyzer().analyze(jd_text))
            if self._is_default_jd(jd_text)
            else self._generic_jd_to_dict(self._analyze_generic_jd(jd_text))
        )
        return {
            "ranked_candidates": [self.to_candidate_score(row) for row in rows],
            "parsed_jd": parsed_jd,
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

    def _rank_generic_jd(self, jd_text: str, *, top_n: int) -> tuple[list[dict[str, Any]], int]:
        profiles = self._generic_candidate_profiles()
        spec = self._analyze_generic_jd(jd_text)
        heap: list[tuple[float, float, float, int, int, dict[str, Any]]] = []

        for sequence, profile in enumerate(profiles):
            row = self._score_generic_candidate(profile, spec)
            candidate_number = self._candidate_numeric_id(row["candidate_id"])
            item = (
                row["overall_score"],
                row["skill_match"],
                row["potential_score"],
                -candidate_number,
                sequence,
                row,
            )
            if len(heap) < top_n:
                heapq.heappush(heap, item)
            elif item[:4] > heap[0][:4]:
                heapq.heapreplace(heap, item)

        rows = [
            item[5]
            for item in sorted(
                heap,
                key=lambda item: (-item[0], -item[1], -item[2], item[5]["candidate_id"]),
            )
        ]
        for rank, row in enumerate(rows, start=1):
            row["rank"] = rank
            row["reasoning"] = self._generic_reasoning(row, spec)
        logger.info(
            "Generic JD ranking role=%r skills=%s scored=%s returned=%s",
            spec.role_title or "unspecified",
            spec.skills[:8],
            len(profiles),
            len(rows),
        )
        return rows, len(profiles)

    def _generic_candidate_profiles(self) -> list[dict[str, Any]]:
        if self._generic_index is not None:
            return self._generic_index

        with self._generic_index_lock:
            if self._generic_index is not None:
                return self._generic_index

            profiles: list[dict[str, Any]] = []
            skill_vocabulary: set[str] = set()
            title_vocabulary: set[str] = set()
            location_vocabulary: set[str] = set(GENERIC_LOCATION_EXTRAS)
            for record in self.repository.iter_candidates():
                profile = record.get("profile") if isinstance(record.get("profile"), dict) else {}
                signals = record.get("redrob_signals") if isinstance(record.get("redrob_signals"), dict) else {}
                career_history = record.get("career_history") if isinstance(record.get("career_history"), list) else []
                skills = record.get("skills") if isinstance(record.get("skills"), list) else []
                projects = record.get("projects") if isinstance(record.get("projects"), list) else []

                title = canonical(profile.get("current_title"))
                title_vocabulary.add(title)
                skill_names = [
                    canonical(skill.get("name", "")) if isinstance(skill, dict) else canonical(skill)
                    for skill in skills
                    if isinstance(skill, (dict, str))
                ]
                skill_vocabulary.update(name for name in skill_names if name)

                location = canonical(profile.get("location"))
                country = canonical(profile.get("country"))
                if location:
                    location_vocabulary.add(location)
                    location_vocabulary.add(location.split(",", 1)[0].strip())
                if country:
                    location_vocabulary.add(country)

                career_titles = canonical(
                    " ".join(
                        str(job.get("title", ""))
                        for job in career_history
                        if isinstance(job, dict)
                    )
                )
                career_text = canonical(
                    " ".join(
                        str(job.get(key, ""))
                        for job in career_history
                        if isinstance(job, dict)
                        for key in ("title", "company", "industry")
                    )
                )
                project_text = canonical(
                    " ".join(
                        str(project.get(key, ""))
                        for project in projects
                        if isinstance(project, dict)
                        for key in ("name",)
                    )
                )
                skill_text = " ".join(skill_names)
                profile_text = canonical(
                    " ".join(
                        str(profile.get(key, ""))
                        for key in (
                            "headline",
                            "summary",
                            "current_title",
                            "current_company",
                            "current_industry",
                            "location",
                            "country",
                        )
                    )
                )
                all_text = canonical(f"{profile_text} {career_text} {project_text} {skill_text}")

                profiles.append(
                    {
                        "candidate_id": str(record.get("candidate_id", "")),
                        "record": record,
                        "title": title,
                        "role_text": canonical(f"{title} {career_titles}"),
                        "skill_text": skill_text,
                        "all_text": all_text,
                        "location_text": canonical(f"{location} {country} {signals.get('preferred_work_mode', '')}"),
                        "years": as_float(profile.get("years_of_experience"), 0.0),
                        "response_rate": min(max(as_float(signals.get("recruiter_response_rate"), 0.0), 0.0), 1.0),
                        "open_to_work": 1.0 if signals.get("open_to_work_flag") else 0.0,
                        "relocate": 1.0 if signals.get("willing_to_relocate") else 0.0,
                        "github": min(max(as_float(signals.get("github_activity_score"), 0.0), 0.0) / 100.0, 1.0),
                        "notice_days": as_float(signals.get("notice_period_days"), 90.0),
                    }
                )

            self._generic_index = profiles
            self._generic_skill_vocabulary = tuple(
                sorted((skill for skill in skill_vocabulary if len(skill) > 1), key=lambda value: (-len(value), value))
            )
            self._generic_title_vocabulary = tuple(
                sorted((title for title in title_vocabulary if title), key=lambda value: (-len(value), value))
            )
            self._generic_location_vocabulary = tuple(
                sorted((location for location in location_vocabulary if location), key=lambda value: (-len(value), value))
            )
            logger.info("Built generic JD index for %s candidates", len(profiles))
            return profiles

    def _analyze_generic_jd(self, jd_text: str) -> GenericJDSpec:
        self._generic_candidate_profiles()
        raw = jd_text.strip()
        text = canonical(raw)
        years_min, years_max = self._extract_generic_years(raw)
        role_title = self._extract_generic_role_title(raw, text)
        role_terms = self._role_terms(role_title, text)
        skills = self._extract_generic_skills(text)
        important_terms = self._extract_important_terms(text, skills, role_terms)
        locations = [
            location
            for location in self._generic_location_vocabulary
            if len(location) > 2 and self._contains_phrase(text, location)
        ][:8]
        anti_patterns = self._extract_generic_anti_patterns(text)
        require_degree = any(
            self._contains_phrase(text, phrase)
            for phrase in ("bachelor", "bachelors", "degree", "b.tech", "b.e", "m.tech", "master", "mba", "phd")
        )

        return GenericJDSpec(
            raw_text=raw,
            normalized_text=text,
            role_title=role_title,
            role_terms=role_terms,
            skills=skills,
            important_terms=important_terms,
            years_min=years_min,
            years_max=years_max,
            locations=locations,
            anti_patterns=anti_patterns,
            require_degree=require_degree,
        )

    def _extract_generic_role_title(self, raw: str, text: str) -> str:
        for title in self._generic_title_vocabulary:
            if self._contains_phrase(text, title):
                return title

        normalized_lines = [canonical(line) for line in raw.splitlines() if line.strip()]
        for line in normalized_lines[:8]:
            line = re.sub(r"^(job description|job title|role|position|title)\s+", "", line).strip()
            line = re.split(r"\b(?:location|employment|experience|required|responsibilities|about)\b", line, maxsplit=1)[0].strip()
            words = [word for word in line.split() if word not in GENERIC_STOP_WORDS]
            role_words = [word for word in words if word in GENERIC_ROLE_WORDS or word in GENERIC_SENIORITY_WORDS]
            if any(word in GENERIC_ROLE_WORDS for word in role_words):
                return " ".join(words[: min(len(words), 6)])

        match = re.search(
            r"(?:hiring|looking for|need|seeking)\s+(?:an?|the)?\s*([a-z0-9+#./ ]{3,80}?)(?:\s+with|\s+who|,|\.|\n|$)",
            text,
        )
        if match:
            candidate = " ".join(word for word in match.group(1).split() if word not in GENERIC_STOP_WORDS)
            if candidate:
                return candidate[:80]

        role_words = [word for word in text.split() if word in GENERIC_ROLE_WORDS or word in GENERIC_SENIORITY_WORDS]
        return " ".join(role_words[:5])

    def _role_terms(self, role_title: str, text: str) -> list[str]:
        terms = [
            word
            for word in role_title.split()
            if word not in GENERIC_STOP_WORDS and (word in GENERIC_ROLE_WORDS or len(word) > 3)
        ]
        if terms:
            unique_terms = list(dict.fromkeys(terms))
            specific_terms = [word for word in unique_terms if word not in GENERIC_BROAD_ROLE_WORDS]
            return (specific_terms or unique_terms)[:10]
        return [word for word in text.split() if word in GENERIC_ROLE_WORDS][:8]

    def _extract_generic_skills(self, text: str) -> list[str]:
        matches: list[str] = []
        relaxed_text = self._relaxed_skill_text(text)
        for skill in self._generic_skill_vocabulary:
            if self._contains_phrase(text, skill) or self._contains_phrase(relaxed_text, self._relaxed_skill_text(skill)):
                matches.append(skill)
            if len(matches) >= 28:
                break
        return matches

    def _extract_important_terms(self, text: str, skills: list[str], role_terms: list[str]) -> list[str]:
        terms: list[str] = []
        for skill in skills:
            terms.extend(token for token in skill.split() if token not in GENERIC_STOP_WORDS)
        terms.extend(role_terms)
        for token in text.split():
            if len(token) >= 3 and token not in GENERIC_STOP_WORDS and not token.isdigit():
                terms.append(token)
        return list(dict.fromkeys(terms))[:45]

    def _extract_generic_years(self, raw: str) -> tuple[float | None, float | None]:
        text = raw.lower().replace("–", "-").replace("—", "-")
        range_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:years|yrs|year)", text)
        if range_match:
            return float(range_match.group(1)), float(range_match.group(2))

        plus_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:\+|plus)?\s*(?:years|yrs|year)", text)
        if plus_match:
            years = float(plus_match.group(1))
            return years, max(years + 4.0, 9.0)
        return None, None

    def _extract_generic_anti_patterns(self, text: str) -> list[str]:
        patterns = []
        for phrase in (
            "consulting only",
            "contract only",
            "do not want",
            "no freshers",
            "not remote",
            "title chaser",
            "without production",
        ):
            if self._contains_phrase(text, phrase):
                patterns.append(phrase)
        return patterns

    def _generic_jd_to_dict(self, spec: GenericJDSpec) -> dict[str, Any]:
        skills = spec.skills or spec.important_terms[:12]
        return {
            "must_have": skills[:12],
            "nice_to_have": spec.important_terms[:12],
            "explicit_reject": spec.anti_patterns,
            "culture_fit": spec.role_terms[:6],
            "behavior_fit": ["response rate", "open to work", "short notice"],
            "hiring_intent": [
                f"match candidates for {spec.role_title}" if spec.role_title else "match candidates to the pasted JD",
                "rank by role, skill, experience, location, and readiness fit",
            ],
            "years_min": spec.years_min or 0.0,
            "years_max": spec.years_max or 0.0,
            "preferred_locations": spec.locations,
            "skills": skills,
            "years_experience": spec.years_min or 0.0,
            "location": "/".join(spec.locations[:3]),
            "require_degree": spec.require_degree,
            "hidden_traits": spec.role_terms[:6],
            "anti_patterns": spec.anti_patterns,
        }

    def _score_generic_candidate(self, profile: dict[str, Any], spec: GenericJDSpec) -> dict[str, Any]:
        matched_skills = [
            skill
            for skill in spec.skills
            if self._candidate_has_term(profile, skill)
        ]
        missing_skills = [skill for skill in spec.skills if skill not in matched_skills]

        if spec.skills:
            skill_score = len(matched_skills) / len(spec.skills)
        else:
            skill_score = self._term_overlap_score(spec.important_terms, profile["all_text"], cap=14)

        direct_title_match = bool(spec.role_title and self._contains_phrase(profile["role_text"], spec.role_title))
        title_overlap = self._term_overlap_score(spec.role_terms, profile["role_text"], cap=max(1, len(spec.role_terms)))
        title_score = 1.0 if direct_title_match else title_overlap

        semantic_score = self._term_overlap_score(spec.important_terms, profile["all_text"], cap=18)
        experience_score = self._experience_score(profile["years"], spec)
        location_score = self._location_score(profile, spec)
        behavior_score = self._behavior_score(profile)

        penalty = 1.0
        risk_factors: list[str] = []
        for pattern in spec.anti_patterns:
            if self._contains_phrase(profile["all_text"], pattern) or self._contains_phrase(profile["role_text"], pattern):
                penalty *= 0.78
                risk_factors.append(f"matches rejected pattern: {pattern}")

        final = (
            skill_score * 0.42
            + title_score * 0.22
            + semantic_score * 0.16
            + experience_score * 0.10
            + location_score * 0.05
            + behavior_score * 0.05
        )
        if spec.role_terms and title_score == 0.0:
            penalty *= 0.78
        final = max(0.0, min(1.0, final * penalty))
        overall = round(final * 100.0, 1)
        record = profile["record"]

        evidence = []
        if matched_skills:
            evidence.append("Matched skills: " + ", ".join(matched_skills[:8]))
        if spec.role_terms:
            matched_role_terms = [term for term in spec.role_terms if self._contains_phrase(profile["role_text"], term)]
            if matched_role_terms:
                evidence.append("Role/title fit: " + ", ".join(matched_role_terms[:6]))
        important_hits = [term for term in spec.important_terms if self._contains_phrase(profile["all_text"], term)]
        if important_hits:
            evidence.append("JD keyword evidence: " + ", ".join(important_hits[:8]))

        missing_requirements = missing_skills[:8]
        if spec.years_min is not None and profile["years"] < spec.years_min:
            missing_requirements.append(f"{spec.years_min:g}+ years experience")
        if spec.locations and location_score < 0.7:
            missing_requirements.append("preferred location or relocation")

        return {
            "candidate_id": profile["candidate_id"],
            "rank": 0,
            "score": round(final, 4),
            "reasoning": "",
            "candidate": {
                "name": record.get("profile", {}).get("anonymized_name", ""),
                "current_title": record.get("profile", {}).get("current_title", ""),
                "years_of_experience": profile["years"],
                "location": record.get("profile", {}).get("location", ""),
                "current_company": record.get("profile", {}).get("current_company", ""),
                "core_hits": len(matched_skills),
            },
            "overall_score": overall,
            "hiring_recommendation": self._generic_recommendation(overall),
            "top_matching_evidence": evidence[:8],
            "missing_requirements": missing_requirements[:8],
            "risk_factors": risk_factors or ["No major risk factors detected"],
            "production_evidence": evidence[:4] or ["Relevant evidence was found in candidate profile text"],
            "behavioral_evidence": [
                f"response rate {profile['response_rate']:.2f}",
                f"notice {profile['notice_days']:.0f} days",
            ],
            "jd_alignment_score": overall,
            "score_breakdown": {},
            "scoring_weights": {
                "skill_match": 42.0,
                "role_title_match": 22.0,
                "semantic_similarity": 16.0,
                "experience_match": 10.0,
                "location_match": 5.0,
                "readiness": 5.0,
            },
            "skill_match": round(skill_score * 100.0, 1),
            "experience_match": round(experience_score * 100.0, 1),
            "semantic_similarity": round(semantic_score * 100.0, 1),
            "location_match": round(location_score * 100.0, 1),
            "potential_score": round(title_score * 100.0, 1),
            "behavioral_score": round(behavior_score * 100.0, 1),
            "transferable_matches": len(matched_skills),
            "behavioral_insights": [
                f"response rate {profile['response_rate']:.2f}",
                "open to work" if profile["open_to_work"] else "open-to-work not listed",
            ],
            "anti_pattern_flags": risk_factors,
            "anti_pattern_penalty": round(penalty, 3),
            "candidate_details": record,
        }

    def _generic_reasoning(self, row: dict[str, Any], spec: GenericJDSpec) -> str:
        profile = row["candidate_details"].get("profile", {})
        title = profile.get("current_title") or "Candidate"
        company = profile.get("current_company") or "company not listed"
        target = spec.role_title or "the pasted role"
        evidence = row["top_matching_evidence"][:3]
        missing = row["missing_requirements"][:3]
        parts = [
            f"{row['hiring_recommendation']}: {title} at {company} for {target}",
            f"JD match score {row['overall_score']:.1f}/100",
        ]
        if evidence:
            parts.append("; ".join(evidence))
        if missing:
            parts.append("missing/weak: " + ", ".join(missing))
        parts.append(
            f"signals: response {row['behavioral_insights'][0].replace('response rate ', '')}, "
            f"location fit {row['location_match']:.0f}%, experience fit {row['experience_match']:.0f}%"
        )
        return "; ".join(parts)[:900]

    def _candidate_has_term(self, profile: dict[str, Any], term: str) -> bool:
        return (
            self._contains_phrase(profile["skill_text"], term)
            or self._contains_phrase(profile["all_text"], term)
            or self._contains_phrase(self._relaxed_skill_text(profile["skill_text"]), self._relaxed_skill_text(term))
        )

    def _term_overlap_score(self, terms: list[str], text: str, *, cap: int) -> float:
        if not terms:
            return 0.65
        hits = sum(1 for term in terms if self._contains_phrase(text, term))
        return min(hits / max(1, min(len(terms), cap)), 1.0)

    def _experience_score(self, years: float, spec: GenericJDSpec) -> float:
        if spec.years_min is None:
            return 0.75
        if years >= spec.years_min and (spec.years_max is None or years <= spec.years_max):
            return 1.0
        if years < spec.years_min:
            return max(0.0, min(0.85, years / max(spec.years_min, 1.0)))
        if spec.years_max and years > spec.years_max:
            return 0.82
        return 0.75

    def _location_score(self, profile: dict[str, Any], spec: GenericJDSpec) -> float:
        if not spec.locations:
            return 0.75
        if any(self._contains_phrase(profile["location_text"], location) for location in spec.locations):
            return 1.0
        if profile["relocate"]:
            return 0.85
        if any(location in {"remote", "hybrid"} for location in spec.locations) and any(
            self._contains_phrase(profile["location_text"], mode) for mode in ("remote", "hybrid", "flexible")
        ):
            return 0.92
        return 0.35

    def _behavior_score(self, profile: dict[str, Any]) -> float:
        notice_score = 1.0 if profile["notice_days"] <= 30 else 0.78 if profile["notice_days"] <= 60 else 0.45
        return min(
            profile["response_rate"] * 0.45
            + profile["open_to_work"] * 0.20
            + notice_score * 0.20
            + profile["github"] * 0.15,
            1.0,
        )

    def _generic_recommendation(self, score: float) -> str:
        if score >= 82:
            return "Strong Hire"
        if score >= 68:
            return "Hire"
        if score >= 52:
            return "Maybe"
        return "Reject"

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        if not phrase:
            return False
        return f" {phrase} " in f" {text} "

    def _relaxed_skill_text(self, value: str) -> str:
        return " ".join(value.replace(".", " ").replace("/", " ").replace("+", " plus ").replace("#", " sharp ").split())

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
