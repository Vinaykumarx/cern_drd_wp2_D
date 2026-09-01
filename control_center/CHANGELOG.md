# Changelog

## [2026-05-07] — Project Status Agent Created
### Added
- `project_agent.py` — Core analysis engine (742 lines)
- `project_cli.py` — Interactive task management CLI (350 lines)
- `project_dashboard.py` — Web dashboard with FastAPI + Chart.js (500+ lines)
- `project_manager.py` — Quick-start menu launcher (350+ lines)
- `start_agent.sh` — Bash quick-start script
- `health_check.py` — System health monitoring
- `validate_startup.py` — Startup validation
- `real_time_tracker.py` — Real-time monitoring
- `master_control.py` — Master control panel
- `PROJECT_AGENT_README.md`, `QUICK_START_AGENT.md`, `DELIVERABLES_SUMMARY.md`,
  `FINAL_SUMMARY.md`, `QUICK_REFERENCE.md`, `STARTUP_GUIDE.md`,
  `STARTUP_VERIFICATION.txt`, `PROJECT_TRACKING_SETUP.md` — Documentation
- `project_tasks.json` — 13 pre-identified tasks
- `IMPLEMENTATION_LOG.txt` — Implementation plan log

### Changed
- (none — first tracked state)

### Fixed
- (none — first tracked state)

## [2026-06-15] — Streamlit Deprecated, Canonical Pipeline Enforced
### Removed
- Direct ingestion bypass in `app/streamlit_app.py` (3 paths: URL import, file upload, auto-import)
- Direct RAGPipeline import and usage from Streamlit
- Direct DocumentManager and SessionManager usage from Streamlit
- Direct `extract_with_docid` imports from Streamlit

### Changed
- `app/streamlit_app.py` → `app/streamlit_app_DEPRECATED.py` (renamed)
- Streamlit now uses FastAPI HTTP client for all ingestion, retrieval, session, and document operations
- `scripts/refactor_ui.py`, `scripts/test_ux_features.py`, `examples/multi_doc_example.py` — updated file path references

### Enforced
- Canonical ingestion path: `extraction/extract_with_docid.py` (only)
- Canonical retrieval path: `core/rag_pipeline.py` → `core/vector_store_lance.py` (only)
- All RAG operations go through `backend/main.py` (FastAPI)

## [2026-06-15] — Phase G: Repository Organization
### Added
- `archive/extraction/` — deprecated extraction scripts moved here
- `archive/scripts/` — future archive target for inactive scripts
- `logs/` — centralized runtime log storage

### Removed
- `extraction/extract_with_docid.py.backup`
- `page_dump.html` (Next.js page dump, orphaned)
- `metadata.json` (empty file, orphaned)
- 4 duplicate CERN-89-12 PDFs from `data/`
- `frontend/postcss.config.js` (replaced by postcss.config.mjs)
- `lancedb_test/` (test directory, orphaned)

### Moved
- 9 deprecated extraction scripts → `archive/extraction/`
- 5 inactive scripts (scratch_chunker.py, test_cern_chat.py, test_ui_headless.py, test_ui_visually.py, repair_swarm.py) → `scripts/`
- 6 runtime logs (backend.log, dashboard.log, fastapi.log, frontend.log, ollama.log, uvicorn.log) → `logs/`

### Deprecated
- `core/chunker.py` — use `core.semantic_chunker.SemanticChunker` instead
- `core/embedder.py` — use `core.rag_pipeline.RAGPipeline.embed()` instead
