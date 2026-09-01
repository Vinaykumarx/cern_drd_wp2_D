# Architecture Decision Records

## ADR-001: Canonical Ingestion Path
**Date:** 2026-06-15
**Decision:** All ingestion must flow through `extraction/extract_with_docid.py` → `RAGPipeline` → `LanceVectorStore`.
**Rationale:** Single canonical path prevents data corruption, simplifies debugging, and enables runtime enforcement.
**Consequences:** 9 standalone extraction scripts deprecated. All ingestion now traceable.

## ADR-002: Read-Only Dashboard
**Date:** 2026-06-15
**Decision:** The Control Center Dashboard reads state files but never writes them.
**Rationale:** Separates observability from control to prevent accidental state corruption.
**Consequences:** Dashboard is purely informational. All state mutations go through FastAPI or scripts.

## ADR-003: Bootstrap Enforcement
**Date:** 2026-06-15
**Decision:** Every executable script must call `require_bootstrap()` before any other import.
**Rationale:** Ensures runtime context is always loaded and architecture validation always runs.
**Consequences:** 11 scripts updated. New scripts must follow the same pattern.

## ADR-004: Port Separation
**Date:** 2026-06-15
**Decision:** Dashboard runs on port 8899, independent from FastAPI (8000), Next.js (3000), Streamlit (8888).
**Rationale:** Prevents port conflicts. Allows dashboard to be started/stopped independently.
**Consequences:** Four independent services, each with a dedicated port.

## ADR-005: Architecture Validator Exemptions
**Date:** 2026-06-15
**Decision:** Validator meta-files (architecture_validator.py, system_validator.py, canonical_gate.py) and scripts/ directory are exempt from pattern scanning.
**Rationale:** Meta-files necessarily contain forbidden patterns in their definitions. Scripts/ is a non-production debug directory.
**Consequences:** No false positives from validator's own source code. Debug scripts can use lancedb directly.

## ADR-006: Startup Blocking on Critical Violations
**Date:** 2026-06-15
**Decision:** FastAPI refuses startup on CRITICAL violations; HIGH violations produce warnings only.
**Rationale:** Deprecated scripts exist on disk but are not executed — flagging as HIGH is correct. CRITICAL violations (direct lancedb.connect, rag.store.table.*) indicate active bypasses that must be fixed.
**Consequences:** System starts with warnings for known-deprecated files. CRITICAL violations block startup entirely.
