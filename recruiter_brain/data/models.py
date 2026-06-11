"""
AI Recruiter Brain — Data Models
=================================

Pydantic models for all data structures used across the system.
These provide validation, serialization, and documentation for
candidate profiles, job descriptions, agent outputs, and rankings.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


# ===========================================================================
# Enums
# ===========================================================================

class Seniority(str, Enum):
    """Standardized seniority levels."""
    INTERN = "intern"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    STAFF = "staff"
    PRINCIPAL = "principal"
    LEAD = "lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    VP = "vp"
    C_LEVEL = "c_level"


class EmploymentType(str, Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    FREELANCE = "freelance"
    INTERNSHIP = "internship"


# ===========================================================================
# Candidate Profile Components
# ===========================================================================

class CareerEntry(BaseModel):
    """A single position in a candidate's career history."""
    company: str
    title: str
    seniority_level: Seniority = Seniority.MID
    start_date: str  # ISO format YYYY-MM
    end_date: Optional[str] = None  # None = current role
    duration_months: int = 0
    industry: str = ""
    description: str = ""
    is_leadership: bool = False
    employment_type: EmploymentType = EmploymentType.FULL_TIME
    company_size: str = ""  # "startup", "mid", "enterprise"
    company_tier: int = 3  # 1=FAANG/top-tier, 2=well-known, 3=other


class Education(BaseModel):
    """Educational background entry."""
    institution: str
    degree: str  # "BS", "MS", "PhD", "MBA", etc.
    field: str
    graduation_year: int = 2020
    gpa: Optional[float] = None
    tier: int = 3  # 1=top-20, 2=well-known, 3=other


class Certification(BaseModel):
    """Professional certification."""
    name: str
    issuer: str
    year: int = 2023
    relevance_score: float = 0.5  # 0-1


class BehavioralSignals(BaseModel):
    """Platform behavioral metrics for a candidate."""
    recruiter_response_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    platform_engagement: float = Field(default=0.5, ge=0.0, le=1.0)
    profile_completeness: float = Field(default=0.5, ge=0.0, le=1.0)
    interview_completion_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    offer_acceptance_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    recruiter_saves: int = Field(default=0, ge=0)
    activity_score: float = Field(default=0.5, ge=0.0, le=1.0)
    last_active_days_ago: int = Field(default=30, ge=0)


class CandidateProfile(BaseModel):
    """Complete candidate profile with all dimensions."""
    candidate_id: str
    name: str
    headline: str = ""
    summary: str = ""
    location: str = ""
    email: str = ""

    # Professional history
    career_history: list[CareerEntry] = Field(default_factory=list)
    total_experience_years: float = 0.0
    current_title: str = ""
    current_company: str = ""

    # Skills & qualifications
    skills: list[str] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)

    # Behavioral
    behavioral_signals: BehavioralSignals = Field(
        default_factory=BehavioralSignals
    )

    # Metadata
    tags: list[str] = Field(default_factory=list)
    source: str = "synthetic"

    @property
    def unified_text(self) -> str:
        """Create unified text representation for embedding."""
        parts = [
            self.headline,
            self.summary,
        ]
        # Add career descriptions
        for entry in self.career_history:
            parts.append(
                f"{entry.title} at {entry.company}: {entry.description}"
            )
        # Skills
        if self.skills:
            parts.append("Skills: " + ", ".join(self.skills))
        # Certifications
        for cert in self.certifications:
            parts.append(f"Certified: {cert.name} by {cert.issuer}")
        # Projects
        for project in self.projects:
            parts.append(f"Project: {project}")
        # Education
        for edu in self.education:
            parts.append(f"{edu.degree} in {edu.field} from {edu.institution}")

        return " . ".join(p for p in parts if p)


# ===========================================================================
# Job Description
# ===========================================================================

class JobDescription(BaseModel):
    """Raw job description input."""
    job_id: str = "jd_001"
    title: str
    company: str = ""
    description: str
    industry: str = ""
    location: str = ""
    seniority: str = ""
    employment_type: str = "full_time"


# ===========================================================================
# Agent Outputs
# ===========================================================================

class RoleParsedOutput(BaseModel):
    """Output of Agent 1 — Role Understanding Agent."""
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    seniority: str = ""
    years_experience: str = ""
    leadership: float = Field(default=0.0, ge=0.0, le=1.0)
    startup_mindset: float = Field(default=0.0, ge=0.0, le=1.0)
    research_orientation: float = Field(default=0.0, ge=0.0, le=1.0)
    product_thinking: float = Field(default=0.0, ge=0.0, le=1.0)
    domain_expertise: list[str] = Field(default_factory=list)
    behavioral_expectations: list[str] = Field(default_factory=list)
    target_industry: str = ""


class AgentScores(BaseModel):
    """All agent scores for a single candidate."""
    candidate_id: str
    technical_fit_score: float = Field(default=0.0, ge=0.0, le=1.0)
    career_fit_score: float = Field(default=0.0, ge=0.0, le=1.0)
    behavioral_fit_score: float = Field(default=0.0, ge=0.0, le=1.0)
    potential_score: float = Field(default=0.0, ge=0.0, le=1.0)
    recruiter_reasoning_score: float = Field(default=0.0, ge=0.0, le=1.0)
    recruiter_reasoning_text: str = ""

    # Sub-scores for explainability
    cosine_similarity: float = 0.0
    semantic_overlap: float = 0.0
    skill_overlap: float = 0.0
    promotion_score: float = 0.0
    career_growth_score: float = 0.0
    industry_match_score: float = 0.0
    leadership_score: float = 0.0
    stability_score: float = 0.0
    adjacent_skill_strength: float = 0.0


class CandidateRanking(BaseModel):
    """A ranked candidate with final score and all sub-scores."""
    rank: int
    candidate_id: str
    name: str
    headline: str = ""
    current_title: str = ""
    current_company: str = ""
    final_score: float = 0.0
    scores: AgentScores = Field(default_factory=lambda: AgentScores(candidate_id=""))
    stage_reached: int = 1  # Which pipeline stage this candidate reached


class Explanation(BaseModel):
    """Explainability output for a shortlisted candidate."""
    candidate_id: str
    candidate_name: str
    why_matched: str = ""
    strengths: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    growth_potential: str = ""
    recruiter_notes: str = ""
    confidence: float = 0.0


# ===========================================================================
# API Models
# ===========================================================================

class RankRequest(BaseModel):
    """Request body for the /api/rank endpoint."""
    job_description: str
    job_title: str = ""
    company: str = ""
    industry: str = ""
    top_k: int = 25
    weights: Optional[dict[str, float]] = None


class RankResponse(BaseModel):
    """Response body for the /api/rank endpoint."""
    job_id: str
    parsed_role: RoleParsedOutput
    rankings: list[CandidateRanking]
    total_candidates_processed: int
    pipeline_stages: dict[str, int]  # stage_name -> candidates remaining


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    version: str = "1.0.0"
    qdrant_connected: bool = False
    model_loaded: bool = False
    candidates_indexed: int = 0
