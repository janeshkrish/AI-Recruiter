"""
Tests — Agent Scoring Logic
=============================

Unit tests for all 6 agents' scoring logic.
"""

from __future__ import annotations

import asyncio

import pytest

from recruiter_brain.agents.behavior_agent import BehavioralIntelligenceAgent
from recruiter_brain.agents.career_agent import CareerIntelligenceAgent
from recruiter_brain.agents.potential_agent import PotentialIntelligenceAgent
from recruiter_brain.agents.recruiter_agent import RecruiterReasoningAgent
from recruiter_brain.agents.role_agent import RoleUnderstandingAgent
from recruiter_brain.data.models import (
    AgentScores,
    BehavioralSignals,
    CandidateProfile,
    CareerEntry,
    Certification,
    Education,
    RoleParsedOutput,
    Seniority,
)


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def sample_candidate() -> CandidateProfile:
    """Create a realistic test candidate."""
    return CandidateProfile(
        candidate_id="test_001",
        name="Jane Smith",
        headline="Senior ML Engineer | Python · PyTorch · NLP",
        summary="Experienced ML engineer with 6 years building production AI systems.",
        location="San Francisco, CA",
        career_history=[
            CareerEntry(
                company="StartupCo",
                title="Junior ML Engineer",
                seniority_level=Seniority.JUNIOR,
                start_date="2018-06",
                end_date="2020-03",
                duration_months=21,
                industry="Technology",
                company_tier=3,
            ),
            CareerEntry(
                company="Google",
                title="ML Engineer",
                seniority_level=Seniority.MID,
                start_date="2020-03",
                end_date="2022-06",
                duration_months=27,
                industry="Technology",
                company_tier=1,
            ),
            CareerEntry(
                company="FrontierAI Labs",
                title="Senior ML Engineer",
                seniority_level=Seniority.SENIOR,
                start_date="2022-06",
                end_date=None,
                duration_months=24,
                industry="Technology",
                is_leadership=False,
                company_tier=1,
            ),
        ],
        total_experience_years=6.0,
        current_title="Senior ML Engineer",
        current_company="FrontierAI Labs",
        skills=[
            "Python", "PyTorch", "TensorFlow", "NLP",
            "Deep Learning", "Machine Learning", "Docker",
            "Kubernetes", "AWS", "FastAPI", "SQL",
            "LLM Engineering", "RAG Systems",
        ],
        certifications=[
            Certification(name="AWS ML Specialty", issuer="AWS", year=2023),
        ],
        education=[
            Education(
                institution="Stanford University",
                degree="MS",
                field="Computer Science",
                graduation_year=2018,
                gpa=3.9,
                tier=1,
            ),
        ],
        behavioral_signals=BehavioralSignals(
            recruiter_response_rate=0.85,
            platform_engagement=0.72,
            profile_completeness=0.95,
            interview_completion_rate=0.80,
            offer_acceptance_rate=0.60,
            recruiter_saves=12,
            activity_score=0.78,
        ),
    )


@pytest.fixture
def sample_parsed_role() -> RoleParsedOutput:
    """Create a parsed JD role."""
    return RoleParsedOutput(
        must_have_skills=[
            "Python", "PyTorch", "Machine Learning", "NLP",
            "LLM Engineering", "RAG Systems",
        ],
        nice_to_have_skills=[
            "Kubernetes", "RLHF", "Fine-tuning",
        ],
        seniority="senior",
        years_experience="5+",
        leadership=0.3,
        startup_mindset=0.7,
        research_orientation=0.4,
        product_thinking=0.6,
        domain_expertise=["technology"],
        target_industry="technology",
    )


