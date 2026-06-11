"""
Tests — Vector Store
=====================

Tests for Qdrant vector store operations using in-memory client.
"""

from __future__ import annotations

import numpy as np
import pytest


class TestQdrantVectorStore:
    """Tests for the Qdrant vector store."""

    def _create_store(self):
        """Create an in-memory vector store for testing."""
        from recruiter_brain.embeddings.vector_store import QdrantVectorStore

        store = QdrantVectorStore(
            collection_name="test_collection",
            dimension=64,
        )
        store._use_inmemory = True
        return store

    def test_create_collection(self):
        """Collection creation should succeed."""
        store = self._create_store()
        result = store.create_collection(recreate=True)
        assert result is True

    def test_upsert_and_count(self):
        """Upserting points should increase count."""
        store = self._create_store()
        store.create_collection(recreate=True)

        # Create dummy data
        ids = ["cand_001", "cand_002", "cand_003"]
        embeddings = np.random.randn(3, 64).astype(np.float32)
        metadata = [
            {"name": "Alice", "skills": ["Python", "ML"]},
            {"name": "Bob", "skills": ["Java", "Spring"]},
            {"name": "Carol", "skills": ["Python", "NLP"]},
        ]

        count = store.upsert_batch(ids, embeddings, metadata)
        assert count == 3
        assert store.get_count() == 3

    def test_search(self):
        """Search should return relevant results."""
        store = self._create_store()
        store.create_collection(recreate=True)

        # Create embeddings where cand_001 and query are similar
        np.random.seed(42)
        query_vec = np.random.randn(64).astype(np.float32)

        # Make cand_001 similar to query
        emb1 = query_vec + np.random.randn(64).astype(np.float32) * 0.1
        emb2 = np.random.randn(64).astype(np.float32)
        emb3 = np.random.randn(64).astype(np.float32)

        embeddings = np.stack([emb1, emb2, emb3])
        ids = ["cand_001", "cand_002", "cand_003"]
        metadata = [
            {"candidate_id": "cand_001", "name": "Similar"},
            {"candidate_id": "cand_002", "name": "Random1"},
            {"candidate_id": "cand_003", "name": "Random2"},
        ]

        store.upsert_batch(ids, embeddings, metadata)

        results = store.search(query_vec, top_k=3)
        assert len(results) == 3
        assert results[0]["candidate_id"] == "cand_001"  # Most similar
        assert results[0]["score"] > results[1]["score"]

    def test_search_top_k(self):
        """Search should respect top_k parameter."""
        store = self._create_store()
        store.create_collection(recreate=True)

        n = 10
        embeddings = np.random.randn(n, 64).astype(np.float32)
        ids = [f"cand_{i:03d}" for i in range(n)]
        metadata = [{"candidate_id": cid} for cid in ids]

        store.upsert_batch(ids, embeddings, metadata)

        results = store.search(np.random.randn(64).astype(np.float32), top_k=5)
        assert len(results) == 5

    def test_delete_collection(self):
        """Deleting collection should work."""
        store = self._create_store()
        store.create_collection(recreate=True)
        result = store.delete_collection()
        assert result is True

    def test_embedding_dimensions(self):
        """Embeddings should match configured dimension."""
        store = self._create_store()
        assert store._dimension == 64

        store.create_collection(recreate=True)

        # Wrong dimension should still upsert (Qdrant handles this)
        correct_emb = np.random.randn(1, 64).astype(np.float32)
        count = store.upsert_batch(
            ["test"], correct_emb, [{"candidate_id": "test"}]
        )
        assert count == 1
