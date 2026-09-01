"""
PyMuPDF-based parser implementation for CanonicalDocument extraction.
Fast, reliable fallback parser providing bounding boxes, page structure, and text blocks.
"""

import os
from typing import Optional, Dict, Any
import fitz  # PyMuPDF

from core.parsers.base import BaseDocumentParser
from core.schemas.canonical import (
    CanonicalDocument,
    DocumentElement,
    ElementType,
    Provenance,
    BoundingBox,
)


class PyMuPDFParser(BaseDocumentParser):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="pymupdf", config=config)

    def parse(self, file_path: str, doc_id: Optional[str] = None) -> CanonicalDocument:
        self.validate_file(file_path)
        filename = os.path.basename(file_path)
        if not doc_id:
            doc_id = os.path.splitext(filename)[0]

        doc = fitz.open(file_path)
        total_pages = len(doc)
        elements = []
        current_section = None

        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_num = page_idx + 1
            
            # Extract text blocks with layout positioning
            blocks = page.get_text("blocks")
            for b in blocks:
                # block tuple: (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) >= 5:
                    x0, y0, x1, y1, text, block_no = b[0], b[1], b[2], b[3], b[4], b[5]
                    text_clean = text.strip()
                    if not text_clean:
                        continue

                    # Heuristic detection for headings
                    is_heading = False
                    if len(text_clean.split("\n")) == 1 and len(text_clean) < 100:
                        if text_clean.startswith(("#", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.", "Section", "Chapter", "TABLE", "FIGURE")):
                            is_heading = True
                            current_section = text_clean

                    el_type = ElementType.HEADING if is_heading else ElementType.TEXT
                    
                    bbox = BoundingBox(l=float(x0), t=float(y0), r=float(x1), b=float(y1))
                    provenance = Provenance(
                        doc_id=doc_id,
                        filename=filename,
                        page_number=page_num,
                        section=current_section,
                        block_id=f"p{page_num}_b{block_no}",
                        bbox=bbox,
                        parser_name="pymupdf",
                        parser_version=fitz.__version__,
                    )

                    elements.append(
                        DocumentElement(
                            element_type=el_type,
                            content=text_clean,
                            provenance=provenance,
                            metadata={"char_count": len(text_clean)},
                        )
                    )

        doc.close()

        return CanonicalDocument(
            doc_id=doc_id,
            filename=filename,
            total_pages=total_pages,
            elements=elements,
            metadata={"parser": "pymupdf", "source_path": file_path},
        )
