"""
Data Models
===========

Pydantic models mapping directly to the actual dataset schema (candidate_schema.json).
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class ProfileData(BaseModel):
    anonymized_name: str
    headline: str = ""
    summary: str = ""
    location: str = ""
    country: str = ""
    years_of_experience: float = 0.0
    current_title: str = ""
    current_company: str = ""
    current_company_size: str = ""
    current_industry: str = ""


class CareerEntry(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: Optional[str] = None
    duration_months: int = 0
    is_current: bool = False
    industry: str = ""
    company_size: str = ""
    description: str = ""


class EducationEntry(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    start_year: int
    end_year: int
    grade: Optional[str] = None
    tier: str = "unknown"


class SkillEntry(BaseModel):
    name: str
    proficiency: str
    endorsements: int = 0
    duration_months: int = 0


class CertificationEntry(BaseModel):
    name: str
    issuer: str
    year: int


class LanguageEntry(BaseModel):
    language: str
    proficiency: str


class ExpectedSalary(BaseModel):
    min: float
    max: float


class RedrobSignals(BaseModel):
    profile_completeness_score: float = 0.0
    signup_date: str = ""
    last_active_date: str = ""
    open_to_work_flag: bool = False
    profile_views_received_30d: int = 0
    applications_submitted_30d: int = 0
    recruiter_response_rate: float = 0.0
    avg_response_time_hours: float = 0.0
    skill_assessment_scores: dict[str, float] = Field(default_factory=dict)
    connection_count: int = 0
    endorsements_received: int = 0
    notice_period_days: int = 0
    expected_salary_range_inr_lpa: Optional[ExpectedSalary] = None
    preferred_work_mode: str = "hybrid"
    willing_to_relocate: bool = False
    github_activity_score: float = -1.0
    search_appearance_30d: int = 0
    saved_by_recruiters_30d: int = 0
    interview_completion_rate: float = 0.0
    offer_acceptance_rate: float = -1.0
    verified_email: bool = False
    verified_phone: bool = False
    linkedin_connected: bool = False


class CandidateProfile(BaseModel):
    """Root model representing a single line from candidates.jsonl."""
    candidate_id: str
    profile: ProfileData
    career_history: list[CareerEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    skills: list[SkillEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    languages: list[LanguageEntry] = Field(default_factory=list)
    redrob_signals: RedrobSignals = Field(default_factory=RedrobSignals)
