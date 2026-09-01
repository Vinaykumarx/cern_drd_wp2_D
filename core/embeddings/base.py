"""
Base Embedding Interface for CERN Multimodal RAG.
Enables pluggable evaluation between BGE-base, BGE-M3, and other embedding candidates.
"""

from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np


class BaseEmbedder(ABC):
    """Abstract interface for dense embedding models."""
    
    def __init__(self, model_name: str, dimension: int):
        self.model_name = model_name
        self.dimension = dimension

    @abstractmethod
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """Embed a list of text strings into an array of shape (N, dimension)."""
        pass

    @abstractmethod
    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single search query into an array of shape (dimension,)."""
        pass
