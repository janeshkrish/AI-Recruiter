"""
Feature Engineering
====================

Normalizes and transforms agent scores for the ranking engine.
Handles missing scores, score calibration, and feature analysis.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from loguru import logger

from recruiter_brain.data.models import AgentScores


class FeatureEngineer:
    """
    Normalizes and calibrates agent scores for the ranking engine.

    Handles:
    - Min-max normalization across candidates
    - Missing score imputation (recruiter_reasoning only for top candidates)
    - Score distribution analysis
    """

    def __init__(self) -> None:
        self._stats: Optional[dict[str, dict[str, float]]] = None
        logger.info("FeatureEngineer initialized")

    def fit(self, scores_list: list[AgentScores]) -> None:
        """
        Compute normalization statistics from a batch of scores.

        Args:
            scores_list: List of AgentScores for all candidates.
        """
        if not scores_list:
            return

        fields = [
            "technical_fit_score",
            "career_fit_score",
            "behavioral_fit_score",
            "potential_score",
            "recruiter_reasoning_score",
        ]

        self._stats = {}
        for field in fields:
            values = [getattr(s, field) for s in scores_list]
            non_zero = [v for v in values if v > 0]

            self._stats[field] = {
                "min": min(values) if values else 0.0,
                "max": max(values) if values else 1.0,
                "mean": float(np.mean(values)) if values else 0.5,
                "std": float(np.std(values)) if values else 0.1,
                "median": float(np.median(values)) if values else 0.5,
                "non_zero_count": len(non_zero),
                "total_count": len(values),
            }

        logger.info(
            f"FeatureEngineer fitted on {len(scores_list)} score records"
        )

    def normalize(self, scores: AgentScores) -> AgentScores:
        """
        Normalize scores to [0, 1] using fitted statistics.

        If no stats are fitted, returns scores as-is (they should
        already be 0-1 from the agents).

        Args:
            scores: Raw agent scores.

        Returns:
            Normalized AgentScores.
        """
        if self._stats is None:
            return scores

        normalized = scores.model_copy()

        for field in [
            "technical_fit_score",
            "career_fit_score",
            "behavioral_fit_score",
            "potential_score",
        ]:
            raw = getattr(scores, field)
            stats = self._stats[field]
            range_val = stats["max"] - stats["min"]

            if range_val > 0:
                norm_val = (raw - stats["min"]) / range_val
            else:
                norm_val = 0.5

            setattr(normalized, field, round(float(np.clip(norm_val, 0, 1)), 4))

        return normalized

    def normalize_batch(
        self, scores_list: list[AgentScores]
    ) -> list[AgentScores]:
        """Normalize a batch of scores."""
        return [self.normalize(s) for s in scores_list]

    def impute_missing(
        self, scores: AgentScores, default: float = 0.5
    ) -> AgentScores:
        """
        Fill missing scores (e.g., recruiter_reasoning for non-top candidates).

        Args:
            scores: Agent scores with potential missing values.
            default: Default value for missing scores.

        Returns:
            AgentScores with imputed values.
        """
        result = scores.model_copy()

        if result.recruiter_reasoning_score == 0.0:
            # Impute from other scores
            if self._stats and self._stats["recruiter_reasoning_score"]["non_zero_count"] > 0:
                result.recruiter_reasoning_score = self._stats[
                    "recruiter_reasoning_score"
                ]["mean"]
            else:
                # Use weighted average of other scores as proxy
                result.recruiter_reasoning_score = (
                    result.technical_fit_score * 0.3
                    + result.career_fit_score * 0.25
                    + result.behavioral_fit_score * 0.2
                    + result.potential_score * 0.25
                )

        return result

    def get_distribution_summary(self) -> dict[str, dict]:
        """Get summary statistics for each score dimension."""
        if self._stats is None:
            return {}
        return self._stats
