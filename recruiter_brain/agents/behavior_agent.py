"""
Agent 4 — Behavioral Intelligence Agent
=========================================

Analyzes platform behavioral signals to assess candidate hireability.

Features:
- Recruiter response rate
- Platform engagement
- Profile completeness
- Interview completion rate
- Offer acceptance rate
- Recruiter saves
- Activity score

All features are min-max normalized across the candidate pool.

Returns: behavioral_fit_score (0–1)
"""

from __future__ import annotations

from typing import Optional

import numpy as np
from loguru import logger

from recruiter_brain.data.models import BehavioralSignals, CandidateProfile


# Feature weights for behavioral scoring
FEATURE_WEIGHTS = {
    "recruiter_response_rate": 0.20,
    "platform_engagement": 0.15,
    "profile_completeness": 0.20,
    "interview_completion_rate": 0.15,
    "offer_acceptance_rate": 0.10,
    "recruiter_saves": 0.10,
    "activity_score": 0.10,
}


class BehavioralIntelligenceAgent:
    """
    Agent 4: Scores candidates on behavioral/engagement signals.

    Normalizes features across the candidate pool (min-max),
    then applies weighted combination for final behavioral fit score.
    """

    def __init__(self) -> None:
        self._pool_stats: Optional[dict[str, dict[str, float]]] = None
        logger.info("BehavioralIntelligenceAgent initialized")

    def compute_pool_stats(
        self, candidates: list[CandidateProfile]
    ) -> None:
        """
        Compute min/max statistics across the candidate pool for normalization.

        Args:
            candidates: Full candidate pool.
        """
        if not candidates:
            logger.warning("Empty candidate pool for behavioral stats")
            return

        features = self._extract_features_batch(candidates)
        self._pool_stats = {}

        for feature_name in FEATURE_WEIGHTS:
            values = [f[feature_name] for f in features]
            self._pool_stats[feature_name] = {
                "min": min(values),
                "max": max(values),
                "mean": np.mean(values),
                "std": np.std(values),
            }

        logger.info(
            f"Computed behavioral pool stats for {len(candidates):,} candidates"
        )

    def score(self, candidate: CandidateProfile) -> dict[str, float]:
        """
        Score a single candidate's behavioral signals.

        Args:
            candidate: The candidate profile.

        Returns:
            Dict with behavioral_fit_score and feature details.
        """
        features = self._extract_features(candidate.behavioral_signals)
        normalized = self._normalize(features)

        # Weighted sum
        behavioral_fit = sum(
            FEATURE_WEIGHTS[name] * normalized[name]
            for name in FEATURE_WEIGHTS
        )

        return {
            "behavioral_fit_score": round(
                float(np.clip(behavioral_fit, 0, 1)), 4
            ),
            **{f"behavioral_{k}": round(v, 4) for k, v in normalized.items()},
        }

    def score_batch(
        self, candidates: list[CandidateProfile]
    ) -> list[dict[str, float]]:
        """
        Score multiple candidates.

        Automatically computes pool stats if not done yet.

        Args:
            candidates: List of candidate profiles.

        Returns:
            List of score dicts.
        """
        if self._pool_stats is None:
            self.compute_pool_stats(candidates)

        return [self.score(c) for c in candidates]

    def _extract_features(
        self, signals: BehavioralSignals
    ) -> dict[str, float]:
        """Extract raw feature values from behavioral signals."""
        return {
            "recruiter_response_rate": signals.recruiter_response_rate,
            "platform_engagement": signals.platform_engagement,
            "profile_completeness": signals.profile_completeness,
            "interview_completion_rate": signals.interview_completion_rate,
            "offer_acceptance_rate": signals.offer_acceptance_rate,
            "recruiter_saves": float(signals.recruiter_saves),
            "activity_score": signals.activity_score,
        }

    def _extract_features_batch(
        self, candidates: list[CandidateProfile]
    ) -> list[dict[str, float]]:
        """Extract features for all candidates."""
        return [
            self._extract_features(c.behavioral_signals) for c in candidates
        ]

    def _normalize(self, features: dict[str, float]) -> dict[str, float]:
        """
        Min-max normalize features using pool statistics.

        Falls back to raw values if pool stats not computed.
        """
        if self._pool_stats is None:
            # No normalization — return raw (already 0-1 for most features)
            return features

        normalized = {}
        for name, value in features.items():
            stats = self._pool_stats.get(name)
            if stats is None:
                normalized[name] = value
                continue

            range_val = stats["max"] - stats["min"]
            if range_val <= 0:
                normalized[name] = 0.5
            else:
                normalized[name] = (value - stats["min"]) / range_val

            # Clip to [0, 1]
            normalized[name] = float(np.clip(normalized[name], 0.0, 1.0))

        return normalized
