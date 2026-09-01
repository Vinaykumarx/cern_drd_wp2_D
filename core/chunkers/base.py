"""
Base Chunker Interface for CERN Multimodal Document Processing.
Ensures deterministic chunking, page provenance retention, and metadata traceability.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import hashlib

from core.schemas.canonical import CanonicalDocument, Provenance, ElementType


class Chunk(BaseModel):
    chunk_id: str
    doc_id: str
    filename: str
    page_number: int
    section: Optional[str] = None
    element_type: str = "text"
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    citation_anchor: str

    @classmethod
    def create_deterministic_id(cls, doc_id: str, page_num: int, index: int, content: str) -> str:
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:8]
        return f"{doc_id}_p{page_num}_c{index}_{content_hash}"


class BaseChunker(ABC):
    """Abstract interface for all document chunking engines."""
    
    def __init__(self, target_chunk_size: int = 500, chunk_overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(self, doc: CanonicalDocument) -> List[Chunk]:
        """
        Split a CanonicalDocument into structure-aware, provenance-grounded Chunks.
        """
        pass