@pytest.fixture
def weak_candidate() -> CandidateProfile:
    """Create a weak candidate for comparison."""
    return CandidateProfile(
        candidate_id="test_weak",
        name="Bob Novice",
        headline="Junior Developer",
        summary="Entry-level developer looking for opportunities.",
        career_history=[
            CareerEntry(
                company="Small Shop",
                title="Junior Developer",
                seniority_level=Seniority.JUNIOR,
                start_date="2023-01",
                end_date=None,
                duration_months=12,
                industry="Retail",
                company_tier=3,
            ),
        ],
        total_experience_years=1.0,
        current_title="Junior Developer",
        current_company="Small Shop",
        skills=["JavaScript", "HTML/CSS", "React"],
        behavioral_signals=BehavioralSignals(
            recruiter_response_rate=0.2,
            platform_engagement=0.3,
            profile_completeness=0.4,
            interview_completion_rate=0.3,
            offer_acceptance_rate=0.5,
            recruiter_saves=0,
            activity_score=0.2,
        ),
    )


# ===========================================================================
# Agent 1: Role Understanding
# ===========================================================================

class TestRoleUnderstandingAgent:
    """Tests for Agent 1."""

    def test_regex_extraction(self):
        """Test regex-based JD extraction."""
        agent = RoleUnderstandingAgent()
        # Force simulation mode
        agent.settings.llm.simulation_mode = True

        jd = """
        Senior Machine Learning Engineer

        Requirements:
        - 5+ years experience in ML
        - Python, PyTorch, TensorFlow
        - NLP and deep learning expertise
        - Experience with Kubernetes

        Preferred:
        - LLM fine-tuning experience
        - Research publications

        We are a fast-paced startup looking for product-minded engineers
        who can lead technical initiatives and mentor junior team members.
        """

        result = asyncio.run(agent.parse(jd))

        assert isinstance(result, RoleParsedOutput)
        assert len(result.must_have_skills) > 0
        assert result.seniority in (
            "senior", "mid", "staff", "lead", "manager", "director",
        )
        assert result.startup_mindset > 0.3
        assert result.leadership > 0.2
        assert 0 <= result.product_thinking <= 1

    def test_empty_jd(self):
        """Test handling of empty JD."""
        agent = RoleUnderstandingAgent()
        agent.settings.llm.simulation_mode = True
        result = asyncio.run(agent.parse(""))
        assert isinstance(result, RoleParsedOutput)


# ===========================================================================
# Agent 3: Career Intelligence
# ===========================================================================

class TestCareerIntelligenceAgent:
    """Tests for Agent 3."""

    def test_score_bounds(self, sample_candidate, sample_parsed_role):
        """Scores should be between 0 and 1."""
        agent = CareerIntelligenceAgent()
        result = agent.score(sample_candidate, sample_parsed_role)

        for key, value in result.items():
            assert 0.0 <= value <= 1.0, f"{key} = {value} is out of bounds"

    def test_strong_vs_weak(
        self, sample_candidate, weak_candidate, sample_parsed_role
    ):
        """Strong candidate should score higher than weak one."""
        agent = CareerIntelligenceAgent()

        strong_scores = agent.score(sample_candidate, sample_parsed_role)
        weak_scores = agent.score(weak_candidate, sample_parsed_role)

        assert strong_scores["career_fit_score"] > weak_scores["career_fit_score"]

    def test_empty_career(self, sample_parsed_role):
        """Handle candidate with no career history."""
        candidate = CandidateProfile(
            candidate_id="empty",
            name="Empty Career",
        )
        agent = CareerIntelligenceAgent()
        result = agent.score(candidate, sample_parsed_role)
        assert result["career_fit_score"] >= 0.0

    def test_promotion_detection(self, sample_parsed_role):
        """Test that career progression is detected."""
        agent = CareerIntelligenceAgent()

        # Candidate with clear progression
        progressive = CandidateProfile(
            candidate_id="prog",
            name="Progressive",
            career_history=[
                CareerEntry(
                    company="Co1", title="Junior", seniority_level=Seniority.JUNIOR,
                    start_date="2018-01", end_date="2020-01", duration_months=24,
                ),
                CareerEntry(
                    company="Co2", title="Mid", seniority_level=Seniority.MID,
                    start_date="2020-01", end_date="2022-01", duration_months=24,
                ),
                CareerEntry(
                    company="Co3", title="Senior", seniority_level=Seniority.SENIOR,
                    start_date="2022-01", end_date=None, duration_months=24,
                ),
            ],
            total_experience_years=6,
        )

        result = agent.score(progressive, sample_parsed_role)
        assert result["promotion_score"] > 0.5


