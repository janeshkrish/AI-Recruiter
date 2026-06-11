"""
Agent 5 — Potential Intelligence Agent (Differentiator)
========================================================

Builds a Skill Transfer Graph and measures adjacent skill strength
for candidates who lack exact required skills but have transferable expertise.

This is the differentiator that separates this system from keyword matching.

Examples:
    Spark → Data Engineering → ML Pipelines → AI Engineering
    Python → ML Engineering → LLM Engineering
    React → Frontend Architecture → Full Stack

Returns: potential_score (0–1) with adjacent_skill_strength.
"""

from __future__ import annotations

from typing import Optional

import networkx as nx
import numpy as np
from loguru import logger

from recruiter_brain.data.models import CandidateProfile, RoleParsedOutput


# ===========================================================================
# Skill Transfer Graph — Pre-built Taxonomy
# ===========================================================================

SKILL_TRANSFER_EDGES: list[tuple[str, str, float]] = [
    # --- Programming Language Transfers ---
    ("Python", "Machine Learning", 0.9),
    ("Python", "Data Engineering", 0.8),
    ("Python", "NLP", 0.85),
    ("Python", "Deep Learning", 0.85),
    ("Python", "LLM Engineering", 0.8),
    ("Python", "scikit-learn", 0.9),
    ("Python", "PyTorch", 0.8),
    ("Python", "TensorFlow", 0.8),
    ("Python", "FastAPI", 0.9),
    ("Python", "Django", 0.85),
    ("Python", "Flask", 0.85),
    ("R", "Machine Learning", 0.7),
    ("R", "Data Science", 0.8),
    ("R", "Statistics", 0.85),
    ("Java", "Spring Boot", 0.9),
    ("Java", "Microservices", 0.7),
    ("Java", "Apache Spark", 0.7),
    ("Java", "Apache Kafka", 0.7),
    ("JavaScript", "React", 0.9),
    ("JavaScript", "Node.js", 0.9),
    ("JavaScript", "TypeScript", 0.95),
    ("JavaScript", "Vue.js", 0.85),
    ("JavaScript", "Angular", 0.85),
    ("TypeScript", "React", 0.9),
    ("TypeScript", "Next.js", 0.9),
    ("TypeScript", "Angular", 0.85),
    ("Go", "Microservices", 0.8),
    ("Go", "Kubernetes", 0.6),
    ("Go", "Distributed Systems", 0.7),
    ("Rust", "Performance Optimization", 0.8),
    ("Rust", "Systems Programming", 0.9),
    ("Scala", "Apache Spark", 0.9),
    ("Scala", "Data Engineering", 0.8),
    ("C++", "Performance Optimization", 0.85),
    ("C++", "Computer Vision", 0.6),
    ("Kotlin", "Android Development", 0.9),
    ("Swift", "iOS Development", 0.9),

    # --- ML/AI Transfer Chains ---
    ("Machine Learning", "Deep Learning", 0.85),
    ("Machine Learning", "Feature Engineering", 0.9),
    ("Machine Learning", "MLOps", 0.7),
    ("Machine Learning", "NLP", 0.7),
    ("Machine Learning", "Computer Vision", 0.7),
    ("Machine Learning", "Reinforcement Learning", 0.6),
    ("Deep Learning", "NLP", 0.8),
    ("Deep Learning", "Computer Vision", 0.8),
    ("Deep Learning", "PyTorch", 0.9),
    ("Deep Learning", "TensorFlow", 0.9),
    ("Deep Learning", "Neural Architecture Search", 0.7),
    ("Deep Learning", "Diffusion Models", 0.7),
    ("Deep Learning", "GANs", 0.75),
    ("NLP", "LLM Engineering", 0.9),
    ("NLP", "Hugging Face Transformers", 0.9),
    ("NLP", "Prompt Engineering", 0.8),
    ("NLP", "RAG Systems", 0.8),
    ("LLM Engineering", "Prompt Engineering", 0.9),
    ("LLM Engineering", "RAG Systems", 0.9),
    ("LLM Engineering", "Fine-tuning", 0.9),
    ("LLM Engineering", "RLHF", 0.8),
    ("LLM Engineering", "LangChain", 0.85),
    ("LLM Engineering", "LlamaIndex", 0.85),
    ("Prompt Engineering", "RAG Systems", 0.8),
    ("Prompt Engineering", "LangChain", 0.8),
    ("RAG Systems", "Vector Databases", 0.9),
    ("RAG Systems", "Qdrant", 0.85),
    ("RAG Systems", "Pinecone", 0.85),
    ("RAG Systems", "Weaviate", 0.85),
    ("Fine-tuning", "RLHF", 0.8),
    ("PyTorch", "TensorFlow", 0.7),
    ("PyTorch", "Deep Learning", 0.9),
    ("scikit-learn", "Machine Learning", 0.9),
    ("scikit-learn", "Feature Engineering", 0.8),
    ("MLOps", "CI/CD", 0.7),
    ("MLOps", "Docker", 0.7),
    ("MLOps", "Kubernetes", 0.6),
    ("MLOps", "Model Optimization", 0.8),

    # --- Data Engineering Chain ---
    ("SQL", "Data Engineering", 0.7),
    ("SQL", "Data Modeling", 0.85),
    ("SQL", "PostgreSQL", 0.9),
    ("SQL", "MySQL", 0.9),
    ("SQL", "Data Warehousing", 0.8),
    ("Data Engineering", "Apache Spark", 0.9),
    ("Data Engineering", "Apache Kafka", 0.8),
    ("Data Engineering", "Apache Airflow", 0.85),
    ("Data Engineering", "ETL Pipelines", 0.9),
    ("Data Engineering", "Data Warehousing", 0.85),
    ("Data Engineering", "Data Modeling", 0.8),
    ("Data Engineering", "dbt", 0.85),
    ("Apache Spark", "Data Engineering", 0.9),
    ("Apache Spark", "Big Data", 0.9),
    ("Apache Kafka", "Event-Driven Architecture", 0.85),
    ("Apache Kafka", "Apache Flink", 0.7),
    ("Apache Airflow", "ETL Pipelines", 0.9),
    ("Data Warehousing", "Snowflake", 0.9),
    ("Data Warehousing", "BigQuery", 0.9),
    ("Data Warehousing", "Redshift", 0.9),
    ("Snowflake", "BigQuery", 0.8),
    ("Snowflake", "Redshift", 0.8),
    ("dbt", "Data Modeling", 0.85),
    ("dbt", "Data Warehousing", 0.7),

    # --- Cloud & DevOps Chain ---
    ("Docker", "Kubernetes", 0.85),
    ("Docker", "Microservices", 0.7),
    ("Docker", "CI/CD", 0.7),
    ("Kubernetes", "Helm", 0.85),
    ("Kubernetes", "ArgoCD", 0.8),
    ("Kubernetes", "Microservices", 0.7),
    ("Terraform", "CloudFormation", 0.8),
    ("Terraform", "Pulumi", 0.85),
    ("Terraform", "Ansible", 0.6),
    ("AWS", "Azure", 0.7),
    ("AWS", "GCP", 0.7),
    ("AWS", "CloudFormation", 0.8),
    ("AWS", "Serverless", 0.8),
    ("Azure", "GCP", 0.7),
    ("CI/CD", "Jenkins", 0.85),
    ("CI/CD", "GitHub Actions", 0.85),
    ("CI/CD", "ArgoCD", 0.7),
    ("Linux", "Docker", 0.6),
    ("Linux", "Nginx", 0.7),
    ("Prometheus", "Grafana", 0.9),

    # --- Frontend Chain ---
    ("React", "Next.js", 0.9),
    ("React", "React Native", 0.8),
    ("React", "Vue.js", 0.7),
    ("React", "Frontend Architecture", 0.8),
    ("Next.js", "React", 0.9),
    ("Next.js", "Full Stack", 0.7),
    ("Vue.js", "React", 0.7),
    ("Angular", "React", 0.65),
    ("Svelte", "React", 0.6),
    ("HTML/CSS", "Tailwind CSS", 0.8),
    ("HTML/CSS", "React", 0.5),
    ("Figma", "UI/UX", 0.8),
    ("GraphQL", "REST APIs", 0.7),
    ("REST APIs", "API Design", 0.9),

    # --- Backend Chain ---
    ("Node.js", "Express.js", 0.9),
    ("Node.js", "Full Stack", 0.7),
    ("FastAPI", "REST APIs", 0.9),
    ("FastAPI", "Microservices", 0.7),
    ("Django", "REST APIs", 0.8),
    ("Flask", "REST APIs", 0.85),
    ("Spring Boot", "Microservices", 0.8),
    ("gRPC", "Microservices", 0.8),
    ("Microservices", "Distributed Systems", 0.8),
    ("Microservices", "Event-Driven Architecture", 0.7),
    ("Event-Driven Architecture", "CQRS", 0.7),
    ("Domain-Driven Design", "Microservices", 0.7),
    ("System Design", "Distributed Systems", 0.85),

    # --- Database Chain ---
    ("PostgreSQL", "MySQL", 0.85),
    ("PostgreSQL", "Data Modeling", 0.7),
    ("MongoDB", "Redis", 0.5),
    ("MongoDB", "NoSQL", 0.9),
    ("Redis", "Caching", 0.9),
    ("Elasticsearch", "Search", 0.9),
    ("Elasticsearch", "Vector Databases", 0.5),

    # --- Cross-domain Transfers ---
    ("Data Engineering", "Machine Learning", 0.6),
    ("Machine Learning", "Data Science", 0.8),
    ("Data Science", "Statistics", 0.85),
    ("Backend Engineer", "Full Stack", 0.6),
    ("Frontend Engineer", "Full Stack", 0.6),
    ("DevOps Engineer", "Platform Engineering", 0.8),
    ("Platform Engineering", "SRE", 0.8),
    ("Cybersecurity", "SOC 2", 0.7),
    ("Cybersecurity", "GDPR Compliance", 0.5),
]


