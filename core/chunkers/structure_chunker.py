"""
Structure-Aware Deterministic Chunker for CERN Scientific Documents.
Preserves page bounds, table structures, section headings, and exact citation provenance.
"""

from typing import List, Dict, Any
from core.chunkers.base import BaseChunker, Chunk
from core.schemas.canonical import CanonicalDocument, ElementType


class StructureAwareChunker(BaseChunker):
    def __init__(self, target_chunk_size: int = 600, chunk_overlap: int = 80):
        super().__init__(target_chunk_size=target_chunk_size, chunk_overlap=chunk_overlap)

    def chunk(self, doc: CanonicalDocument) -> List[Chunk]:
        chunks: List[Chunk] = []
        chunk_idx = 0
        current_section = "General"

        # Process document elements sequentially
        for elem in doc.elements:
            page_num = elem.provenance.page_number
            if elem.provenance.section:
                current_section = elem.provenance.section

            # Tables and Figures are treated as standalone high-value semantic units
            if elem.element_type in [ElementType.TABLE, ElementType.FIGURE, ElementType.EQUATION]:
                content = elem.content
                if elem.table_csv:
                    content = f"[TABLE on Page {page_num}]\n{elem.table_csv}\n\nDescription: {elem.content}"

                chunk_id = Chunk.create_deterministic_id(
                    doc_id=doc.doc_id,
                    page_num=page_num,
                    index=chunk_idx,
                    content=content,
                )
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        doc_id=doc.doc_id,
                        filename=doc.filename,
                        page_number=page_num,
                        section=current_section,
                        element_type=elem.element_type.value,
                        content=content,
                        metadata={
                            "is_table": elem.element_type == ElementType.TABLE,
                            "is_figure": elem.element_type == ElementType.FIGURE,
                            **elem.metadata,
                        },
                        citation_anchor=elem.provenance.citation_anchor,
                    )
                )
                chunk_idx += 1
                continue

            # Standard Text Elements
            text = elem.content.strip()
            if not text:
                continue

            # If element text is within target size, create chunk directly
            if len(text) <= self.target_chunk_size:
                chunk_id = Chunk.create_deterministic_id(
                    doc_id=doc.doc_id,
                    page_num=page_num,
                    index=chunk_idx,
                    content=text,
                )
                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        doc_id=doc.doc_id,
                        filename=doc.filename,
                        page_number=page_num,
                        section=current_section,
                        element_type=elem.element_type.value,
                        content=text,
                        metadata=elem.metadata,
                        citation_anchor=elem.provenance.citation_anchor,
                    )
                )
                chunk_idx += 1
            else:
                # Sub-split long text blocks cleanly at sentence / paragraph bounds
                paragraphs = text.split("\n\n")
                buffer = ""
                for p in paragraphs:
                    if len(buffer) + len(p) <= self.target_chunk_size:
                        buffer = f"{buffer}\n\n{p}".strip()
                    else:
                        if buffer:
                            chunk_id = Chunk.create_deterministic_id(
                                doc_id=doc.doc_id,
                                page_num=page_num,
                                index=chunk_idx,
                                content=buffer,
                            )
                            chunks.append(
                                Chunk(
                                    chunk_id=chunk_id,
                                    doc_id=doc.doc_id,
                                    filename=doc.filename,
                                    page_number=page_num,
                                    section=current_section,
                                    element_type="text",
                                    content=buffer,
                                    metadata=elem.metadata,
                                    citation_anchor=elem.provenance.citation_anchor,
                                )
                            )
                            chunk_idx += 1
                        buffer = p

                if buffer:
                    chunk_id = Chunk.create_deterministic_id(
                        doc_id=doc.doc_id,
                        page_num=page_num,
                        index=chunk_idx,
                        content=buffer,
                    )
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            doc_id=doc.doc_id,
                            filename=doc.filename,
                            page_number=page_num,
                            section=current_section,
                            element_type="text",
                            content=buffer,
                            metadata=elem.metadata,
                            citation_anchor=elem.provenance.citation_anchor,
                        )
                    )
                    chunk_idx += 1

        return chunks
