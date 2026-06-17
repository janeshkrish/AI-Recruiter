"""
Skill Transfer Graph
====================

A unique intelligence module that understands skill adjacency.
Instead of punishing candidates for missing an exact keyword, this engine 
calculates transferability (e.g. PyTorch -> TensorFlow -> Keras).

Expanded to 120+ edges covering AI/ML, NLP/LLM, Data Engineering,
DevOps, Web, Backend, and cross-domain transfer paths.
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
        """Builds a comprehensive taxonomy of tech skills with transfer weights."""
        edges = [
            # ================================================================
            # ML / Deep Learning Frameworks
            # ================================================================
            ("pytorch", "tensorflow", 0.8),
            ("pytorch", "keras", 0.7),
            ("tensorflow", "keras", 0.9),
            ("pytorch", "jax", 0.6),
            ("tensorflow", "jax", 0.5),
            ("keras", "tensorflow", 0.9),
            ("pytorch", "mxnet", 0.5),
            ("scikit-learn", "machine learning", 0.8),
            ("xgboost", "machine learning", 0.7),
            ("lightgbm", "xgboost", 0.9),
            ("catboost", "xgboost", 0.85),
            ("xgboost", "learning-to-rank", 0.7),
            
            # ================================================================
            # NLP & LLMs (Critical for this JD)
            # ================================================================
            ("nlp", "llms", 0.8),
            ("nlp", "text mining", 0.7),
            ("nlp", "information retrieval", 0.8),
            ("transformers", "llms", 0.9),
            ("huggingface", "transformers", 0.9),
            ("huggingface", "llms", 0.8),
            ("bert", "transformers", 0.9),
            ("gpt", "llms", 0.9),
            ("llama", "llms", 0.85),
            ("claude", "llms", 0.85),
            ("gemini", "llms", 0.85),
            ("fine-tuning", "llms", 0.8),
            ("lora", "fine-tuning", 0.9),
            ("qlora", "fine-tuning", 0.9),
            ("qlora", "lora", 0.95),
            ("peft", "fine-tuning", 0.85),
            ("rlhf", "fine-tuning", 0.7),
            ("prompt engineering", "llms", 0.6),
            ("langchain", "llms", 0.5),
            ("llamaindex", "rag", 0.7),
            
            # ================================================================
            # RAG & Retrieval (Core JD requirement)
            # ================================================================
            ("rag", "llms", 0.8),
            ("rag", "information retrieval", 0.85),
            ("rag", "vector databases", 0.8),
            ("rag", "embeddings", 0.8),
            ("information retrieval", "search", 0.9),
            ("search", "elasticsearch", 0.8),
            ("search", "ranking", 0.85),
            ("ranking", "learning-to-rank", 0.9),
            ("ranking", "recommendation systems", 0.7),
            ("recommendation systems", "collaborative filtering", 0.8),
            ("bm25", "information retrieval", 0.8),
            ("bm25", "search", 0.8),
            ("hybrid search", "search", 0.9),
            ("hybrid search", "vector databases", 0.8),
            
            # ================================================================
            # Embeddings & Vector Databases (Core JD requirement)
            # ================================================================
            ("embeddings", "sentence-transformers", 0.9),
            ("embeddings", "word2vec", 0.6),
            ("sentence-transformers", "transformers", 0.8),
            ("openai", "embeddings", 0.7),
            ("openai", "llms", 0.8),
            ("bge", "embeddings", 0.9),
            ("e5", "embeddings", 0.9),
            ("vector databases", "faiss", 0.9),
            ("vector databases", "pinecone", 0.9),
            ("vector databases", "qdrant", 0.9),
            ("vector databases", "weaviate", 0.9),
            ("vector databases", "milvus", 0.9),
            ("vector databases", "chroma", 0.85),
            ("faiss", "pinecone", 0.7),
            ("faiss", "qdrant", 0.7),
            ("pinecone", "weaviate", 0.8),
            ("opensearch", "elasticsearch", 0.9),
            ("opensearch", "search", 0.8),
            
            # ================================================================
            # Evaluation & Metrics (JD explicitly requires this)
            # ================================================================
            ("evaluation", "ndcg", 0.9),
            ("evaluation", "mrr", 0.9),
            ("evaluation", "map", 0.9),
            ("ndcg", "ranking", 0.8),
            ("mrr", "ranking", 0.8),
            ("a/b testing", "evaluation", 0.7),
            ("a/b testing", "experimentation", 0.9),
            
            # ================================================================
            # Data Engineering
            # ================================================================
            ("spark", "hadoop", 0.7),
            ("pyspark", "spark", 0.9),
            ("airflow", "data engineering", 0.8),
            ("kafka", "data streaming", 0.9),
            ("kafka", "data engineering", 0.7),
            ("flink", "data streaming", 0.8),
            ("dbt", "data engineering", 0.7),
            ("etl", "data engineering", 0.8),
            ("data pipelines", "data engineering", 0.9),
            ("data pipelines", "airflow", 0.7),
            
            # ================================================================
            # ML Core Concepts
            # ================================================================
            ("machine learning", "deep learning", 0.7),
            ("deep learning", "neural networks", 0.9),
            ("data science", "machine learning", 0.6),
            ("statistics", "data science", 0.7),
            ("python", "machine learning", 0.4),
            ("python", "data science", 0.4),
            ("computer vision", "deep learning", 0.7),
            ("nlp", "deep learning", 0.7),
            ("mlops", "machine learning", 0.6),
            ("mlflow", "mlops", 0.8),
            ("kubeflow", "mlops", 0.7),
            ("feature engineering", "machine learning", 0.7),
            
            # ================================================================
            # DevOps & Cloud
            # ================================================================
            ("docker", "kubernetes", 0.7),
            ("kubernetes", "cloud", 0.7),
            ("aws", "cloud", 0.9),
            ("gcp", "cloud", 0.9),
            ("azure", "cloud", 0.9),
            ("aws", "gcp", 0.7),
            ("aws sagemaker", "mlops", 0.7),
            ("terraform", "infrastructure", 0.8),
            ("ci/cd", "devops", 0.8),
            ("github actions", "ci/cd", 0.8),
            
            # ================================================================
            # Databases
            # ================================================================
            ("postgresql", "sql", 0.9),
            ("mysql", "sql", 0.9),
            ("mongodb", "nosql", 0.9),
            ("redis", "caching", 0.8),
            ("dynamodb", "nosql", 0.8),
            ("cassandra", "nosql", 0.7),
            ("neo4j", "graph databases", 0.9),
            
            # ================================================================
            # Web / Backend (for broader matching)
            # ================================================================
            ("fastapi", "python", 0.7),
            ("flask", "python", 0.7),
            ("django", "python", 0.7),
            ("fastapi", "flask", 0.8),
            ("react", "javascript", 0.7),
            ("typescript", "javascript", 0.9),
            ("node.js", "javascript", 0.8),
            ("golang", "distributed systems", 0.5),
            ("rust", "systems programming", 0.6),
            
            # ================================================================
            # Cross-Domain Transfer Paths
            # ================================================================
            ("recommendation systems", "ranking", 0.7),
            ("recommendation systems", "machine learning", 0.6),
            ("search", "recommendation systems", 0.6),
            ("distributed systems", "data engineering", 0.5),
            ("distributed systems", "cloud", 0.5),
            ("backend", "distributed systems", 0.4),
            ("data engineering", "machine learning", 0.4),
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
                                best_adjacent = f"{c_skill} → {req}"
                        elif len(path) == 3:  # 2 hops away
                            # Diminish score for 2 hops
                            weight = 0.5
                            if weight > best_match:
                                best_match = weight
                                best_adjacent = f"{c_skill} → ... → {req}"
                        elif len(path) == 4:  # 3 hops away
                            weight = 0.25
                            if weight > best_match:
                                best_match = weight
                                best_adjacent = f"{c_skill} →→ {req}"
                    except nx.NetworkXNoPath:
                        pass
                        
            total_score += best_match
            if best_adjacent and best_match < 1.0:
                adjacent_matches.append(best_adjacent)
                
        final_score = total_score / len(req_skills)
        return min(1.0, final_score), adjacent_matches

    def get_graph_stats(self) -> dict:
        """Return graph statistics for the UI."""
        return {
            "total_skills": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "clusters": len(list(nx.connected_components(self.graph)))
        }
