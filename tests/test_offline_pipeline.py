from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

from src.feature_engineering.features import FeatureEngineer
from src.parser.candidate_profile_parser import CandidateProfileParser
from src.parser.jd_analyzer import JDAnalyzer
from src.ranking.ranker import OfflineRanker
from src.validation.honeypot_detector import HoneypotDetector
from src.validation.submission_validator import SubmissionValidator


def candidate_record(candidate_id: str, *, title: str = "Senior ML Engineer", years: float = 6.0) -> dict:
    return {
        "candidate_id": candidate_id,
        "profile": {
            "anonymized_name": "Candidate",
            "headline": "Production ML retrieval engineer",
            "summary": "Built production embeddings, hybrid retrieval, ranking, and evaluation systems in Python.",
            "location": "Pune",
            "country": "India",
            "years_of_experience": years,
            "current_title": title,
            "current_company": "ProductCo",
            "current_company_size": "201-500",
            "current_industry": "SaaS",
        },
        "career_history": [
            {
                "company": "ProductCo",
                "title": title,
                "start_date": "2021-01-01",
                "end_date": None,
                "duration_months": 65,
                "is_current": True,
                "industry": "SaaS",
                "company_size": "201-500",
                "description": "Owned production Python ranker with embeddings, vector database, BM25 hybrid search, NDCG evaluation, and A/B tests.",
            }
        ],
        "education": [
            {
                "institution": "Institute",
                "degree": "B.Tech",
                "field_of_study": "Computer Science",
                "start_year": 2014,
                "end_year": 2018,
                "grade": "8.2 CGPA",
                "tier": "tier_2",
            }
        ],
        "skills": [
            {"name": "Python", "proficiency": "expert", "endorsements": 40, "duration_months": 65},
            {"name": "Information Retrieval", "proficiency": "advanced", "endorsements": 20, "duration_months": 48},
            {"name": "Learning to Rank", "proficiency": "advanced", "endorsements": 18, "duration_months": 36},
            {"name": "Qdrant", "proficiency": "advanced", "endorsements": 12, "duration_months": 30},
            {"name": "NDCG", "proficiency": "advanced", "endorsements": 10, "duration_months": 24},
        ],
        "certifications": [{"name": "Machine Learning Engineering", "issuer": "Local", "year": 2025}],
        "projects": [{"name": "Hybrid ranker", "description": "Production vector search project with offline evaluation."}],
        "languages": [{"language": "English", "proficiency": "professional"}],
        "redrob_signals": {
            "profile_completeness_score": 95,
            "signup_date": "2025-01-01",
            "last_active_date": "2026-06-15",
            "open_to_work_flag": True,
            "profile_views_received_30d": 20,
            "applications_submitted_30d": 2,
            "recruiter_response_rate": 0.8,
            "avg_response_time_hours": 12,
            "skill_assessment_scores": {"Python": 88, "Information Retrieval": 82},
            "connection_count": 400,
            "endorsements_received": 90,
            "notice_period_days": 30,
            "expected_salary_range_inr_lpa": {"min": 30, "max": 45},
            "preferred_work_mode": "hybrid",
            "willing_to_relocate": False,
            "github_activity_score": 80,
            "search_appearance_30d": 200,
            "saved_by_recruiters_30d": 6,
            "interview_completion_rate": 0.9,
            "offer_acceptance_rate": 0.7,
            "verified_email": True,
            "verified_phone": True,
            "linkedin_connected": True,
        },
    }


class OfflinePipelineTests(unittest.TestCase):
    def test_parser_preserves_required_sections(self) -> None:
        parsed = CandidateProfileParser().parse_record(candidate_record("CAND_0000001"))
        self.assertEqual(parsed.candidate_id, "CAND_0000001")
        self.assertTrue(parsed.career_history)
        self.assertTrue(parsed.education)
        self.assertTrue(parsed.skills)
        self.assertTrue(parsed.certifications)
        self.assertTrue(parsed.projects)
        self.assertTrue(parsed.languages)
        self.assertIn("skill assessment scores", parsed.recruiter_signal_text)

    def test_feature_engineering_has_required_surface(self) -> None:
        jd = JDAnalyzer().analyze(None)
        parsed = CandidateProfileParser().parse_record(candidate_record("CAND_0000002"))
        features = FeatureEngineer().transform(parsed, jd)
        self.assertGreaterEqual(len(features.values), 100)
        for key in (
            "production_ai_months",
            "years_in_ai",
            "years_in_product_companies",
            "retrieval_months",
            "ranking_months",
            "github_activity_score",
            "notice_period_days",
            "consulting_only_flag",
            "langchain_only_flag",
            "computer_vision_only_flag",
        ):
            self.assertIn(key, features.values)

    def test_honeypot_penalizes_impossible_profile(self) -> None:
        record = candidate_record("CAND_0000003", years=1.0)
        record["career_history"][0]["start_date"] = "2025-01-01"
        record["career_history"][0]["end_date"] = "2024-01-01"
        for index in range(5):
            record["skills"].append({"name": f"Expert Skill {index}", "proficiency": "expert", "endorsements": 1, "duration_months": 0})
        parsed = CandidateProfileParser().parse_record(record)
        result = HoneypotDetector().evaluate(parsed)
        self.assertLess(result.penalty, 1.0)
        self.assertTrue(result.flags)

    def test_ranker_is_deterministic_and_tie_breaks_by_id(self) -> None:
        base = candidate_record("CAND_0000010")
        same = candidate_record("CAND_0000009")
        rows = OfflineRanker().rank_records([base, same], top_n=2)
        self.assertEqual([row["candidate_id"] for row in rows], ["CAND_0000009", "CAND_0000010"])
        self.assertEqual([row["rank"] for row in rows], [1, 2])
        self.assertIn("JD match", rows[0]["reasoning"])

    def test_submission_validator_accepts_valid_csv_and_repo(self) -> None:
        rows = [["candidate_id", "rank", "score", "reasoning"]]
        for index in range(1, 101):
            rows.append([f"CAND_{index:07d}", str(index), f"{1 - index / 1000:.4f}", "Deterministic evidence."])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "submission.csv"
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.writer(handle)
                writer.writerows(rows)
            self.assertEqual(SubmissionValidator().validate_csv(path), [])
        self.assertEqual(SubmissionValidator().validate_repository(Path(__file__).resolve().parents[1]), [])


if __name__ == "__main__":
    unittest.main()
