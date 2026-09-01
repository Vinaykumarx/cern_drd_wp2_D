"""
Canonical Document Schema for CERN Multimodal RAG.
Provides a strict, uniform document model preserving deep provenance
across all parsers (Docling, Marker, PyMuPDF).
"""

from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
import uuid
import datetime


class ElementType(str, Enum):
    TEXT = "text"
    HEADING = "heading"
    TABLE = "table"
    FIGURE = "figure"
    EQUATION = "equation"
    LIST_ITEM = "list_item"
    CODE = "code"


class BoundingBox(BaseModel):
    l: float = 0.0  # left / x0
    t: float = 0.0  # top / y0
    r: float = 0.0  # right / x1
    b: float = 0.0  # bottom / y1
    coord_origin: str = "top-left"


class Provenance(BaseModel):
    doc_id: str
    filename: str
    page_number: int  # 1-indexed
    section: Optional[str] = None
    subsection: Optional[str] = None
    block_id: str = Field(default_factory=lambda: f"blk_{uuid.uuid4().hex[:8]}")
    bbox: Optional[BoundingBox] = None
    parser_name: str = "unknown"
    parser_version: Optional[str] = None

    @property
    def citation_anchor(self) -> str:
        """Returns standard URL/UI page link anchor (e.g., #page=12)."""
        return f"{self.filename}#page={self.page_number}"


class DocumentElement(BaseModel):
    element_id: str = Field(default_factory=lambda: f"elem_{uuid.uuid4().hex[:12]}")
    element_type: ElementType
    content: str  # text representation or markdown
    provenance: Provenance
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Specific fields for tables and figures
    table_csv: Optional[str] = None  # CSV string or file reference
    table_rows: Optional[List[List[str]]] = None
    image_path: Optional[str] = None
    caption: Optional[str] = None


class CanonicalDocument(BaseModel):
    doc_id: str
    filename: str
    title: Optional[str] = None
    total_pages: int = 1
    elements: List[DocumentElement] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat())

    def get_elements_by_page(self, page_num: int) -> List[DocumentElement]:
        return [el for el in self.elements if el.provenance.page_number == page_num]

    def get_elements_by_type(self, el_type: ElementType) -> List[DocumentElement]:
        return [el for el in self.elements if el.element_type == el_type]
