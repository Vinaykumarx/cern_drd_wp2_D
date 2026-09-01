"""
Base Reranker Interface for CERN Multimodal Retrieval.
Standardizes re-scoring of retrieved candidate chunks for maximal precision.
"""

from abc import ABC, abstractmethod
from typing import List
from core.storage.base import SearchResult


class BaseReranker(ABC):
    """Abstract interface for rerankers."""
    
    def __init__(self, model_name: str):
        self.model_name = model_name

    @abstractmethod
    def rerank(self, query: str, candidates: List[SearchResult], top_n: int = 5) -> List[SearchResult]:
        """Rerank candidates based on cross-attention with query."""
        pass
