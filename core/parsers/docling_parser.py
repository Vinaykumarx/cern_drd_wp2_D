"""
Docling Document Parser for CERN Multimodal RAG.
Primary candidate for scientific PDF parsing with table structure and formula understanding.
"""

import os
from typing import Optional, Dict, Any

from core.parsers.base import BaseDocumentParser
from core.schemas.canonical import (
    CanonicalDocument,
    DocumentElement,
    ElementType,
    Provenance,
    BoundingBox,
)


class DoclingDocumentParser(BaseDocumentParser):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="docling", config=config)
        self._converter = None

    def _get_converter(self):
        if self._converter is None:
            try:
                from docling.document_converter import DocumentConverter
                self._converter = DocumentConverter()
            except ImportError:
                raise ImportError(
                    "Docling package not installed. Install via `pip install docling` or use PyMuPDFParser fallback."
                )
        return self._converter

    def parse(self, file_path: str, doc_id: Optional[str] = None) -> CanonicalDocument:
        self.validate_file(file_path)
        filename = os.path.basename(file_path)
        if not doc_id:
            doc_id = os.path.splitext(filename)[0]

        converter = self._get_converter()
        conv_result = converter.convert(file_path)
        doc = conv_result.document

        elements = []
        total_pages = doc.num_pages if hasattr(doc, "num_pages") else 1

        # Iterate over Docling body items
        for item, _ in doc.iterate_items():
            text = getattr(item, "text", "") or ""
            text = text.strip()
            if not text:
                continue

            label = getattr(item, "label", "text").lower()
            page_no = 1
            bbox = None

            if hasattr(item, "prov") and item.prov:
                prov_first = item.prov[0]
                page_no = getattr(prov_first, "page_no", 1)
                if hasattr(prov_first, "bbox") and prov_first.bbox:
                    b = prov_first.bbox
                    bbox = BoundingBox(
                        l=float(getattr(b, "l", 0.0)),
                        t=float(getattr(b, "t", 0.0)),
                        r=float(getattr(b, "r", 0.0)),
                        b=float(getattr(b, "b", 0.0)),
                        coord_origin=getattr(b, "coord_origin", "top-left"),
                    )

            # Map Docling labels to ElementType
            if "heading" in label or "title" in label or "header" in label:
                el_type = ElementType.HEADING
            elif "table" in label:
                el_type = ElementType.TABLE
            elif "figure" in label or "picture" in label or "image" in label:
                el_type = ElementType.FIGURE
            elif "equation" in label or "formula" in label:
                el_type = ElementType.EQUATION
            elif "code" in label:
                el_type = ElementType.CODE
            elif "list" in label:
                el_type = ElementType.LIST_ITEM
            else:
                el_type = ElementType.TEXT

            prov = Provenance(
                doc_id=doc_id,
                filename=filename,
                page_number=page_no,
                bbox=bbox,
                parser_name="docling",
            )

            # If it is a table item, export table representation
            table_csv = None
            if el_type == ElementType.TABLE and hasattr(item, "export_to_dataframe"):
                try:
                    df = item.export_to_dataframe()
                    table_csv = df.to_csv(index=False)
                except Exception:
                    table_csv = None

            elements.append(
                DocumentElement(
                    element_type=el_type,
                    content=text,
                    provenance=prov,
                    table_csv=table_csv,
                    metadata={"docling_label": label},
                )
            )

        return CanonicalDocument(
            doc_id=doc_id,
            filename=filename,
            total_pages=total_pages,
            elements=elements,
            metadata={"parser": "docling", "source_path": file_path},
        )
