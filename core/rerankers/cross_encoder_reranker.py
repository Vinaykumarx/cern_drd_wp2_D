"""
CrossEncoder Reranker implementation using sentence-transformers.
"""

from typing import List, Optional
from core.storage.base import SearchResult
from core.rerankers.base import BaseReranker


class CrossEncoderReranker(BaseReranker):
    def __init__(
        self,
        model_name: str = "BAAI/bge-reranker-base",
        device: Optional[str] = None,
    ):
        super().__init__(model_name=model_name)
        self.device = device
        self._model = None

    def _get_model(self):
        if self._model is None:
            import torch
            from sentence_transformers import CrossEncoder
            
            target_device = self.device
            if not target_device:
                target_device = "cuda" if torch.cuda.is_available() else "cpu"
                
            self._model = CrossEncoder(self.model_name, device=target_device)
        return self._model

    def rerank(self, query: str, candidates: List[SearchResult], top_n: int = 5) -> List[SearchResult]:
        if not candidates:
            return []
        if len(candidates) <= 1:
            return candidates[:top_n]

        model = self._get_model()
        pairs = [[query, c.content] for c in candidates]
        scores = model.predict(pairs)

        # Update candidate scores
        scored_candidates = []
        for cand, score in zip(candidates, scores):
            cand_copy = cand.model_copy()
            cand_copy.score = float(score)
            scored_candidates.append(cand_copy)

        # Sort descending by reranker score
        scored_candidates.sort(key=lambda x: x.score, reverse=True)
        return scored_candidates[:top_n]
