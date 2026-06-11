"""
Skill Transfer Graph
====================

A unique intelligence module that understands skill adjacency.
Instead of punishing candidates for missing an exact keyword, this engine 
calculates transferability (e.g. PyTorch -> TensorFlow -> Keras).
"""

from __future__ import annotations

import networkx as nx
from typing import Any


class SkillTransferGraph:
    """Evaluates candidates based on adjacent and transferable skills."""

    def __init__(self):
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self):
        """Builds a lightweight taxonomy of AI/ML and Data skills."""
        edges = [
            # ML Frameworks
            ("pytorch", "tensorflow", 0.8),
            ("pytorch", "keras", 0.7),
            ("tensorflow", "keras", 0.9),
            ("pytorch", "jax", 0.6),
            
            # NLP & LLMs
            ("nlp", "llms", 0.8),
            ("transformers", "llms", 0.9),
            ("huggingface", "llms", 0.8),
            ("bert", "transformers", 0.9),
            ("gpt", "llms", 0.9),
            ("fine-tuning", "llms", 0.8),
            ("lora", "fine-tuning", 0.9),
            ("rag", "llms", 0.8),
            ("vector databases", "rag", 0.8),
            ("faiss", "vector databases", 0.9),
            ("pinecone", "vector databases", 0.9),
            ("qdrant", "vector databases", 0.9),
            ("embeddings", "sentence-transformers", 0.9),
            
            # Data Engineering
            ("spark", "hadoop", 0.7),
            ("pyspark", "spark", 0.9),
            ("airflow", "data engineering", 0.8),
            ("kafka", "data streaming", 0.9),
            
            # General
            ("machine learning", "deep learning", 0.7),
            ("data science", "machine learning", 0.6),
            ("python", "machine learning", 0.4),
        ]
        
        for n1, n2, weight in edges:
            self.graph.add_edge(n1, n2, weight=weight)

    def calculate_transferability(self, candidate_skills: list[str], required_skills: list[str]) -> tuple[float, list[str]]:
        """
        Calculate how well candidate skills map to required skills.
        Returns:
            (transfer_score 0-1, list of adjacent matches found)
        """
        if not required_skills:
            return 1.0, []
            
        c_skills = [s.lower().strip() for s in candidate_skills]
        req_skills = [s.lower().strip() for s in required_skills]
        
        total_score = 0.0
        adjacent_matches = []
        
        for req in req_skills:
            best_match = 0.0
            best_adjacent = None
            
            for c_skill in c_skills:
                # Exact match
                if req == c_skill or req in c_skill or c_skill in req:
                    best_match = 1.0
                    break
                    
                # Graph Transferability Match
                if self.graph.has_node(req) and self.graph.has_node(c_skill):
                    try:
                        # Find shortest path length considering weights
                        path = nx.shortest_path(self.graph, source=c_skill, target=req, weight=None)
                        if len(path) == 2:  # direct neighbor
                            weight = self.graph[c_skill][req]['weight']
                            if weight > best_match:
                                best_match = weight
                                best_adjacent = f"{c_skill} -> {req}"
                        elif len(path) == 3:  # 2 hops away
                            # Diminish score by 0.5 for 2 hops
                            weight = 0.5
                            if weight > best_match:
                                best_match = weight
                                best_adjacent = f"{c_skill} -> (transfer) -> {req}"
                    except nx.NetworkXNoPath:
                        pass
                        
            total_score += best_match
            if best_adjacent and best_match < 1.0:
                adjacent_matches.append(best_adjacent)
                
        final_score = total_score / len(req_skills)
        return min(1.0, final_score), adjacent_matches
