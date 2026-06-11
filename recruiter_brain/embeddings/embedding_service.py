"""
Embedding Service
==================

Wraps sentence-transformers for generating text embeddings.

Features:
- BAAI/bge-large-en-v1.5 model (1024-dim)
- GPU/CPU auto-detection
- Batch encoding with progress bars
- L2 normalization
- Model caching (singleton)
"""

from __future__ import annotations

from typing import Optional, Union

import numpy as np
from loguru import logger
from tqdm import tqdm

from recruiter_brain.config import get_settings


class EmbeddingService:
    """
    Embedding service wrapping sentence-transformers.

    Uses BAAI/bge-large-en-v1.5 by default (1024-dim embeddings).
    Implements singleton pattern to avoid loading the model multiple times.
    """

    _instance: Optional["EmbeddingService"] = None
    _model = None

    def __new__(cls, *args, **kwargs) -> "EmbeddingService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name: Optional[str] = None) -> None:
        if self._model is not None:
            return  # Already initialized

        settings = get_settings()
        self._model_name = model_name or settings.embedding.model_name
        self._batch_size = settings.embedding.batch_size
        self._dimension = settings.embedding.dimension
        self._device = None

        self._load_model()

    def _load_model(self) -> None:
        """Load the embedding model with GPU/CPU auto-detection."""
        try:
            import torch
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            self._device = "cpu"

        logger.info(
            f"Loading embedding model: {self._model_name} on {self._device}"
        )

        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(
                self._model_name,
                device=self._device,
            )
            # Verify dimension
            test_emb = self._model.encode(["test"], normalize_embeddings=True)
            actual_dim = test_emb.shape[1]
            if actual_dim != self._dimension:
                logger.warning(
                    f"Model dimension {actual_dim} != configured {self._dimension}. "
                    f"Updating to {actual_dim}."
                )
                self._dimension = actual_dim

            logger.info(
                f"✓ Model loaded: dim={self._dimension}, device={self._device}"
            )
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            logger.warning("Falling back to random embeddings for testing")
            self._model = None

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._dimension

    def encode(
        self,
        texts: Union[str, list[str]],
        batch_size: Optional[int] = None,
        show_progress: bool = False,
        normalize: bool = True,
    ) -> np.ndarray:
        """
        Encode texts into embeddings.

        Args:
            texts: Single text or list of texts.
            batch_size: Override default batch size.
            show_progress: Show progress bar.
            normalize: L2-normalize embeddings.

        Returns:
            numpy array of shape (n_texts, dimension).
        """
        if isinstance(texts, str):
            texts = [texts]

        if not texts:
            return np.array([]).reshape(0, self._dimension)

        bs = batch_size or self._batch_size

        if self._model is None:
            # Fallback: random embeddings for testing
            logger.warning("Using random embeddings (model not loaded)")
            rng = np.random.RandomState(42)
            embs = rng.randn(len(texts), self._dimension).astype(np.float32)
            if normalize:
                norms = np.linalg.norm(embs, axis=1, keepdims=True)
                embs = embs / (norms + 1e-8)
            return embs

        # For BGE models, add instruction prefix for queries
        prefixed_texts = texts
        if "bge" in self._model_name.lower():
            # BGE models recommend instruction prefix for retrieval
            prefixed_texts = [
                f"Represent this sentence: {t}" for t in texts
            ]

        embeddings = self._model.encode(
            prefixed_texts,
            batch_size=bs,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize,
            convert_to_numpy=True,
        )

        return embeddings.astype(np.float32)

    def encode_queries(
        self,
        queries: Union[str, list[str]],
        batch_size: Optional[int] = None,
    ) -> np.ndarray:
        """
        Encode search queries (with special instruction prefix for BGE).

        Args:
            queries: Query text(s).
            batch_size: Override batch size.

        Returns:
            numpy array of embeddings.
        """
        if isinstance(queries, str):
            queries = [queries]

        if self._model is None:
            return self.encode(queries, batch_size)

        if "bge" in self._model_name.lower():
            prefixed = [
                f"Represent this sentence for searching relevant passages: {q}"
                for q in queries
            ]
        else:
            prefixed = queries

        return self._model.encode(
            prefixed,
            batch_size=batch_size or self._batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
        ).astype(np.float32)

    def similarity(
        self, embeddings_a: np.ndarray, embeddings_b: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity matrix between two sets of embeddings.

        Args:
            embeddings_a: (N, dim) array.
            embeddings_b: (M, dim) array.

        Returns:
            (N, M) similarity matrix.
        """
        # Normalize (should already be normalized, but ensure)
        a_norm = embeddings_a / (
            np.linalg.norm(embeddings_a, axis=1, keepdims=True) + 1e-8
        )
        b_norm = embeddings_b / (
            np.linalg.norm(embeddings_b, axis=1, keepdims=True) + 1e-8
        )
        return np.dot(a_norm, b_norm.T)

    def reset(self) -> None:
        """Reset the singleton (for testing)."""
        EmbeddingService._instance = None
        EmbeddingService._model = None
