"""
FAISS Vector Store
===================

Local embedded vector database for fast semantic search using FAISS.
Replaces external dependencies like Qdrant to support high-speed local evaluation.

Memory-safe design: Only lightweight metadata (candidate_id + scoring fields)
is stored in the .npy file. Full profiles are fetched from SQLite on demand.
"""

from __future__ import annotations

import json
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
        # Use JSON for metadata — human-readable, no pickle, memory-safe
        self.metadata_path = self.cache_dir / "candidates_meta.json"
        # Legacy npy path for cleanup
        self._legacy_npy_path = self.cache_dir / "candidates_meta.npy"

        self.index = None
        self.metadata: list[dict[str, Any]] = []

        os.makedirs(self.cache_dir, exist_ok=True)

        # Remove legacy oversized npy file if present
        if self._legacy_npy_path.exists():
            self._legacy_npy_path.unlink()
            logger.info("Removed legacy metadata npy file.")

        self._initialize_index()

    def _initialize_index(self):
        """Load from disk if exists, otherwise create new."""
        if self.index_path.exists() and self.metadata_path.exists():
            logger.info(f"Loading FAISS index from {self.index_path}...")
            self.index = faiss.read_index(str(self.index_path))

            # JSON is safe and has no memory spike issues
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            logger.info(f"Loaded {self.index.ntotal} vectors, {len(self.metadata)} metadata entries.")
        else:
            logger.info(f"Creating new FAISS index (dim={self.dimension})...")
            self.index = faiss.IndexFlatIP(self.dimension)
            self.metadata = []

    def save(self):
        """Persist index and metadata to disk."""
        if self.index is not None:
            logger.info(f"Saving FAISS index ({self.index.ntotal} vectors) to {self.index_path}...")
            faiss.write_index(self.index, str(self.index_path))

            # Save as JSON — lightweight, no pickle memory explosion
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False)

            logger.info("FAISS index saved.")

    def is_empty(self) -> bool:
        return self.index is None or self.index.ntotal == 0

    def add_embeddings(self, embeddings: np.ndarray, metadata_list: list[dict[str, Any]]):
        """
        Add a batch of embeddings and their lightweight metadata.

        IMPORTANT: metadata_list should contain only serializable, lightweight dicts.
        Do NOT store full Pydantic model objects here — they cause memory errors at scale.
        Store candidate_id and scoring-relevant fields only; fetch full profiles from SQLite.

        Args:
            embeddings: Float32 numpy array of shape (N, dim)
            metadata_list: List of N lightweight metadata dicts
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

        # Strip any non-serializable objects before storing
        safe_meta = []
        for m in metadata_list:
            safe = {
                k: v for k, v in m.items()
                if isinstance(v, (str, int, float, bool, list, dict, type(None)))
                and k != "raw_profile"  # Never store full Pydantic objects
            }
            safe_meta.append(safe)

        self.metadata.extend(safe_meta)
        logger.debug(f"Added {len(embeddings)} vectors. Total: {self.index.ntotal}")

    def search(self, query_embedding: np.ndarray, top_k: int = 100) -> list[dict[str, Any]]:
        """
        Search for top_k most similar vectors.

        Args:
            query_embedding: Float32 numpy array of shape (dim,) or (1, dim)

        Returns:
            List of dicts with 'metadata' (lightweight) and 'score' (cosine similarity 0-1)
        """
        if self.is_empty():
            logger.warning("FAISS index is empty. Cannot search.")
            return []

        if query_embedding.dtype != np.float32:
            query_embedding = query_embedding.astype(np.float32)

        if len(query_embedding.shape) == 1:
            query_embedding = query_embedding.reshape(1, -1)
        faiss.normalize_L2(query_embedding)

        # Cap top_k to index size
        actual_k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_embedding, actual_k)

        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx != -1 and idx < len(self.metadata):
                score = float(scores[0][i])
                normalized_score = max(0.0, min(1.0, score))

                results.append({
                    "metadata": self.metadata[idx],
                    "score": normalized_score
                })

        return results
