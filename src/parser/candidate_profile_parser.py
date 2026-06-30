from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterator


def canonical(text: Any) -> str:
    return _canonical_string("" if text is None else str(text))


@lru_cache(maxsize=20000)
def _canonical_string(text: str) -> str:
    value = text.lower()
    value = value.replace("&", " and ")
    value = re.sub(r"[^a-z0-9+#./]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


@dataclass(frozen=True)
class ParsedCandidate:
    candidate_id: str
    raw: dict[str, Any]
    profile: dict[str, Any]
    career_history: list[dict[str, Any]]
    education: list[dict[str, Any]]
    skills: list[dict[str, Any]]
    certifications: list[dict[str, Any]]
    projects: list[dict[str, Any]]
    languages: list[dict[str, Any]]
    redrob_signals: dict[str, Any]
    profile_text: str
    career_text: str
    education_text: str
    skill_text: str
    certification_text: str
    project_text: str
    language_text: str
    recruiter_signal_text: str
    all_text: str


class CandidateProfileParser:
    """Parses every candidate section used by the deterministic ranker.

    The public Redrob JSONL is already structured, so parsing here means
    normalizing missing/optional sections, preserving the full raw record, and
    building canonical section text for deterministic feature extraction.
    """

    def parse_jsonl(self, path: str | Path) -> Iterator[ParsedCandidate]:
        input_path = Path(path)
        with input_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                yield self.parse_record(json.loads(line))

    def parse_records(self, records: Iterator[dict[str, Any]]) -> Iterator[ParsedCandidate]:
        for record in records:
            yield self.parse_record(record)

    def parse_record(self, data: dict[str, Any]) -> ParsedCandidate:
        profile = self._dict(data.get("profile"))
        career_history = self._list_of_dicts(data.get("career_history"))
        education = self._list_of_dicts(data.get("education"))
        skills = self._normalize_skills(data.get("skills"))
        certifications = self._list_of_dicts(data.get("certifications"))
        projects = self._list_of_dicts(data.get("projects"))
        languages = self._list_of_dicts(data.get("languages"))
        redrob_signals = self._dict(data.get("redrob_signals"))

        profile_text = self._section_text(profile)
        career_text = self._section_text(career_history)
        skill_text = canonical(" ".join(str(skill.get("name", "")) for skill in skills))
        education_text = self._section_text(education)
        certification_text = self._section_text(certifications)
        project_text = self._section_text(projects)
        language_text = self._section_text(languages)
        recruiter_signal_text = self._section_text(redrob_signals)
        all_text = canonical(
            " ".join(
                [
                    profile_text,
                    career_text,
                    skill_text,
                    education_text,
                    certification_text,
                    project_text,
                    language_text,
                    recruiter_signal_text,
                ]
            )
        )

        return ParsedCandidate(
            candidate_id=str(data.get("candidate_id", "")),
            raw=data,
            profile=profile,
            career_history=career_history,
            education=education,
            skills=skills,
            certifications=certifications,
            projects=projects,
            languages=languages,
            redrob_signals=redrob_signals,
            profile_text=profile_text,
            career_text=career_text,
            education_text=education_text,
            skill_text=skill_text,
            certification_text=certification_text,
            project_text=project_text,
            language_text=language_text,
            recruiter_signal_text=recruiter_signal_text,
            all_text=all_text,
        )

    def _dict(self, value: Any) -> dict[str, Any]:
        return value if isinstance(value, dict) else {}

    def _list_of_dicts(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, dict)]

    def _normalize_skills(self, value: Any) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []
        skills: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, str):
                skills.append({"name": item, "proficiency": "intermediate", "endorsements": 0, "duration_months": 0})
            elif isinstance(item, dict):
                skills.append(
                    {
                        "name": str(item.get("name", "")),
                        "proficiency": str(item.get("proficiency", "intermediate")),
                        "endorsements": item.get("endorsements", 0),
                        "duration_months": item.get("duration_months", 0),
                    }
                )
        return skills

    def _section_text(self, value: Any) -> str:
        return canonical(" ".join(self._flatten_values(value)))

    def _flatten_values(self, value: Any) -> Iterator[str]:
        if isinstance(value, dict):
            for key, nested in value.items():
                yield str(key)
                yield from self._flatten_values(nested)
        elif isinstance(value, list):
            for nested in value:
                yield from self._flatten_values(nested)
        elif value is not None:
            yield str(value)
