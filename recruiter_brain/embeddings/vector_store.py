"""
Vector Store — Qdrant Integration
===================================

Manages candidate embeddings in Qdrant vector database.

Features:
- Collection creation with proper vector config
- Batch upsert with metadata
- Hybrid search: vector similarity + metadata filters
- In-memory fallback when Qdrant server unavailable
"""

from __future__ import annotations

from typing import Any, Optional

import numpy as np
from loguru import logger

from recruiter_brain.config import get_settings


class QdrantVectorStore:
    """
    Vector store backed by Qdrant.

    Supports both remote Qdrant server and in-memory mode.
    """

    def __init__(
        self,
        collection_name: Optional[str] = None,
        dimension: Optional[int] = None,
    ) -> None:
        settings = get_settings()
        self._collection = collection_name or settings.qdrant.collection
        self._dimension = dimension or settings.embedding.dimension
        self._client = None
        self._use_inmemory = settings.qdrant.use_inmemory

        self._connect(settings)

    def _connect(self, settings) -> None:
        """Initialize Qdrant client."""
        try:
            from qdrant_client import QdrantClient

            if self._use_inmemory:
                logger.info("Using in-memory Qdrant client")
                self._client = QdrantClient(location=":memory:")
            else:
                logger.info(
                    f"Connecting to Qdrant at "
                    f"{settings.qdrant.host}:{settings.qdrant.port}"
                )
                try:
                    self._client = QdrantClient(
                        host=settings.qdrant.host,
                        port=settings.qdrant.port,
                        timeout=10,
                    )
                    # Test connection
                    self._client.get_collections()
                    logger.info("✓ Connected to Qdrant server")
                except Exception as e:
                    logger.warning(
                        f"Cannot connect to Qdrant server: {e}. "
                        f"Falling back to in-memory mode."
                    )
                    self._client = QdrantClient(location=":memory:")
                    self._use_inmemory = True

        except ImportError:
            logger.error("qdrant-client not installed")
            self._client = None

    def create_collection(self, recreate: bool = False) -> bool:
        """
        Create the vector collection.

        Args:
            recreate: If True, drop and recreate existing collection.

        Returns:
            True if collection was created/exists.
        """
        if self._client is None:
            return False

        from qdrant_client.models import Distance, VectorParams

        try:
            collections = [
                c.name for c in self._client.get_collections().collections
            ]

            if self._collection in collections:
                if recreate:
                    logger.info(f"Recreating collection '{self._collection}'")
                    self._client.delete_collection(self._collection)
                else:
                    logger.info(
                        f"Collection '{self._collection}' already exists"
                    )
                    return True

            self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=self._dimension,
                    distance=Distance.COSINE,
                ),
            )
            logger.info(
                f"✓ Created collection '{self._collection}' "
                f"(dim={self._dimension}, cosine)"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            return False

    def upsert_batch(
        self,
        ids: list[str],
        embeddings: np.ndarray,
        metadata: list[dict[str, Any]],
        batch_size: int = 100,
    ) -> int:
        """
        Batch upsert embeddings with metadata.

        Args:
            ids: List of candidate IDs.
            embeddings: (N, dim) numpy array.
            metadata: List of metadata dicts per candidate.
            batch_size: Upload batch size.

        Returns:
            Number of points upserted.
        """
        if self._client is None:
            logger.error("Qdrant client not initialized")
            return 0

        from qdrant_client.models import PointStruct

        total = len(ids)
        upserted = 0

        for i in range(0, total, batch_size):
            batch_ids = ids[i : i + batch_size]
            batch_embs = embeddings[i : i + batch_size]
            batch_meta = metadata[i : i + batch_size]

            points = [
                PointStruct(
                    id=idx,
                    vector=emb.tolist(),
                    payload={**meta, "candidate_id": cid},
                )
                for idx, (cid, emb, meta) in enumerate(
                    zip(batch_ids, batch_embs, batch_meta), start=i
                )
            ]

            try:
                self._client.upsert(
                    collection_name=self._collection,
                    points=points,
                )
                upserted += len(points)
            except Exception as e:
                logger.error(f"Upsert batch failed at offset {i}: {e}")

        logger.info(f"Upserted {upserted}/{total} points to '{self._collection}'")
        return upserted

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 100,
        filters: Optional[dict] = None,
        score_threshold: Optional[float] = None,
    ) -> list[dict]:
        """
        Search for similar candidates.

        Args:
            query_vector: Query embedding (1D array).
            top_k: Number of results.
            filters: Metadata filters.
            score_threshold: Minimum similarity score.

        Returns:
            List of dicts with candidate_id, score, and metadata.
        """
        if self._client is None:
            return []

        from qdrant_client.models import Filter, FieldCondition, MatchValue

        # Build filter
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, list):
                    # Match any in list
                    for v in value:
                        conditions.append(
                            FieldCondition(key=key, match=MatchValue(value=v))
                        )
                else:
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
            if conditions:
                qdrant_filter = Filter(should=conditions)

        try:
            results = self._client.search(
                collection_name=self._collection,
                query_vector=query_vector.tolist(),
                limit=top_k,
                query_filter=qdrant_filter,
                score_threshold=score_threshold,
            )

            return [
                {
                    "candidate_id": hit.payload.get("candidate_id", ""),
                    "score": hit.score,
                    "metadata": hit.payload,
                }
                for hit in results
            ]

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_count(self) -> int:
        """Get total number of points in collection."""
        if self._client is None:
            return 0
        try:
            info = self._client.get_collection(self._collection)
            return info.points_count
        except Exception:
            return 0

    def delete_collection(self) -> bool:
        """Delete the collection."""
        if self._client is None:
            return False
        try:
            self._client.delete_collection(self._collection)
            logger.info(f"Deleted collection '{self._collection}'")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            return False
