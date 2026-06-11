"""
Embedding Service
==================

Generates dense embeddings using sentence-transformers.
"""

from __future__ import annotations

import hashlib
import numpy as np
from loguru import logger

from recruiter_brain.config import get_settings


class EmbeddingService:
    """Service to generate dense embeddings for text using sentence-transformers."""

    def __init__(self):
        self.settings = get_settings()
        model_name = self.settings.embeddings.model_name
        device = self.settings.embeddings.device
        self.dimension = self.settings.embeddings.dimension
        self.is_simulation = self.settings.llm.simulation_mode
        self.model = None
        
        if self.is_simulation:
            logger.info("Running embedding service in SIMULATION mode (Mock embeddings).")
        else:
            logger.info(f"Loading embedding model: {model_name} on {device}...")
            # Defer import to prevent memory crash on Windows machines with small paging files
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(model_name, device=device)
                actual_dim = self.model.get_sentence_embedding_dimension()
                if actual_dim != self.dimension:
                    logger.warning(
                        f"Config dimension ({self.dimension}) does not match "
                        f"actual model dimension ({actual_dim}). Updating."
                    )
                    self.dimension = actual_dim
            except Exception as e:
                logger.error(f"Failed to load sentence_transformers: {e}. Falling back to simulation mode.")
                self.is_simulation = True

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for a list of strings.
        
        Returns:
            Numpy array of shape (N, dimension) of dtype float32
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
            
        logger.debug(f"Encoding {len(texts)} texts...")
        
        if self.is_simulation or not self.model:
            # Generate deterministic pseudo-random vectors based on hash
            embeddings = []
            for t in texts:
                # Seed numpy with hash of text for deterministic output
                seed = int(hashlib.md5(t.encode('utf-8')).hexdigest()[:8], 16)
                rng = np.random.RandomState(seed)
                vec = rng.randn(self.dimension).astype(np.float32)
                # L2 normalize
                vec = vec / np.linalg.norm(vec)
                embeddings.append(vec)
            return np.array(embeddings, dtype=np.float32)

        # Real inference
        embeddings = self.model.encode(
            texts, 
            batch_size=self.settings.embeddings.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        
        return embeddings.astype(np.float32)

    def generate_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single string."""
        return self.generate_embeddings([text])

    def generate_candidate_embeddings(self, preprocessed_candidates: list[dict]) -> np.ndarray:
        """Generate embeddings from the 'embedding_doc' field of preprocessed candidates."""
        texts = [c["embedding_doc"] for c in preprocessed_candidates]
        return self.generate_embeddings(texts)
