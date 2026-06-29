from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from src.parser.candidate_profile_parser import ParsedCandidate, canonical


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def as_int(value: Any, default: int = 0) -> int:
    return int(as_float(value, default))


def parse_date(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d")
    except ValueError:
        return None


@dataclass(frozen=True)
class HoneypotResult:
    penalty: float
    flags: list[str] = field(default_factory=list)


class HoneypotDetector:
    """Detects impossible or internally inconsistent candidate profiles."""

    def evaluate(self, candidate: ParsedCandidate) -> HoneypotResult:
        flags: list[str] = []
        penalty = 1.0

        profile_years = as_float(candidate.profile.get("years_of_experience"), 0.0)
        career_months = sum(max(0, as_int(job.get("duration_months"), 0)) for job in candidate.career_history)
        career_years = career_months / 12.0
        if profile_years >= 3 and career_years > 0 and abs(profile_years - career_years) > 4.0:
            penalty *= 0.82
            flags.append("profile years and career durations differ materially")
        if profile_years < 2 and career_months > 72:
            penalty *= 0.78
            flags.append("low stated experience conflicts with long career history")

        impossible_dates = 0
        for job in candidate.career_history:
            start = parse_date(job.get("start_date"))
            end = parse_date(job.get("end_date"))
            if start and end and end < start:
                impossible_dates += 1
        if impossible_dates:
            penalty *= 0.70
            flags.append("career dates contain impossible ranges")

        expert_zero_duration = 0
        total_expert = 0
        for skill in candidate.skills:
            if canonical(skill.get("proficiency")) == "expert":
                total_expert += 1
                if as_int(skill.get("duration_months"), 0) == 0:
                    expert_zero_duration += 1
        if expert_zero_duration >= 5:
            penalty *= 0.20
            flags.append("many expert skills have zero months used")
        elif expert_zero_duration >= 3:
            penalty *= 0.55
            flags.append("several expert skills have zero months used")

        if total_expert >= 12 and profile_years < 5:
            penalty *= 0.70
            flags.append("expertise count is high for stated experience")

        skill_months = [as_int(skill.get("duration_months"), 0) for skill in candidate.skills]
        if skill_months and max(skill_months) > max(profile_years * 12 + 24, 36):
            penalty *= 0.82
            flags.append("skill duration exceeds plausible career duration")

        if len(candidate.skills) >= 45 and profile_years < 6:
            penalty *= 0.82
            flags.append("very broad skill list for limited experience")

        return HoneypotResult(penalty=max(0.05, min(1.0, penalty)), flags=flags[:5])
