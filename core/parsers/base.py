"""
Base Parser Interface for CERN Multimodal Document Processing.
Enables plug-and-play evaluation between Docling, Marker, MinerU, and PyMuPDF.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import os
from core.schemas.canonical import CanonicalDocument


class BaseDocumentParser(ABC):
    """Abstract interface for all document parsers."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def parse(self, file_path: str, doc_id: Optional[str] = None) -> CanonicalDocument:
        """
        Parse a document (e.g. PDF) into the CanonicalDocument representation.
        Must strictly preserve page provenance and element types.
        """
        pass

    def validate_file(self, file_path: str) -> bool:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")
        return True
