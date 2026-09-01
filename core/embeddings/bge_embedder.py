"""
SentenceTransformer / BGE dense embedder implementation for CERN scientific corpus.
"""

from typing import List, Optional
import numpy as np
from core.embeddings.base import BaseEmbedder


class BGEEmbedder(BaseEmbedder):
    def __init__(
        self,
        model_name: str = "BAAI/bge-base-en-v1.5",
        device: Optional[str] = None,
        normalize_embeddings: bool = True,
    ):
        self._model = None
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        dimension = 768 if "bge-base" in model_name else (1024 if "bge-m3" in model_name or "bge-large" in model_name else 384)
        super().__init__(model_name=model_name, dimension=dimension)

    def _get_model(self):
        if self._model is None:
            import torch
            from sentence_transformers import SentenceTransformer
            
            target_device = self.device
            if not target_device:
                target_device = "cuda" if torch.cuda.is_available() else "cpu"
                
            self._model = SentenceTransformer(self.model_name, device=target_device)
            # update dimension dynamically from actual model
            self.dimension = self._model.get_sentence_embedding_dimension()
        return self._model

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.empty((0, self.dimension), dtype=np.float32)
        model = self._get_model()
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
        )
        return embeddings.astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        # BGE models benefit from instruction prefix on queries
        if "bge" in self.model_name.lower():
            query_text = f"Represent this sentence for searching relevant passages: {query}"
        else:
            query_text = query
            
        model = self._get_model()
        embedding = model.encode(
            query_text,
            show_progress_bar=False,
            normalize_embeddings=self.normalize_embeddings,
            convert_to_numpy=True,
        )
        return embedding.astype(np.float32)
