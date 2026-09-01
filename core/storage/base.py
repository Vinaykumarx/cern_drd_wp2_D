"""
Base Vector Store Interface for CERN Multimodal RAG.
Decouples storage engines (LanceDB, Qdrant, Milvus) from retrieval logic.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import numpy as np

from core.chunkers.base import Chunk


class SearchResult(BaseModel):
    chunk_id: str
    doc_id: str
    filename: str
    page_number: int
    section: Optional[str] = None
    element_type: str = "text"
    content: str
    score: float  # Similarity score (higher is better for cosine / dot product)
    citation_anchor: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseVectorStore(ABC):
    """Abstract interface for vector database storage and retrieval."""
    
    def __init__(self, uri: str, table_name: str = "cern_multimodal_chunks"):
        self.uri = uri
        self.table_name = table_name

    @abstractmethod
    def add_chunks(self, chunks: List[Chunk], embeddings: np.ndarray) -> int:
        """Add chunks with their corresponding dense embeddings to the vector store."""
        pass

    @abstractmethod
    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        doc_id: Optional[str] = None,
        filter_expr: Optional[str] = None,
    ) -> List[SearchResult]:
        """Perform similarity search returning top-k SearchResult objects."""
        pass

    @abstractmethod
    def count(self, doc_id: Optional[str] = None) -> int:
        """Return total vector count optionally filtered by doc_id."""
        pass

    @abstractmethod
    def delete_doc(self, doc_id: str) -> bool:
        """Delete all vectors associated with a specific doc_id."""
        pass
