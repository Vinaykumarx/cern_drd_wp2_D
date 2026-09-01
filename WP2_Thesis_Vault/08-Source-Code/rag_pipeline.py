import os
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import numpy as np
from sentence_transformers import SentenceTransformer, CrossEncoder

from core.vector_store_lance import LanceVectorStore
from core.semantic_chunker import SemanticChunker


@dataclass
class Chunk:
    id: str
    text: str
    source: str
    page: int
    chunk_index: int
    doc_id: str  # Document ID (e.g., filename or user label)
    metadata: Dict[str, Any]
    # Agentic Semantic Chunking Metadata
    title: str = ""
    topic: str = ""
    summary: str = ""
    keywords: str = ""
    quality_score: float = 0.0
    pdf_source: str = ""  # Source PDF file for display in popup


class RAGPipeline:
    """
    RAG pipeline that:
      - loads metadata.json built by extraction/pipeline.py
      - builds chunks for text, tables, figures/graphs
      - ingests into LanceDB
      - performs semantic search and returns structured hits
    """

    def __init__(
        self,
        db_uri: str = "lancedb",
        table_name: str = "cern_demo",
        embed_model_name: str = "BAAI/bge-base-en-v1.5",
        metadata_path: str = "metadata.json",
    ) -> None:
        self.base_dir = Path(__file__).resolve().parent.parent
        self.metadata_path = self.base_dir / metadata_path
        self.doc_id = "default"  # default doc_id; can be overridden per ingest

        print("[Embedder] Loading SentenceTransformer:", embed_model_name)
        self.embed_model = SentenceTransformer(embed_model_name, device="cuda")

        # LanceDB vector store (768-dim for BGE)
        self.store = LanceVectorStore(
            db_uri=db_uri,
            table_name=table_name,
            dim=768,
        )
        
        print("[Reranker] Loading CrossEncoder: cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2", device="cuda")

        self.metadata = self._load_metadata()

    # ------------------------------------------------------------------
    # METADATA
    # ------------------------------------------------------------------

    def _load_metadata(self) -> Dict[str, Any]:
        if not self.metadata_path.exists():
            print(f"[RAG] metadata.json not found at {self.metadata_path}")
            return {"pages": [], "tables": [], "figures": []}

        with open(self.metadata_path) as f:
            data = json.load(f)

        # ensure keys exist
        for k in ("pages", "tables", "figures"):
            if k not in data:
                data[k] = []

        print(
            f"[RAG] Loaded metadata: "
            f"{len(data['pages'])} pages, "
            f"{len(data['tables'])} tables, "
            f"{len(data['figures'])} figures"
        )
        return data

    # ------------------------------------------------------------------
    # CHUNKING
    # ------------------------------------------------------------------

    def _chunk_text(
        self,
        text: str,
        page: int,
        source_name: str,
        doc_id: str = "default",
        pdf_source: str = "",
    ) -> List[Chunk]:
        """
        Deterministic Semantic Chunking via Markdown headers.
        """
        if not text.strip():
            return []
             
        print(f"[RAG] Deterministic Chunking page {page} for {doc_id}...")
        chunker = SemanticChunker()
        semantic_chunks = chunker.chunk_document(text, doc_id, page)
        
        chunks: List[Chunk] = []
        for idx, sc in enumerate(semantic_chunks):
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    text=sc.text,
                    source=source_name,
                    page=page,
                    chunk_index=idx,
                    doc_id=doc_id,
                    metadata={
                        "section_type": "text", 
                        "page": page, 
                        "chunk_index": idx, 
                        "doc_id": doc_id,
                    },
                    title=sc.title,
                    topic=sc.topic,
                    summary=sc.summary,
                    keywords=", ".join(sc.keywords),
                    quality_score=sc.quality_score,
                    pdf_source=pdf_source
                )
            )

        return chunks

    def build_chunks_from_metadata(self, doc_id: str = "default") -> List[Chunk]:
        """
        Combine:
          - page text chunks
          - table "virtual chunks" (full_text or preview)
          - figure/graph caption chunks
        into a single list of Chunk objects.
        """
        chunks: List[Chunk] = []

        # 1) Page text
        for page_entry in self.metadata.get("pages", []):
            page = page_entry.get("page")
            text = page_entry.get("text", "") or ""
            if not text.strip():
                continue
            text_chunks = self._chunk_text(
                text=text,
                page=page,
                source_name=f"{doc_id}.pdf",
                doc_id=doc_id,
                pdf_source=f"{doc_id}.pdf",
            )
            chunks.extend(text_chunks)

        # 2) Tables
        tables_data = self.metadata.get("tables", {})
        # Handle both dict and list formats
        if isinstance(tables_data, dict):
            tables_data = tables_data.values()
        
        for t in tables_data:
            page = t.get("page")
            csv_path = t.get("table_csv") or t.get("csv_file")
            full_text = (t.get("full_text") or "").strip()
            preview_rows = t.get("preview") or []

            if full_text:
                body = full_text[:3000]
            else:
                body = "\n".join(
                    ", ".join(row) for row in preview_rows[:10]
                )[:3000]

            if not body.strip():
                continue

            text = f"[TABLE] Page {page}\n{body}"
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    text=text,
                    source=csv_path or "",
                    page=page,
                    chunk_index=0,
                    doc_id=doc_id,
                    metadata={
                        "section_type": "table",
                        "page": page,
                        "table_csv": csv_path,
                        "preview_rows": preview_rows,
                        "full_text": full_text,
                        "doc_id": doc_id,
                    },
                )
            )

        # 3) Figures / graphs
        figures_data = self.metadata.get("figures", {})
        # Handle both dict and list formats
        if isinstance(figures_data, dict):
            figures_data = figures_data.values()
        
        for fig in figures_data:
            page = fig.get("page")
            caption = fig.get("caption") or ""
            kind = fig.get("kind") or "image"
            image_path = fig.get("image_path") or ""

            if not caption.strip():
                continue

            text = f"[FIGURE] Page {page} ({kind}): {caption}"
            chunks.append(
                Chunk(
                    id=str(uuid.uuid4()),
                    text=text,
                    source=image_path,
                    page=page if page is not None else -1,
                    chunk_index=0,
                    doc_id=doc_id,
                    metadata={
                        "section_type": "figure",
                        "page": page,
                        "kind": kind,
                        "image_path": image_path,
                        "caption": caption,
                        "doc_id": doc_id,
                    },
                )
            )

        print(f"[RAG] Built {len(chunks)} chunks from metadata.")
        return chunks

    # ------------------------------------------------------------------
    # EMBEDDING + INGEST
    # ------------------------------------------------------------------

    def embed(self, texts: List[str]) -> np.ndarray:
        vecs = self.embed_model.encode(texts, show_progress_bar=False)
        return np.asarray(vecs, dtype="float32")

    def ingest_from_doc_id_output(self, doc_id: str) -> None:
        """
        Load metadata from outputs/{doc_id}/metadata.json and ingest chunks.
        This is used when ingesting a newly extracted document.
        """
        output_dir = self.base_dir / "outputs" / doc_id
        metadata_file = output_dir / "metadata.json"
        
        if not metadata_file.exists():
            print(f"[Ingest] No metadata found at {metadata_file}")
            return
        
        # Temporarily load and switch metadata
        with open(metadata_file) as f:
            self.metadata = json.load(f)
        
        # Ensure keys exist
        for k in ("pages", "tables", "figures"):
            if k not in self.metadata:
                self.metadata[k] = []
        
        print(f"[Ingest] Loaded doc-specific metadata from {metadata_file}")
        self.ingest_from_metadata(doc_id=doc_id)

    def ingest_from_metadata(self, doc_id: str = "default") -> None:
        """
        Build chunks from metadata.json and ingest all into LanceDB.
        Assumes the Lance table already exists with correct schema.
        """
        print(f"[Ingest] Building chunks from metadata.json (doc_id={doc_id}) …")
        chunks = self.build_chunks_from_metadata(doc_id=doc_id)
        if not chunks:
            print("[Ingest] No chunks to ingest.")
            return

        embed_blocks = []
        for c in chunks:
            if c.summary or c.topic:
                # Optimized context-aware string for embedding
                composite = f"Category: {c.topic}\nSummary: {c.summary}\n\n{c.text}"
                embed_blocks.append(composite)
            else:
                embed_blocks.append(c.text)

        vecs = self.embed(embed_blocks)

        rows = []
        for i, c in enumerate(chunks):
            section_type = c.metadata.get("section_type")
            src = c.source

            # Normalize 'source' field:
            #  - text → pdf name
            #  - table → CSV path
            #  - figure → image path
            if section_type == "text":
                if not src:
                    src = "CERN_Yellow_Report_357576.pdf"
            elif section_type == "table":
                src = c.metadata.get("table_csv") or src or ""
            elif section_type == "figure":
                src = c.metadata.get("image_path") or src or ""

            rows.append(
                {
                    "id": c.id,
                    "text": c.text,
                    "source": src,
                    "page": c.page,
                    "chunk_index": c.chunk_index,
                    "doc_id": c.doc_id,  # Track document source
                    "title": c.title,
                    "topic": c.topic,
                    "summary": c.summary,
                    "keywords": c.keywords,
                    "quality_score": float(c.quality_score),
                    "vector": vecs[i],  # list[float32] of length 768
                }
            )

        print(f"[Ingest] Storing {len(rows)} rows into LanceDB …")
        self.store.add(rows)
        print("[Ingest] Done.")

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        doc_ids: Optional[List[str]] = None,
        doc_id: Optional[str] = None,
        original_query: Optional[str] = None,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Search LanceDB and split results into:
          - text_hits
          - figure_hits
          - table_hits
        Each hit: {score, page, text, source, section_type, doc_id, ...}
        
        If doc_ids is specified, exclusively scans inside those notebook documents.
        """
        if doc_id and not doc_ids:
            doc_ids = [doc_id]

        vec = self.embed([query])[0].tolist()
        # Over-fetch and then split by type
        try:
            raw = self.store.search(vec, doc_ids=doc_ids, top_k=top_k * 5)
        except Exception as e:
            print(f"[RAG] search failed ({e}), retrying once...")
            raw = self.store.search(vec, doc_ids=doc_ids, top_k=top_k * 5)

        rerank_q = original_query if original_query else query
        if raw:
            # Re-rank strictly based on original_query
            pairs = [[rerank_q, r.get("text", "")] for r in raw]
            scores = self.reranker.predict(pairs)
            for i, r in enumerate(raw):
                r["rerank_score"] = float(scores[i])
            
            # Sort all raw results by the new CrossEncoder score
            raw = sorted(raw, key=lambda x: x.get("rerank_score", 0.0), reverse=True)

        hits: List[Dict[str, Any]] = []
        for r in raw:
            text = r.get("text", "") or ""
            source = r.get("source", "") or ""
            page = r.get("page")
            distance = r.get("_distance", 0.0)
            doc_id_result = r.get("doc_id", "default")
            title = r.get("title", "")
            topic = r.get("topic", "")
            summary = r.get("summary", "")
            keywords = r.get("keywords", "")
            quality_score = r.get("quality_score", 0.0)

            # Note: doc_ids is already filtered at the vector engine layer

            if text.startswith("[TABLE]"):
                section_type = "table"
            elif text.startswith("[FIGURE]"):
                section_type = "figure"
            else:
                section_type = "text"

            hit: Dict[str, Any] = {
                "score": float(distance),
                "page": page,
                "text": text,
                "source": source,
                "section_type": section_type,
                "doc_id": doc_id_result,
                "title": title,
                "topic": topic,
                "summary": summary,
                "keywords": keywords,
                "quality_score": quality_score,
                "pdf_source": r.get("pdf_source", ""),
            }

            if section_type == "table" and source.endswith(".csv"):
                hit["table_csv"] = source
            if section_type == "figure" and (
                source.endswith(".png")
                or source.endswith(".jpg")
                or source.endswith(".jpeg")
            ):
                hit["image_path"] = source

            hits.append(hit)

        # Split and truncate per type
        text_hits = [h for h in hits if h["section_type"] == "text"][:top_k]
        figure_hits = [h for h in hits if h["section_type"] == "figure"][:top_k]
        table_hits = [h for h in hits if h["section_type"] == "table"][:top_k]

        return text_hits, figure_hits, table_hits
