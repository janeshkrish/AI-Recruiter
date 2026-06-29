from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator


def canonical(text: Any) -> str:
    value = "" if text is None else str(text).lower()
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
    skill_text: str
    all_text: str


class CandidateProfileParser:
    """Parses every candidate field used by the deterministic ranker."""

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

        profile_text = canonical(
            " ".join(
                str(profile.get(key, ""))
                for key in (
                    "anonymized_name",
                    "headline",
                    "summary",
                    "location",
                    "country",
                    "current_title",
                    "current_company",
                    "current_company_size",
                    "current_industry",
                )
            )
        )
        career_text = canonical(
            " ".join(
                " ".join(str(job.get(key, "")) for key in job)
                for job in career_history
            )
        )
        skill_text = canonical(" ".join(str(skill.get("name", "")) for skill in skills))
        education_text = canonical(
            " ".join(" ".join(str(item.get(key, "")) for key in item) for item in education)
        )
        certification_text = canonical(
            " ".join(" ".join(str(item.get(key, "")) for key in item) for item in certifications)
        )
        project_text = canonical(
            " ".join(" ".join(str(item.get(key, "")) for key in item) for item in projects)
        )
        language_text = canonical(
            " ".join(" ".join(str(item.get(key, "")) for key in item) for item in languages)
        )
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
            skill_text=skill_text,
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
