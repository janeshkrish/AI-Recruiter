from __future__ import annotations

import unittest


try:
    from fastapi.testclient import TestClient
    from backend.app.main import app
except Exception as exc:  # pragma: no cover - used when app deps are not installed
    TestClient = None
    app = None
    IMPORT_ERROR = exc
else:
    IMPORT_ERROR = None


@unittest.skipIf(TestClient is None, f"Backend dependencies not installed: {IMPORT_ERROR}")
class BackendApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_root_landing(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("frontend", response.json())

    def test_health_and_stats(self) -> None:
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)
        self.assertFalse(health.json()["network_required_for_ranking"])

        stats = self.client.get("/api/stats")
        self.assertEqual(stats.status_code, 200)
        self.assertGreater(stats.json()["total_applicants"], 0)

    def test_candidate_browse_and_detail(self) -> None:
        response = self.client.get("/api/candidates?page=1&limit=2")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["data"]), 2)

        candidate_id = payload["data"][0]["candidate_id"]
        detail = self.client.get(f"/api/candidates/{candidate_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.json()["candidate_id"], candidate_id)

    def test_role_ranking_response(self) -> None:
        response = self.client.get("/api/candidates/role-ranking?limit=3")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["total"], 3)
        self.assertEqual([row["rank"] for row in payload["rows"]], [1, 2, 3])
        self.assertTrue(payload["rows"][0]["candidate_id"].startswith("CAND_"))
        self.assertIn("reasoning", payload["rows"][0])

    def test_analytics_copilot_and_resume_upload(self) -> None:
        analytics = self.client.get("/api/pipeline/analytics")
        self.assertEqual(analytics.status_code, 200)
        self.assertEqual(analytics.json()["ranking_mode"], "offline_deterministic")

        copilot = self.client.post(
            "/api/copilot",
            json={"question": "Why rank 1?", "candidates": [{"candidate_id": "CAND_0000001", "rank": 1, "score": 80, "skill_match": 70, "experience_match": 65, "reasoning": "Strong Python retrieval fit."}]},
        )
        self.assertEqual(copilot.status_code, 200)
        self.assertIn("CAND_0000001", copilot.json()["answer"])

        upload = self.client.post(
            "/api/resumes/upload",
            files={"file": ("resume.txt", b"Python machine learning retrieval ranking", "text/plain")},
        )
        self.assertEqual(upload.status_code, 200)
        self.assertIn("python", upload.json()["extracted_skills"])


if __name__ == "__main__":
    unittest.main()
