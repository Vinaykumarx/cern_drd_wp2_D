"""
Canonical Gate — Runtime validation for canonical architecture enforcement.

Ensures all ingestion and retrieval operations go through the approved paths:
  - Ingestion: extraction/extract_with_docid.py
  - Retrieval: core/rag_pipeline.RAGPipeline
  - Vector store: core/vector_store_lance.LanceVectorStore
  - API: backend/main.py (FastAPI)
"""

import os
import sys
import inspect
from pathlib import Path
from typing import Optional, List, Tuple

CANONICAL_INGESTION_MODULE = "extraction.extract_with_docid"
CANONICAL_RETRIEVAL_CLASS = "core.rag_pipeline.RAGPipeline"
CANONICAL_STORE_CLASS = "core.vector_store_lance.LanceVectorStore"
CANONICAL_API_MODULE = "backend.main"

FORBIDDEN_PATTERNS = [
    "lancedb.connect",
    "import lancedb",
    "rag.store.table.",
    ".store.table.search",
    ".store.table.to_pandas",
    ".store.table.delete",
]


class CanonicalGate:
    """
    Validates that runtime access to ingestion, retrieval, and vector store
    follows the canonical architecture path.
    """

    def __init__(self, enabled: bool = True, log_violations: bool = True):
        self.enabled = enabled
        self.log_violations = log_violations
        self._violations: List[str] = []

    def validate_caller(self, caller_frame=None) -> Tuple[bool, str]:
        """
        Inspect the call stack to verify the caller is a canonical module.
        Returns (is_valid, reason).
        """
        if not self.enabled:
            return True, "Gate disabled"

        frame = caller_frame or inspect.currentframe()
        caller_name = frame.f_globals.get("__name__", "")

        allowed_prefixes = [
            "core.rag_pipeline",
            "core.vector_store_lance",
            "core.semantic_chunker",
            "core.llm_client",
            "core.document_manager",
            "core.document_state_manager",
            "core.session_manager",
            "core.health_monitor",
            "core.cern_search",
            "core.async_chunker",
            "core.agents",
            "backend.main",
            "extraction.extract_with_docid",
            "extraction.extract_vlm_layout",
        ]

        for prefix in allowed_prefixes:
            if caller_name.startswith(prefix):
                return True, f"Canonical caller: {caller_name}"

        is_test = "unittest" in sys.modules or "pytest" in sys.modules
        if is_test:
            return True, "Test environment — bypass allowed"

        self._violations.append(f"Non-canonical caller: {caller_name}")
        if self.log_violations:
            print(f"[CanonicalGate] VIOLATION: {caller_name} is not a permitted caller")
        return False, f"Non-canonical caller: {caller_name}"

    def check_forbidden_access(self, obj: object, accessor: str) -> bool:
        """
        Check if a forbidden access pattern is being used.
        Returns True if access is allowed, False if forbidden.
        """
        if not self.enabled:
            return True

        for pattern in FORBIDDEN_PATTERNS:
            if pattern in accessor:
                self._violations.append(f"Forbidden access pattern: {accessor}")
                if self.log_violations:
                    print(f"[CanonicalGate] FORBIDDEN: {accessor}")
                return False
        return True

    def report_violations(self) -> List[str]:
        return self._violations.copy()

    def clear_violations(self):
        self._violations.clear()

    @property
    def has_violations(self) -> bool:
        return len(self._violations) > 0


_canonical_gate: Optional[CanonicalGate] = None


def get_canonical_gate() -> CanonicalGate:
    global _canonical_gate
    if _canonical_gate is None:
        _canonical_gate = CanonicalGate()
    return _canonical_gate
