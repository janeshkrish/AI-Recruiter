"""Legacy compatibility wrapper for the offline ranker.

This module intentionally contains no hosted LLM client code. It remains only so
older imports continue to work while the executable ranking pipeline lives in
``src/``.
"""

from __future__ import annotations

from typing import Any

from src.parser.jd_analyzer import JDAnalyzer


class RecruiterAgent:
    """Compatibility facade around the deterministic offline ranker."""

    async def parse_job_description(self, jd_text: str) -> dict[str, Any]:
        analyzer = JDAnalyzer()
        return analyzer.to_dict(analyzer.analyze(jd_text))

    async def run_pipeline(self, jd_text: str, custom_weights: dict[str, float] | None = None) -> dict[str, Any]:
        raise RuntimeError(
            "RecruiterAgent no longer owns data access. Use OfflineRanker with candidate records "
            "or the FastAPI /api/rank endpoint."
        )
