# Known Bugs

## BUG-001
- Description: LanceDB vector count desyncs between extraction and dashboard_status
- Severity: Critical
- Status: Fixed
- Fix: Replaced ANN search in verify_document_vectors() with filtered count_rows(). Removed destructive reset()+re-ingest from search() error recovery path. Fixed get_all_vectors() to use full table scan instead of zero-vector ANN pagination.

## BUG-002
- Description: SemanticChunker and vector searches block FastAPI async event loop
- Severity: Critical
- Status: Fixed
- Fix: Wrapped all sync rag.search(), call_local_summary(), store.get_all_vectors(), store.get_all_doc_ids(), and client.chat.completions.create() calls in FastAPI endpoints with asyncio.to_thread(). Converted /api/ingest_document to BackgroundTasks pattern. Replaced sync httpx.get()/head() calls with async http_client equivalents.

## BUG-003
- Description: Knowledge graph endpoint loads all vectors — browser freezes as DB grows
- Severity: Critical
- Status: Fixed
- Fix: Removed 768-dim vector column from get_all_vectors() (was loaded for graph but never used). Hard-capped graph at 300 nodes with early break. Reduced default limit from 50 to 30. Added truncated flag to pagination response.

## BUG-004
- Description: BLIP hardcoded to process max 3 images per PDF
- Severity: High
- Status: Open

## BUG-005
- Description: Chunk metadata uses hardcoded topics/naive keywords instead of dynamic generation
- Severity: High
- Status: Open

## BUG-006
- Description: Redundant asset storage (file system + LanceDB) — risk of desync on delete
- Severity: Medium
- Status: Open

## BUG-007
- Description: Dual frontend (Streamlit + Next.js) — features missing between them
- Severity: Medium
- Status: Open