class PotentialIntelligenceAgent:
    """
    Agent 5: Evaluates candidate potential through skill transfer graph analysis.

    For candidates lacking exact required skills, measures how close their
    existing skills are to the required ones via graph shortest-path distances.
    """

    def __init__(self) -> None:
        self.graph = nx.DiGraph()
        self._build_graph()
        logger.info(
            f"PotentialIntelligenceAgent initialized: "
            f"{self.graph.number_of_nodes()} nodes, "
            f"{self.graph.number_of_edges()} edges"
        )

    def _build_graph(self) -> None:
        """Build the skill transfer directed graph."""
        for source, target, weight in SKILL_TRANSFER_EDGES:
            source_lower = source.lower().strip()
            target_lower = target.lower().strip()
            # Store original case as node attribute
            self.graph.add_node(source_lower, label=source)
            self.graph.add_node(target_lower, label=target)
            # Edge weight represents transfer strength (higher = easier transfer)
            # For shortest path, we want distance = 1 - strength
            self.graph.add_edge(
                source_lower,
                target_lower,
                weight=1.0 - weight,
                strength=weight,
            )
            # Add reverse edge with reduced strength
            if not self.graph.has_edge(target_lower, source_lower):
                self.graph.add_edge(
                    target_lower,
                    source_lower,
                    weight=1.0 - weight * 0.6,
                    strength=weight * 0.6,
                )

    def score(
        self,
        candidate: CandidateProfile,
        parsed_role: RoleParsedOutput,
    ) -> dict[str, float]:
        """
        Score a candidate's potential based on skill transferability.

        For each required skill the candidate doesn't have:
        - Find shortest path from any candidate skill to the required skill
        - adjacent_skill_strength = 1 / (1 + shortest_path_length)

        Args:
            candidate: The candidate profile.
            parsed_role: Parsed JD requirements.

        Returns:
            Dict with potential_score and adjacent_skill_strength.
        """
        required_skills = (
            parsed_role.must_have_skills + parsed_role.nice_to_have_skills
        )

        if not required_skills:
            return {
                "potential_score": 0.5,
                "adjacent_skill_strength": 0.5,
            }

        cand_skills_lower = {s.lower().strip() for s in candidate.skills}
        required_lower = {s.lower().strip() for s in required_skills}

        # Skills the candidate already has
        direct_matches = cand_skills_lower & required_lower
        # Skills the candidate is missing
        missing_skills = required_lower - cand_skills_lower

        if not missing_skills:
            # Candidate has all required skills
            return {
                "potential_score": 1.0,
                "adjacent_skill_strength": 1.0,
            }

        # Direct match ratio
        direct_ratio = len(direct_matches) / len(required_lower)

        # For each missing skill, compute adjacency strength
        adjacency_scores = []
        for missing_skill in missing_skills:
            strength = self._compute_adjacency(
                cand_skills_lower, missing_skill
            )
            adjacency_scores.append(strength)

        avg_adjacency = (
            float(np.mean(adjacency_scores)) if adjacency_scores else 0.0
        )

        # Potential score combines direct match and adjacency
        potential = 0.4 * direct_ratio + 0.6 * avg_adjacency

        return {
            "potential_score": round(float(np.clip(potential, 0, 1)), 4),
            "adjacent_skill_strength": round(avg_adjacency, 4),
        }

    def score_batch(
        self,
        candidates: list[CandidateProfile],
        parsed_role: RoleParsedOutput,
    ) -> list[dict[str, float]]:
        """Score multiple candidates."""
        return [self.score(c, parsed_role) for c in candidates]

    def _compute_adjacency(
        self, candidate_skills: set[str], target_skill: str
    ) -> float:
        """
        Compute how close a candidate's skills are to a target skill.

        Uses shortest path in the skill transfer graph.

        Args:
            candidate_skills: Set of candidate's skills (lowercase).
            target_skill: The missing required skill (lowercase).

        Returns:
            Adjacency strength 0–1 (1 = very close, 0 = no connection).
        """
        if target_skill not in self.graph:
            # Target skill not in graph — can only do fuzzy text matching
            return self._fuzzy_skill_match(candidate_skills, target_skill)

        best_strength = 0.0

        for cand_skill in candidate_skills:
            if cand_skill not in self.graph:
                continue

            try:
                path_length = nx.shortest_path_length(
                    self.graph,
                    source=cand_skill,
                    target=target_skill,
                    weight="weight",
                )
                # Convert distance to strength
                strength = 1.0 / (1.0 + path_length)
                best_strength = max(best_strength, strength)
            except nx.NetworkXNoPath:
                continue

        return best_strength

    def _fuzzy_skill_match(
        self, candidate_skills: set[str], target: str
    ) -> float:
        """
        Fallback fuzzy matching for skills not in the graph.

        Uses substring matching and word overlap.
        """
        target_words = set(target.split())

        best_score = 0.0
        for skill in candidate_skills:
            skill_words = set(skill.split())

            # Substring containment
            if target in skill or skill in target:
                best_score = max(best_score, 0.7)
                continue

            # Word overlap
            overlap = len(target_words & skill_words)
            total = len(target_words | skill_words)
            if total > 0:
                word_score = overlap / total * 0.5
                best_score = max(best_score, word_score)

        return best_score

    def get_skill_paths(
        self, source_skill: str, target_skill: str
    ) -> list[list[str]]:
        """
        Get all shortest paths between two skills (for explainability).

        Args:
            source_skill: Starting skill.
            target_skill: Target skill.

        Returns:
            List of skill paths (lists of skill names).
        """
        src = source_skill.lower().strip()
        tgt = target_skill.lower().strip()

        if src not in self.graph or tgt not in self.graph:
            return []

        try:
            paths = list(
                nx.all_shortest_paths(
                    self.graph, source=src, target=tgt, weight="weight"
                )
            )
            # Convert back to original case
            return [
                [
                    self.graph.nodes[n].get("label", n)
                    for n in path
                ]
                for path in paths[:5]  # Limit to 5 paths
            ]
        except nx.NetworkXNoPath:
            return []
