# Current System State

- Active Task: TASK-0004 — extraction audit (pymupdf4llm → Docling migration plan)
- System Status: Repository organized. Deprecated scripts archived. Runtime logs in logs/. Duplicate PDFs removed. Architecture validation: 0 violations. Phases A–G complete.
- Backend Status: FastAPI running on :8000
- Retrieval Status: LanceDB connected, BGE 768-dim, Cross-Encoder reranker loaded
- Known Issues: 3 critical bugs fixed. BUG-004 (BLIP 3-image cap), BUG-005 (naive chunking keywords), BUG-006 (redundant asset storage), BUG-007 (dual frontend) remain open.
- Extraction Status: pymupdf4llm fallback in use. Docling primary path (lines 202–263 of extract_with_docid.py) working but unoptimized. Migration plan in review.
