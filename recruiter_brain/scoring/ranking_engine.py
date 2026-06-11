"""
Hybrid Ranking Engine
======================

Orchestrates the complete 4-stage candidate ranking pipeline:

Stage 1: Embedding Retrieval (100K → Top 2K)
Stage 2: Hybrid Scoring (2K → Top 500)
Stage 3: Recruiter Reasoning LLM (500 → Top 200)
Stage 4: Final Ranking (200 → Top 25)

Combines all agent outputs with configurable weights.
"""

from __future__ import annotations

import asyncio
import time
from typing import Optional

import numpy as np
from loguru import logger
from tqdm import tqdm

from recruiter_brain.agents.behavior_agent import BehavioralIntelligenceAgent
from recruiter_brain.agents.career_agent import CareerIntelligenceAgent
from recruiter_brain.agents.potential_agent import PotentialIntelligenceAgent
from recruiter_brain.agents.recruiter_agent import RecruiterReasoningAgent
from recruiter_brain.agents.role_agent import RoleUnderstandingAgent
from recruiter_brain.agents.technical_agent import TechnicalCapabilityAgent
from recruiter_brain.config import get_settings
from recruiter_brain.data.models import (
    AgentScores,
    CandidateProfile,
    CandidateRanking,
    RankResponse,
    RoleParsedOutput,
)
from recruiter_brain.embeddings.embedding_service import EmbeddingService
from recruiter_brain.embeddings.vector_store import QdrantVectorStore
from recruiter_brain.scoring.feature_engineering import FeatureEngineer


