"""
Embedding Service
==================

Generates dense embeddings using sentence-transformers.
"""

from __future__ import annotations

import numpy as np
from loguru import logger
from sentence_transformers import SentenceTransformer

from recruiter_brain.config import get_settings


class EmbeddingService:
    """Service to generate dense embeddings for text using sentence-transformers."""

    def __init__(self):
        self.settings = get_settings()
        model_name = self.settings.embeddings.model_name
        device = self.settings.embeddings.device
        
        logger.info(f"Loading embedding model: {model_name} on {device}...")
        self.model = SentenceTransformer(model_name, device=device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
        # Validate config matches model
        if self.dimension != self.settings.embeddings.dimension:
            logger.warning(
                f"Config dimension ({self.settings.embeddings.dimension}) "
                f"does not match actual model dimension ({self.dimension})."
            )

    def generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """
        Generate embeddings for a list of strings.
        
        Returns:
            Numpy array of shape (N, dimension) of dtype float32
        """
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
            
        logger.debug(f"Encoding {len(texts)} texts...")
        
        # Set batch_size from config, and normalize_embeddings=True for Cosine Similarity in FAISS
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
