"""
FAISS Vector Store
===================

Local embedded vector database for fast semantic search using FAISS.
Replaces external dependencies like Qdrant to support high-speed local evaluation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from loguru import logger

from recruiter_brain.config import get_settings


class FAISSVectorStore:
    """FAISS wrapper for storing and searching candidate embeddings."""

    def __init__(self):
        self.settings = get_settings()
        self.dimension = self.settings.embeddings.dimension
        self.cache_dir = Path(self.settings.dataset.cache_dir)
        self.index_path = self.cache_dir / "candidates.faiss"
        self.metadata_path = self.cache_dir / "candidates_meta.npy"
        
        self.index = None
        self.metadata = []  # Maps FAISS index row to candidate metadata dict
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self._initialize_index()

    def _initialize_index(self):
        """Load from disk if exists, otherwise create new."""
        if self.index_path.exists() and self.metadata_path.exists():
            logger.info(f"Loading FAISS index from {self.index_path}...")
            self.index = faiss.read_index(str(self.index_path))
            # Load metadata allowing pickle (safe for internal use)
            self.metadata = np.load(self.metadata_path, allow_pickle=True).tolist()
            logger.info(f"Loaded {self.index.ntotal} vectors.")
        else:
            logger.info(f"Creating new FAISS index (dim={self.dimension})...")
            # Using IndexFlatIP for Cosine Similarity (assuming embeddings are L2 normalized)
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def save(self):
        """Persist index and metadata to disk."""
        if self.index is not None:
            logger.info(f"Saving FAISS index to {self.index_path}...")
            faiss.write_index(self.index, str(self.index_path))
            np.save(self.metadata_path, np.array(self.metadata, dtype=object))

    def is_empty(self) -> bool:
        return self.index is None or self.index.ntotal == 0

    def add_embeddings(self, embeddings: np.ndarray, metadata_list: list[dict[str, Any]]):
        """
        Add a batch of embeddings and their metadata.
        
        Args:
            embeddings: Float32 numpy array of shape (N, dim)
            metadata_list: List of N metadata dicts (must contain 'candidate_id')
        """
        if len(embeddings) != len(metadata_list):
            raise ValueError("Embeddings and metadata lists must be same length.")
            
        if self.index is None:
            self._initialize_index()
            
        # Ensure float32
        if embeddings.dtype != np.float32:
            embeddings = embeddings.astype(np.float32)
            
        # Ensure L2 normalization for Inner Product to act as Cosine Similarity
        faiss.normalize_L2(embeddings)
            
        self.index.add(embeddings)
        self.metadata.extend(metadata_list)
        logger.debug(f"Added {len(embeddings)} vectors. Total: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, top_k: int = 100) -> list[dict[str, Any]]:
        """
        Search for top_k most similar vectors.
        
        Args:
            query_embedding: Float32 numpy array of shape (1, dim)
            top_k: Number of results to return
            
        Returns:
            List of dicts containing 'metadata' and 'score' (cosine similarity)
        """
        if self.is_empty():
            logger.warning("FAISS index is empty. Cannot search.")
            return []
            
        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)
            
        # Ensure L2 norm
        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)
        
        # Search returns distances (scores) and indices
        scores, indices = self.index.search(query_embedding, top_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1 and idx < len(self.metadata):
                score = float(scores[0][i])
                # Ensure score is between 0 and 1 (handling slight float inaccuracies)
                # If vectors are strictly positive, inner product is 0 to 1.
                # If they can be negative, inner product is -1 to 1. We map to 0-1 if needed,
                # but standard cosine similarity for semantics is often taken as is or max(0, score)
                normalized_score = max(0.0, min(1.0, score))
                
                results.append({
                    "metadata": self.metadata[idx],
                    "score": normalized_score
                })
                
        return results
