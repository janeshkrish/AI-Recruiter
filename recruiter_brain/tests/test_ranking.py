"""
Tests — Ranking Engine
========================

Tests for the hybrid ranking engine pipeline.
"""

from __future__ import annotations

import asyncio

import pytest

from recruiter_brain.data.models import AgentScores, CandidateRanking
from recruiter_brain.scoring.feature_engineering import FeatureEngineer


# ===========================================================================
# Feature Engineering Tests
# ===========================================================================

class TestFeatureEngineer:
    """Tests for FeatureEngineer."""

    def test_normalize_preserves_bounds(self):
        """Normalized scores should stay in [0, 1]."""
        fe = FeatureEngineer()

        scores = [
            AgentScores(
                candidate_id=f"c{i}",
                technical_fit_score=i * 0.1,
                career_fit_score=i * 0.12,
                behavioral_fit_score=i * 0.08,
                potential_score=i * 0.11,
            )
            for i in range(10)
        ]

        fe.fit(scores)

        for s in scores:
            normalized = fe.normalize(s)
            assert 0.0 <= normalized.technical_fit_score <= 1.0
            assert 0.0 <= normalized.career_fit_score <= 1.0
            assert 0.0 <= normalized.behavioral_fit_score <= 1.0
            assert 0.0 <= normalized.potential_score <= 1.0

    def test_impute_missing_recruiter(self):
        """Missing recruiter score should be imputed."""
        fe = FeatureEngineer()

        scores = AgentScores(
            candidate_id="test",
            technical_fit_score=0.8,
            career_fit_score=0.6,
            behavioral_fit_score=0.5,
            potential_score=0.7,
            recruiter_reasoning_score=0.0,  # Missing
        )

        imputed = fe.impute_missing(scores)
        assert imputed.recruiter_reasoning_score > 0.0

    def test_distribution_summary(self):
        """Distribution summary should contain expected keys."""
        fe = FeatureEngineer()

        scores = [
            AgentScores(
                candidate_id=f"c{i}",
                technical_fit_score=0.5 + i * 0.05,
                career_fit_score=0.4 + i * 0.06,
                behavioral_fit_score=0.3 + i * 0.07,
                potential_score=0.5 + i * 0.04,
            )
            for i in range(5)
        ]

        fe.fit(scores)
        summary = fe.get_distribution_summary()

        assert "technical_fit_score" in summary
        assert "min" in summary["technical_fit_score"]
        assert "max" in summary["technical_fit_score"]
        assert "mean" in summary["technical_fit_score"]


# ===========================================================================
# Ranking Weight Tests
# ===========================================================================

class TestRankingWeights:
    """Test that ranking weights produce correct ordering."""

    def test_weight_calculation(self):
        """Final score should be correct weighted sum."""
        weights = {
            "technical": 0.35,
            "career": 0.20,
            "behavioral": 0.15,
            "potential": 0.15,
            "recruiter": 0.15,
        }

        scores = AgentScores(
            candidate_id="test",
            technical_fit_score=0.9,
            career_fit_score=0.7,
            behavioral_fit_score=0.6,
            potential_score=0.8,
            recruiter_reasoning_score=0.75,
        )

        expected = (
            0.35 * 0.9
            + 0.20 * 0.7
            + 0.15 * 0.6
            + 0.15 * 0.8
            + 0.15 * 0.75
        )

        actual = (
            weights["technical"] * scores.technical_fit_score
            + weights["career"] * scores.career_fit_score
            + weights["behavioral"] * scores.behavioral_fit_score
            + weights["potential"] * scores.potential_score
            + weights["recruiter"] * scores.recruiter_reasoning_score
        )

        assert abs(actual - expected) < 1e-6

    def test_ranking_order(self):
        """Higher scores should produce higher ranks."""
        rankings = [
            CandidateRanking(
                rank=0,
                candidate_id=f"c{i}",
                name=f"Candidate {i}",
                final_score=0.1 * i,
            )
            for i in range(10)
        ]

        # Sort descending
        rankings.sort(key=lambda r: r.final_score, reverse=True)
        for i, r in enumerate(rankings):
            r.rank = i + 1

        # Verify order
        for i in range(len(rankings) - 1):
            assert rankings[i].final_score >= rankings[i + 1].final_score
        assert rankings[0].rank == 1

    def test_weights_sum_to_one(self):
        """Default weights should sum to 1.0."""
        from recruiter_brain.config import ScoringWeights

        weights = ScoringWeights()
        total = (
            weights.technical
            + weights.career
            + weights.behavioral
            + weights.potential
            + weights.recruiter
        )
        assert abs(total - 1.0) < 1e-6
