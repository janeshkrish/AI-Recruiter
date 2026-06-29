"""Compatibility wrapper for the offline Redrob ranker."""

from __future__ import annotations

from typing import Any, Iterable

from src.parser.jd_analyzer import DEFAULT_REDROB_JD
from src.ranking.ranker import OfflineRanker


class DocumentInformedRanker:
    """Legacy class name backed by the new deterministic offline pipeline."""

    def __init__(self, jd_text: str | None = None, weights: dict[str, float] | None = None) -> None:
        self.ranker = OfflineRanker(jd_text=jd_text or DEFAULT_REDROB_JD, weights=weights)

    def rank(self, candidates: Iterable[dict[str, Any]], top_n: int = 100) -> list[dict[str, Any]]:
        return self.ranker.rank_records(candidates, top_n=top_n)
