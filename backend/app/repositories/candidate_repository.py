from __future__ import annotations

import json
import logging
import threading
from pathlib import Path
from typing import Any, Iterable

from backend.app.core.errors import AppError
from src.parser.candidate_profile_parser import canonical


logger = logging.getLogger(__name__)


class CandidateRepository:
    """Read-through in-memory repository over the Redrob JSONL dataset."""

    def __init__(self, candidates_path: Path) -> None:
        self.candidates_path = candidates_path
        self._records: list[dict[str, Any]] | None = None
        self._by_id: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def ensure_loaded(self) -> None:
        if self._records is not None:
            return
        with self._lock:
            if self._records is not None:
                return
            if not self.candidates_path.exists():
                raise AppError(
                    f"Candidates file not found: {self.candidates_path}",
                    status_code=500,
                    code="DATASET_NOT_FOUND",
                )
            records: list[dict[str, Any]] = []
            by_id: dict[str, dict[str, Any]] = {}
            logger.info("Loading candidates from %s", self.candidates_path)
            with self.candidates_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    candidate_id = str(record.get("candidate_id", ""))
                    if candidate_id:
                        by_id[candidate_id] = record
                        records.append(record)
            self._records = records
            self._by_id = by_id
            logger.info("Loaded %s candidates", len(records))

    def iter_candidates(self) -> Iterable[dict[str, Any]]:
        self.ensure_loaded()
        return iter(self._records or [])

    def get_by_id(self, candidate_id: str) -> dict[str, Any] | None:
        self.ensure_loaded()
        return self._by_id.get(candidate_id)

    def get_many_by_id(self, candidate_ids: Iterable[str]) -> list[dict[str, Any]]:
        self.ensure_loaded()
        return [self._by_id[candidate_id] for candidate_id in candidate_ids if candidate_id in self._by_id]

    def list_candidates(
        self,
        *,
        page: int,
        limit: int,
        search: str = "",
        skills: str = "",
        min_experience: float = 0.0,
        current_role: str = "",
    ) -> dict[str, Any]:
        self.ensure_loaded()
        page = max(1, page)
        limit = max(1, min(limit, 500))
        filtered = [
            record
            for record in self._records or []
            if self._matches(record, search=search, skills=skills, min_experience=min_experience, current_role=current_role)
        ]
        total = len(filtered)
        start = (page - 1) * limit
        end = start + limit
        return {
            "data": filtered[start:end],
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": max(1, (total + limit - 1) // limit),
        }

    def stats(self) -> dict[str, Any]:
        self.ensure_loaded()
        records = self._records or []
        companies = {
            record.get("profile", {}).get("current_company")
            for record in records
            if record.get("profile", {}).get("current_company")
        }
        years = [float(record.get("profile", {}).get("years_of_experience") or 0.0) for record in records]
        hidden_gems = sum(
            1
            for record in records
            if float(record.get("redrob_signals", {}).get("github_activity_score") or 0.0) >= 70
            and float(record.get("profile", {}).get("years_of_experience") or 0.0) < 5
        )
        return {
            "total_applicants": len(records),
            "indexed_candidates": len(records),
            "total_companies": len(companies),
            "average_experience": round(sum(years) / len(years), 1) if years else 0.0,
            "hidden_gems_found": hidden_gems,
        }

    def _matches(
        self,
        record: dict[str, Any],
        *,
        search: str,
        skills: str,
        min_experience: float,
        current_role: str,
    ) -> bool:
        profile = record.get("profile", {})
        if min_experience and float(profile.get("years_of_experience") or 0.0) < min_experience:
            return False
        if current_role and canonical(current_role) not in canonical(profile.get("current_title")):
            return False
        if skills:
            wanted = [canonical(item) for item in skills.split(",") if item.strip()]
            skill_text = " ".join(canonical(skill.get("name") if isinstance(skill, dict) else skill) for skill in record.get("skills", []))
            if wanted and not all(skill in skill_text for skill in wanted):
                return False
        if search:
            needle = canonical(search)
            haystack = canonical(
                " ".join(
                    [
                        str(record.get("candidate_id", "")),
                        str(profile.get("anonymized_name", "")),
                        str(profile.get("headline", "")),
                        str(profile.get("current_company", "")),
                        str(profile.get("current_title", "")),
                        " ".join(str(skill.get("name", "")) for skill in record.get("skills", []) if isinstance(skill, dict)),
                    ]
                )
            )
            if needle not in haystack:
                return False
        return True