class HybridRankingEngine:
    """
    Orchestrates the full multi-agent ranking pipeline.

    Manages all agents, the vector store, and the 4-stage
    funnel from 100K candidates down to the final top 25.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.weights = self.settings.weights.as_dict

        # Initialize agents
        self.role_agent = RoleUnderstandingAgent()
        self.embedding_service = EmbeddingService()
        self.technical_agent = TechnicalCapabilityAgent(self.embedding_service)
        self.career_agent = CareerIntelligenceAgent()
        self.behavioral_agent = BehavioralIntelligenceAgent()
        self.potential_agent = PotentialIntelligenceAgent()
        self.recruiter_agent = RecruiterReasoningAgent()

        # Infrastructure
        self.vector_store = QdrantVectorStore(
            dimension=self.embedding_service.dimension
        )
        self.feature_engineer = FeatureEngineer()

        # State
        self._candidates: dict[str, CandidateProfile] = {}
        self._embeddings: dict[str, np.ndarray] = {}
        self._scores: dict[str, AgentScores] = {}

        logger.info("HybridRankingEngine initialized")

    def index_candidates(
        self,
        candidates: list[CandidateProfile],
        batch_size: int = 256,
    ) -> int:
        """
        Index all candidates: generate embeddings and store in Qdrant.

        Args:
            candidates: Full candidate pool.
            batch_size: Batch size for embedding generation.

        Returns:
            Number of candidates indexed.
        """
        logger.info(f"Indexing {len(candidates):,} candidates...")
        start = time.time()

        # Store candidates in memory for lookup
        for c in candidates:
            self._candidates[c.candidate_id] = c

        # Create collection
        self.vector_store.create_collection(recreate=True)

        # Generate embeddings in batches
        all_ids = []
        all_embeddings = []
        all_metadata = []

        for i in tqdm(
            range(0, len(candidates), batch_size),
            desc="Embedding candidates",
        ):
            batch = candidates[i : i + batch_size]
            texts = [c.unified_text for c in batch]

            # Generate embeddings
            embeddings = self.embedding_service.encode(
                texts, batch_size=batch_size
            )

            for j, candidate in enumerate(batch):
                cid = candidate.candidate_id
                emb = embeddings[j]

                all_ids.append(cid)
                all_embeddings.append(emb)
                all_metadata.append({
                    "name": candidate.name,
                    "headline": candidate.headline,
                    "current_title": candidate.current_title,
                    "current_company": candidate.current_company,
                    "experience_years": candidate.total_experience_years,
                    "location": candidate.location,
                    "skills": candidate.skills[:10],
                    "seniority": (
                        candidate.career_history[-1].seniority_level.value
                        if candidate.career_history
                        else "mid"
                    ),
                })

                # Cache embedding
                self._embeddings[cid] = emb

        # Upsert to Qdrant
        emb_matrix = np.stack(all_embeddings)
        self.vector_store.upsert_batch(all_ids, emb_matrix, all_metadata)

        elapsed = time.time() - start
        logger.info(
            f"✓ Indexed {len(candidates):,} candidates in {elapsed:.1f}s "
            f"({len(candidates) / elapsed:.0f} candidates/sec)"
        )

        # Pre-compute behavioral stats
        self.behavioral_agent.compute_pool_stats(candidates)

        return len(candidates)

    async def rank(
        self,
        job_description: str,
        job_title: str = "",
        top_k: int = 25,
        custom_weights: Optional[dict[str, float]] = None,
    ) -> RankResponse:
        """
        Execute the full 4-stage ranking pipeline.

        Args:
            job_description: Raw JD text.
            job_title: Job title.
            top_k: Number of final candidates.
            custom_weights: Override default scoring weights.

        Returns:
            RankResponse with ranked candidates and pipeline stats.
        """
        weights = custom_weights or self.weights
        pipeline = self.settings.pipeline
        total_start = time.time()

        logger.info("=" * 60)
        logger.info("STARTING RANKING PIPELINE")
        logger.info("=" * 60)

        # ---- Stage 0: Parse Job Description ----
        logger.info("Stage 0: Parsing job description...")
        parsed_role = await self.role_agent.parse(job_description)
        logger.info(
            f"  → {len(parsed_role.must_have_skills)} must-have, "
            f"{len(parsed_role.nice_to_have_skills)} nice-to-have skills"
        )

        # Prepare technical agent with JD
        self.technical_agent.prepare_jd(job_description, parsed_role)

        # ---- Stage 1: Embedding Retrieval (→ Top 2K) ----
        logger.info(f"Stage 1: Vector retrieval → top {pipeline.stage1_top_k}...")
        stage1_start = time.time()

        jd_embedding = self.embedding_service.encode_queries(job_description)[0]
        search_results = self.vector_store.search(
            query_vector=jd_embedding,
            top_k=pipeline.stage1_top_k,
        )

        stage1_ids = [r["candidate_id"] for r in search_results]
        stage1_candidates = [
            self._candidates[cid]
            for cid in stage1_ids
            if cid in self._candidates
        ]

        logger.info(
            f"  → {len(stage1_candidates)} candidates retrieved "
            f"({time.time() - stage1_start:.1f}s)"
        )

        # ---- Stage 2: Multi-Agent Scoring (→ Top 500) ----
        logger.info(f"Stage 2: Multi-agent scoring → top {pipeline.stage2_top_k}...")
        stage2_start = time.time()

        stage2_scores = []
        for candidate in tqdm(stage1_candidates, desc="Scoring candidates"):
            cid = candidate.candidate_id

            # Agent 2: Technical
            emb = self._embeddings.get(cid)
            tech_scores = self.technical_agent.score_candidate(candidate, emb)

            # Agent 3: Career
            career_scores = self.career_agent.score(candidate, parsed_role)

            # Agent 4: Behavioral
            behav_scores = self.behavioral_agent.score(candidate)

            # Agent 5: Potential
            potential_scores = self.potential_agent.score(candidate, parsed_role)

            # Aggregate
            agent_scores = AgentScores(
                candidate_id=cid,
                technical_fit_score=tech_scores["technical_fit_score"],
                career_fit_score=career_scores["career_fit_score"],
                behavioral_fit_score=behav_scores["behavioral_fit_score"],
                potential_score=potential_scores["potential_score"],
                cosine_similarity=tech_scores.get("cosine_similarity", 0),
                semantic_overlap=tech_scores.get("semantic_overlap", 0),
                skill_overlap=tech_scores.get("skill_overlap", 0),
                promotion_score=career_scores.get("promotion_score", 0),
                career_growth_score=career_scores.get("career_growth_score", 0),
                industry_match_score=career_scores.get("industry_match_score", 0),
                leadership_score=career_scores.get("leadership_score", 0),
                stability_score=career_scores.get("stability_score", 0),
                adjacent_skill_strength=potential_scores.get(
                    "adjacent_skill_strength", 0
                ),
            )

            self._scores[cid] = agent_scores
            stage2_scores.append(agent_scores)

        # Compute stage 2 ranking (without recruiter reasoning)
        stage2_ranked = sorted(
            stage2_scores,
            key=lambda s: (
                weights["technical"] * s.technical_fit_score
                + weights["career"] * s.career_fit_score
                + weights["behavioral"] * s.behavioral_fit_score
                + weights["potential"] * s.potential_score
            ),
            reverse=True,
        )[: pipeline.stage2_top_k]

        stage2_ids = {s.candidate_id for s in stage2_ranked}
        logger.info(
            f"  → {len(stage2_ranked)} candidates scored "
            f"({time.time() - stage2_start:.1f}s)"
        )

        # ---- Stage 3: Recruiter Reasoning (→ Top 200) ----
        logger.info(f"Stage 3: LLM recruiter reasoning → top {pipeline.stage3_top_k}...")
        stage3_start = time.time()

        # Get candidates for LLM evaluation
        stage3_candidates = [
            self._candidates[s.candidate_id]
            for s in stage2_ranked
            if s.candidate_id in self._candidates
        ]
        stage3_scores_list = stage2_ranked

        # Run recruiter reasoning on all stage 2 candidates
        for i, (candidate, scores) in enumerate(
            zip(stage3_candidates, stage3_scores_list)
        ):
            eval_result = await self.recruiter_agent.evaluate(
                candidate=candidate,
                jd_title=job_title,
                jd_text=job_description,
                parsed_role=parsed_role,
                prior_scores=scores,
            )
            scores.recruiter_reasoning_score = eval_result["score"]
            scores.recruiter_reasoning_text = eval_result.get("reasoning", "")

            if (i + 1) % 50 == 0:
                logger.info(f"  Evaluated {i + 1}/{len(stage3_candidates)}")

        logger.info(
            f"  → Recruiter reasoning complete "
            f"({time.time() - stage3_start:.1f}s)"
        )

        # ---- Stage 4: Final Ranking (→ Top 25) ----
        logger.info(f"Stage 4: Final ranking → top {top_k}...")

        # Fit feature engineer on all scores
        all_scores = list(self._scores.values())
        self.feature_engineer.fit(all_scores)

        # Compute final scores
        final_rankings: list[CandidateRanking] = []

        for scores in stage2_ranked:
            cid = scores.candidate_id
            candidate = self._candidates.get(cid)
            if not candidate:
                continue

            # Impute missing scores
            scores = self.feature_engineer.impute_missing(scores)

            # Final weighted score
            final_score = (
                weights["technical"] * scores.technical_fit_score
                + weights["career"] * scores.career_fit_score
                + weights["behavioral"] * scores.behavioral_fit_score
                + weights["potential"] * scores.potential_score
                + weights["recruiter"] * scores.recruiter_reasoning_score
            )

            # Determine stage reached
            stage = 4 if scores.recruiter_reasoning_score > 0 else 2

            ranking = CandidateRanking(
                rank=0,  # Will be set after sorting
                candidate_id=cid,
                name=candidate.name,
                headline=candidate.headline,
                current_title=candidate.current_title,
                current_company=candidate.current_company,
                final_score=round(final_score, 4),
                scores=scores,
                stage_reached=stage,
            )
            final_rankings.append(ranking)

        # Sort by final score
        final_rankings.sort(key=lambda r: r.final_score, reverse=True)

        # Assign ranks and trim
        for i, r in enumerate(final_rankings):
            r.rank = i + 1

        top_rankings = final_rankings[:top_k]

        elapsed = time.time() - total_start
        logger.info("=" * 60)
        logger.info(
            f"PIPELINE COMPLETE in {elapsed:.1f}s — "
            f"Top {len(top_rankings)} candidates ranked"
        )
        logger.info("=" * 60)

        return RankResponse(
            job_id="jd_live",
            parsed_role=parsed_role,
            rankings=top_rankings,
            total_candidates_processed=len(self._candidates),
            pipeline_stages={
                "total_candidates": len(self._candidates),
                "stage1_retrieved": len(stage1_candidates),
                "stage2_scored": len(stage2_ranked),
                "stage3_llm_evaluated": len(stage3_candidates),
                "stage4_final": len(top_rankings),
            },
        )

    def get_candidate_scores(self, candidate_id: str) -> Optional[AgentScores]:
        """Get cached scores for a specific candidate."""
        return self._scores.get(candidate_id)

    def get_candidate(self, candidate_id: str) -> Optional[CandidateProfile]:
        """Get a candidate profile by ID."""
        return self._candidates.get(candidate_id)


# ---------------------------------------------------------------------------
# CLI entry point for standalone pipeline execution
# ---------------------------------------------------------------------------

async def run_pipeline(
    num_candidates: int = 1000,
    jd_index: int = 0,
) -> RankResponse:
    """
    Run the full pipeline with synthetic data.

    Args:
        num_candidates: Number of candidates to generate/load.
        jd_index: Which sample JD to use (0-4).

    Returns:
        RankResponse with results.
    """
    from recruiter_brain.data.generate_synthetic_data import (
        generate_sample_job_descriptions,
        load_candidates,
    )

    # Load data
    candidates = load_candidates(limit=num_candidates)
    jds = generate_sample_job_descriptions()
    jd = jds[jd_index]

    # Initialize engine
    engine = HybridRankingEngine()

    # Index candidates
    engine.index_candidates(candidates)

    # Run ranking
    result = await engine.rank(
        job_description=jd.description,
        job_title=jd.title,
    )

    # Print results
    print("\n" + "=" * 80)
    print(f"JOB: {jd.title} at {jd.company}")
    print("=" * 80)
    print(f"\nParsed Requirements:")
    print(f"  Must-have: {', '.join(result.parsed_role.must_have_skills[:10])}")
    print(f"  Nice-to-have: {', '.join(result.parsed_role.nice_to_have_skills[:5])}")
    print(f"  Seniority: {result.parsed_role.seniority}")
    print(f"\nPipeline Stages: {result.pipeline_stages}")
    print(f"\n{'Rank':<6}{'Name':<25}{'Title':<30}{'Score':<8}{'Tech':<7}{'Career':<8}{'Behav':<7}{'Potent':<7}{'LLM':<7}")
    print("-" * 105)

    for r in result.rankings:
        print(
            f"{r.rank:<6}{r.name:<25}{r.current_title:<30}"
            f"{r.final_score:<8.3f}"
            f"{r.scores.technical_fit_score:<7.3f}"
            f"{r.scores.career_fit_score:<8.3f}"
            f"{r.scores.behavioral_fit_score:<7.3f}"
            f"{r.scores.potential_score:<7.3f}"
            f"{r.scores.recruiter_reasoning_score:<7.3f}"
        )

    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run ranking pipeline")
    parser.add_argument("-n", "--num-candidates", type=int, default=1000)
    parser.add_argument("-j", "--jd-index", type=int, default=0)
    args = parser.parse_args()

    asyncio.run(run_pipeline(args.num_candidates, args.jd_index))
