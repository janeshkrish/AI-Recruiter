from __future__ import annotations

from typing import Any

from backend.app.repositories.candidate_repository import CandidateRepository
from backend.app.services.ranking_service import RankingService


class AnalyticsService:
    def __init__(self, repository: CandidateRepository, ranking_service: RankingService) -> None:
        self.repository = repository
        self.ranking_service = ranking_service

    def pipeline_analytics(self) -> dict[str, Any]:
        stats = self.repository.stats()
        weights = self.ranking_service.weights()
        return {
            "ranking_mode": "offline_deterministic",
            "network_required_for_ranking": False,
            "weights": weights,
            "vector_store": {
                "total_indexed": stats["indexed_candidates"],
                "dimension": "deterministic features",
                "backend": "none",
            },
            "skill_graph": {
                "total_edges": 120,
                "total_skills": 100,
                "mode": "feature ontology",
            },
            "agents": [
                {"id": "agent_a", "name": "Technical Fit", "description": "Retrieval, ranking, vector DB, Python, and evaluation evidence."},
                {"id": "agent_b", "name": "Career Intelligence", "description": "Experience band, tenure stability, product vs service background."},
                {"id": "agent_c", "name": "Behavioral Intel", "description": "Redrob response, activity, notice, relocation, and verification signals."},
                {"id": "agent_d", "name": "Potential Engine", "description": "Startup/product mindset, projects, open source, and transferable signals."},
                {"id": "agent_e", "name": "Risk Detector", "description": "Honeypots, impossible dates, keyword stuffing, and explicit JD anti-patterns."},
            ],
            "feature_groups": list(weights.keys()),
        }
