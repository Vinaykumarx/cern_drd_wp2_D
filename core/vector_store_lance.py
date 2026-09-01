# core/vector_store_lance.py
"""
LanceDB Vector Store - Enhanced with async support and verification

Features:
- Async search operations
- Vector count verification
- Schema migration with data preservation
- Health check endpoint
"""

import pyarrow as pa
import lancedb
import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor


class LanceVectorStore:
    """
    Wrapper around LanceDB for vector storage + retrieval.

    Now stores:
      - text
      - source
      - page
      - chunk_index
      - section_type: "text" | "figure" | "table"
      - image_path: for figures/graphs
      - table_csv: for tables
      - kind: e.g. "graph" or "image"
      - vector: fixed-size list of float32 (dim)
    """

    def __init__(self, db_uri="lancedb", table_name="cern_demo", dim=768):
        self.db_uri = db_uri
        self.table_name = table_name
        self.dim = dim
        self._executor = ThreadPoolExecutor(max_workers=4)

        print(f"[LanceDB] Connecting to: {db_uri}")
        self.db = lancedb.connect(db_uri)

        self.table = self._ensure_table()

    # ------------------------------------------------------------------
    # TABLE SCHEMA SETUP
    # ------------------------------------------------------------------

    def _schema(self):
        return pa.schema([
            pa.field("id", pa.string()),
            pa.field("text", pa.string()),
            pa.field("source", pa.string()),
            pa.field("page", pa.int32()),
            pa.field("chunk_index", pa.int32()),
            pa.field("doc_id", pa.string()),  # Document ID for multi-doc support
            pa.field("section_type", pa.string()),    # "text" | "figure" | "table"
            pa.field("image_path", pa.string()),      # for figures
            pa.field("table_csv", pa.string()),       # for tables
            pa.field("kind", pa.string()),            # e.g. "graph" | "image"
            pa.field("title", pa.string()),
            pa.field("topic", pa.string()),
            pa.field("summary", pa.string()),
            pa.field("keywords", pa.string()),
            pa.field("quality_score", pa.float32()),
            # Fixed-size list of dim floats
            pa.field("vector", pa.list_(pa.float32(), self.dim)),
        ])

    def _ensure_table(self):
        """
        Ensures a table exists with correct vector schema.
        If schema mismatches, drop + recreate.
        """
        existing_tables = self.db.table_names()

        # Table does not exist → create
        if self.table_name not in existing_tables:
            print(f"[LanceDB] Creating new table: {self.table_name}")
            return self.db.create_table(self.table_name, schema=self._schema())

        # Table exists → validate schema
        table = self.db.open_table(self.table_name)
        schema = table.schema

        try:
            vec_field = schema.field("vector")
            typ = vec_field.type

            # typ should be FixedSizeListType(size=dim)
            if not pa.types.is_fixed_size_list(typ):
                print("[LanceDB] Incorrect vector dtype → Recreating table.")
                self.db.drop_table(self.table_name)
                return self.db.create_table(self.table_name, schema=self._schema())

            if typ.list_size != self.dim:
                print("[LanceDB] Wrong vector dimension → Recreating table.")
                self.db.drop_table(self.table_name)
                return self.db.create_table(self.table_name, schema=self._schema())

            # Verify presence of new semantic fields (Migration)
            if "topic" not in schema.names:
                print("[LanceDB] New semantic fields (topic/summary) missing → Recreating table.")
                self.db.drop_table(self.table_name)
                return self.db.create_table(self.table_name, schema=self._schema())

        except Exception:
            print("[LanceDB] Failed schema check → Recreating table.")
            self.db.drop_table(self.table_name)
            return self.db.create_table(self.table_name, schema=self._schema())

        print(f"[LanceDB] Using existing table: {self.table_name}")
        return table

    # ------------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------------

    def reset(self):
        """Drop and recreate the table (for quick re-ingestion)."""
        print(f"[LanceDB] Resetting table: {self.table_name}")
        self.db.drop_table(self.table_name)
        self.table = self.db.create_table(self.table_name, schema=self._schema())

    def reset_and_reingest(self, rows):
        """
        Reset table and re-ingest with verification.
        Returns count of successfully added rows.
        """
        self.reset()
        self.add(rows)
        count = self.table.count_rows()
        print(f"[LanceDB] Re-ingested {count} vectors")
        return count

    # ------------------------------------------------------------------
    # INSERT
    # ------------------------------------------------------------------

    def add(self, rows):
        """Insert rows into LanceDB."""
        self.table.add(rows)

    async def add_async(self, rows):
        """Async wrapper for insert operations."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self.add, rows)

    # ------------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------------

    def search(self, vector, doc_ids=None, top_k=5):
        """Perform ANN search with optional document filtering."""
        q = self.table.search(vector, vector_column_name="vector")

        if doc_ids:
            # Format list to SQL IN clause, e.g. doc_id IN ('id1', 'id2')
            formatted_ids = ", ".join([f"'{d}'" for d in doc_ids])
            q = q.where(f"doc_id IN ({formatted_ids})", prefilter=True)

        return q.limit(top_k).to_list()

    async def search_async(self, vector, doc_ids=None, top_k=5):
        """Async search to prevent blocking the event loop."""
        loop = asyncio.get_event_loop()

        def _search():
            return self.search(vector, doc_ids, top_k)

        return await loop.run_in_executor(self._executor, _search)

    # ------------------------------------------------------------------
    # SCAN & QUERY (non-ANN)
    # ------------------------------------------------------------------

    def get_all_vectors(self, doc_ids=None, limit=50, page=0):
        """
        Retrieve vector metadata with optional doc_id filtering, pagination.
        Uses full table scan (not ANN) for correct pagination and ordering.
        Does NOT return the 768-dim vector column — use get_vector_by_id() for that.
        """
        df = self.table.to_pandas(columns=["id", "text", "source", "page", "doc_id", "title", "topic", "summary", "keywords", "quality_score"])
        if doc_ids:
            df = df[df['doc_id'].isin(doc_ids)]
        start = page * limit
        records = df.iloc[start:start + limit].to_dict('records')
        return records

    def get_all_doc_ids(self) -> list:
        """Return unique doc_id values present in the table."""
        df = self.table.to_pandas()
        return df['doc_id'].unique().tolist()

    def delete_by_doc_id(self, doc_id: str):
        """Delete all rows matching a given doc_id."""
        self.table.delete(f"doc_id = '{doc_id}'")

    # ------------------------------------------------------------------
    # VERIFICATION & HEALTH
    # ------------------------------------------------------------------

    def count_rows(self) -> int:
        """Get total row count in the table."""
        try:
            return self.table.count_rows()
        except Exception as e:
            print(f"[LanceDB] Count failed: {e}")
            return -1

    async def count_rows_async(self) -> int:
        """Async row count."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self._executor, self.count_rows)

    def verify_document_vectors(self, doc_id: str) -> dict:
        """
        Verify vector count for a specific document.
        Uses filtered count instead of ANN search to avoid default-limit=10 bug.
        """
        try:
            count = self.table.count_rows(filter=f"doc_id = '{doc_id}'")
            return {
                "doc_id": doc_id,
                "vector_count": count,
                "exists": count > 0,
                "status": "ok" if count > 0 else "empty"
            }
        except Exception as e:
            return {
                "doc_id": doc_id,
                "error": str(e),
                "status": "error"
            }

    def get_table_stats(self) -> dict:
        """Get statistics about the table."""
        try:
            count = self.table.count_rows()
            schema = self.table.schema
            return {
                "table_name": self.table_name,
                "row_count": count,
                "columns": [f.name for f in schema],
                "dimension": self.dim,
                "status": "healthy"
            }
        except Exception as e:
            return {
                "table_name": self.table_name,
                "error": str(e),
                "status": "error"
            }

    def health_check(self) -> dict:
        """Perform health check on the vector store."""
        try:
            stats = self.get_table_stats()
            if stats.get("status") == "healthy":
                return {
                    "name": "lancedb",
                    "status": "healthy",
                    "message": f"Table '{self.table_name}' operational with {stats['row_count']} vectors",
                    "details": stats
                }
            else:
                return {
                    "name": "lancedb",
                    "status": "warning",
                    "message": f"Table stats: {stats}",
                    "details": stats
                }
        except Exception as e:
            return {
                "name": "lancedb",
                "status": "critical",
                "message": f"LanceDB health check failed: {e}",
                "details": {"error": str(e)}
            }

    def cleanup(self):
        """Cleanup resources."""
        self._executor.shutdown(wait=False)