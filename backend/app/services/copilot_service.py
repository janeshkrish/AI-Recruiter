from __future__ import annotations

from typing import Any


class CopilotService:
    """Deterministic, non-LLM answer helper for the restored UI copilot."""

    def answer(self, question: str, candidates: list[dict[str, Any]], total_candidates: int | None = None) -> str:
        if not candidates:
            return "No ranked candidates were provided yet. Run a JD analysis first, then ask about the results."

        normalized = question.lower()
        top = candidates[0]
        second = candidates[1] if len(candidates) > 1 else None

        if "compare" in normalized and second:
            return self._compare(top, second)
        if "hidden" in normalized or "gem" in normalized:
            gem = max(candidates, key=lambda item: (item.get("potential_score") or 0) - (item.get("experience_match") or 0) * 0.2)
            return (
                f"Candidate {gem.get('candidate_id')} is the strongest hidden-gem signal in this slice: "
                f"potential {gem.get('potential_score', 0):.1f}, skill match {gem.get('skill_match', 0):.1f}, "
                f"and rank {gem.get('rank', 'n/a')}. Review the listed risks before moving forward."
            )
        if "rank" in normalized or "highest" in normalized or "#1" in normalized:
            return (
                f"{top.get('candidate_id')} is ranked highest because the deterministic scorer gave "
                f"{top.get('score', 0):.1f}/100 overall, with technical match {top.get('skill_match', 0):.1f}, "
                f"production experience {top.get('experience_match', 0):.1f}, and this evidence: "
                f"{top.get('reasoning', 'No reasoning available')}"
            )

        count = total_candidates or len(candidates)
        avg_score = sum(float(item.get("score") or 0.0) for item in candidates) / len(candidates)
        return (
            f"I reviewed {len(candidates)} displayed candidates out of {count}. "
            f"Their average displayed score is {avg_score:.1f}/100. The current top candidate is "
            f"{top.get('candidate_id')} with rank {top.get('rank', 1)}. Ask me to compare candidates, explain rank #1, or find hidden gems."
        )

    def _compare(self, first: dict[str, Any], second: dict[str, Any]) -> str:
        first_score = float(first.get("score") or 0.0)
        second_score = float(second.get("score") or 0.0)
        delta = first_score - second_score
        stronger_dimension = "technical match" if (first.get("skill_match") or 0) >= (second.get("skill_match") or 0) else "behavioral/readiness"
        return (
            f"{first.get('candidate_id')} leads {second.get('candidate_id')} by {delta:.1f} score points. "
            f"The main edge is {stronger_dimension}. "
            f"First reasoning: {first.get('reasoning', 'n/a')} Second reasoning: {second.get('reasoning', 'n/a')}"
        )