# ===========================================================================
# Agent 4: Behavioral Intelligence
# ===========================================================================

class TestBehavioralIntelligenceAgent:
    """Tests for Agent 4."""

    def test_score_bounds(self, sample_candidate):
        """Scores should be between 0 and 1."""
        agent = BehavioralIntelligenceAgent()
        result = agent.score(sample_candidate)

        assert 0.0 <= result["behavioral_fit_score"] <= 1.0

    def test_pool_normalization(self, sample_candidate, weak_candidate):
        """Pool normalization should differentiate candidates."""
        agent = BehavioralIntelligenceAgent()
        agent.compute_pool_stats([sample_candidate, weak_candidate])

        strong_score = agent.score(sample_candidate)
        weak_score = agent.score(weak_candidate)

        assert strong_score["behavioral_fit_score"] > weak_score["behavioral_fit_score"]


# ===========================================================================
# Agent 5: Potential Intelligence
# ===========================================================================

class TestPotentialIntelligenceAgent:
    """Tests for Agent 5."""

    def test_graph_built(self):
        """Skill transfer graph should have nodes and edges."""
        agent = PotentialIntelligenceAgent()
        assert agent.graph.number_of_nodes() > 50
        assert agent.graph.number_of_edges() > 100

    def test_direct_skill_match(self, sample_candidate, sample_parsed_role):
        """Candidate with matching skills should score high."""
        agent = PotentialIntelligenceAgent()
        result = agent.score(sample_candidate, sample_parsed_role)
        assert result["potential_score"] > 0.5

    def test_no_skill_match(self, sample_parsed_role):
        """Candidate with zero relevant skills should score low."""
        agent = PotentialIntelligenceAgent()
        candidate = CandidateProfile(
            candidate_id="none",
            name="No Match",
            skills=["Cooking", "Gardening", "Painting"],
        )
        result = agent.score(candidate, sample_parsed_role)
        assert result["potential_score"] < 0.3

    def test_adjacent_skills(self, sample_parsed_role):
        """Candidate with adjacent skills should get partial credit."""
        agent = PotentialIntelligenceAgent()

        # Has Python and Deep Learning but not LLM Engineering directly
        candidate = CandidateProfile(
            candidate_id="adjacent",
            name="Adjacent Skills",
            skills=["Python", "Deep Learning", "TensorFlow"],
        )

        result = agent.score(candidate, sample_parsed_role)
        assert result["potential_score"] > 0.2
        assert result["adjacent_skill_strength"] > 0.0

    def test_skill_paths(self):
        """Test skill path finding for explainability."""
        agent = PotentialIntelligenceAgent()
        paths = agent.get_skill_paths("Python", "LLM Engineering")
        assert len(paths) > 0
        assert paths[0][0] == "Python"


# ===========================================================================
# Agent 6: Recruiter Reasoning
# ===========================================================================

class TestRecruiterReasoningAgent:
    """Tests for Agent 6."""

    def test_simulation_mode(self, sample_candidate):
        """Simulation mode should return valid scores."""
        agent = RecruiterReasoningAgent()
        agent.settings.llm.simulation_mode = True

        prior = AgentScores(
            candidate_id="test",
            technical_fit_score=0.8,
            career_fit_score=0.7,
            behavioral_fit_score=0.6,
            potential_score=0.75,
        )

        result = asyncio.run(
            agent.evaluate(
                candidate=sample_candidate,
                jd_title="Senior ML Engineer",
                jd_text="Looking for ML engineer...",
                parsed_role=RoleParsedOutput(),
                prior_scores=prior,
            )
        )

        assert "score" in result
        assert 0.0 <= result["score"] <= 1.0
        assert "reasoning" in result
        assert len(result["reasoning"]) > 0
        assert "recommendation" in result
