"""
LanceDB Vector Store Implementation for CERN Multimodal RAG.
Provides zero-server, high-performance local vector storage with metadata filtering.
"""

import os
from typing import List, Optional
import numpy as np
import lancedb
import pyarrow as pa

from core.chunkers.base import Chunk
from core.storage.base import BaseVectorStore, SearchResult


class LanceDBStore(BaseVectorStore):
    def __init__(self, uri: str = "lancedb", table_name: str = "cern_chunks"):
        super().__init__(uri=uri, table_name=table_name)
        os.makedirs(self.uri, exist_ok=True)
        self.db = lancedb.connect(self.uri)
        self._table = None

    def _get_table(self, vector_dim: Optional[int] = None):
        if self._table is not None:
            return self._table

        if self.table_name in self.db.table_names():
            self._table = self.db.open_table(self.table_name)
            return self._table

        if vector_dim is None:
            raise ValueError(
                f"Table {self.table_name} does not exist and vector_dim was not provided."
            )

        # Define explicit PyArrow schema
        schema = pa.schema([
            pa.field("id", pa.string()),
            pa.field("doc_id", pa.string()),
            pa.field("filename", pa.string()),
            pa.field("page_number", pa.int32()),
            pa.field("section", pa.string()),
            pa.field("element_type", pa.string()),
            pa.field("text", pa.string()),
            pa.field("citation_anchor", pa.string()),
            pa.field("vector", pa.list_(pa.float32(), vector_dim)),
        ])

        self._table = self.db.create_table(self.table_name, schema=schema, mode="create")
        return self._table

    def add_chunks(self, chunks: List[Chunk], embeddings: np.ndarray) -> int:
        if not chunks:
            return 0
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks count must match embeddings count.")

        vector_dim = embeddings.shape[1]
        table = self._get_table(vector_dim=vector_dim)

        records = []
        for chunk, emb in zip(chunks, embeddings):
            records.append({
                "id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "filename": chunk.filename,
                "page_number": int(chunk.page_number),
                "section": chunk.section or "",
                "element_type": chunk.element_type,
                "text": chunk.content,
                "citation_anchor": chunk.citation_anchor,
                "vector": emb.tolist(),
            })

        table.add(records)
        return len(records)

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        doc_id: Optional[str] = None,
        filter_expr: Optional[str] = None,
    ) -> List[SearchResult]:
        if self.table_name not in self.db.table_names():
            return []

        table = self._get_table()
        query_builder = table.search(query_vector.tolist()).limit(top_k)

        # Build filter expression
        active_filter = filter_expr
        if doc_id:
            doc_filter = f"doc_id = '{doc_id}'"
            active_filter = f"{active_filter} AND {doc_filter}" if active_filter else doc_filter

        if active_filter:
            query_builder = query_builder.where(active_filter)

        results_df = query_builder.to_pandas()
        search_results: List[SearchResult] = []

        for _, row in results_df.iterrows():
            # In LanceDB cosine/L2 distance: convert distance to similarity score
            distance = float(row.get("_distance", 0.0))
            similarity_score = max(0.0, 1.0 - distance)

            search_results.append(
                SearchResult(
                    chunk_id=str(row["id"]),
                    doc_id=str(row["doc_id"]),
                    filename=str(row["filename"]),
                    page_number=int(row["page_number"]),
                    section=str(row.get("section", "")),
                    element_type=str(row.get("element_type", "text")),
                    content=str(row["text"]),
                    score=similarity_score,
                    citation_anchor=str(row["citation_anchor"]),
                    metadata={},
                )
            )

        return search_results

    def count(self, doc_id: Optional[str] = None) -> int:
        if self.table_name not in self.db.table_names():
            return 0
        table = self._get_table()
        if doc_id:
            df = table.search().where(f"doc_id = '{doc_id}'").limit(100000).to_pandas()
            return len(df)
        return len(table)

    def delete_doc(self, doc_id: str) -> bool:
        if self.table_name not in self.db.table_names():
            return False
        table = self._get_table()
        table.delete(f"doc_id = '{doc_id}'")
        return True
