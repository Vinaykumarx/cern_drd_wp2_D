# SYSTEM LOCK — Canonical Architecture Enforcement

## Canonical Ingestion Path

```
PDF → extraction/extract_with_docid.extract_pdf_with_docid()
    → core.rag_pipeline.RAGPipeline.ingest_from_doc_id_output()
    → core.vector_store_lance.LanceVectorStore.add()
```

**Entry point**: `extraction/extract_with_docid.py`

**API proxy**: `POST /api/upload` or `POST /api/upload_multiple` or `POST /api/import_remote`

All ingestion must go through this chain. No other path is permitted.

---

## Canonical Retrieval Path

```
Query → core.rag_pipeline.RAGPipeline.search()
      → core.vector_store_lance.LanceVectorStore.search()
```

**Entry point**: `core.rag_pipeline.RAGPipeline`

**API proxy**: `POST /api/chat` or other FastAPI endpoints that call `rag.search()`

All retrieval must go through this chain. No other path is permitted.

---

## Canonical Vector Store

**Class**: `core.vector_store_lance.LanceVectorStore`

**Allowed access patterns**:
- `RAGPipeline.store.*` (where `store` is a `LanceVectorStore` instance)
- `LanceVectorStore.add()`, `.search()`, `.count_rows()`, `.get_all_vectors()`, `.get_all_doc_ids()`, `.delete_by_doc_id()`, `.verify_document_vectors()`, `.reset()`, `.reset_and_reingest()`, `.get_table_stats()`

All LanceDB access must go through `LanceVectorStore` wrapper methods.
Direct `lancedb.connect()` or `rag.store.table.*` is forbidden outside the store class.

---

## Forbidden Patterns

### Forbidden Imports
| Pattern | Severity | Reason |
|---------|----------|--------|
| `import lancedb` | CRITICAL | Bypasses LanceVectorStore wrapper |
| `from lancedb import ...` | CRITICAL | Bypasses LanceVectorStore wrapper |

### Forbidden Call Patterns
| Pattern | Severity | Reason |
|---------|----------|--------|
| `.connect(` | CRITICAL | Direct database connection outside store |
| `rag.store.table.` | CRITICAL | Bypasses store wrapper methods |
| `.store.table.search` | CRITICAL | Bypasses store.search() |
| `.store.table.to_pandas` | CRITICAL | Bypasses store.get_all_vectors() |
| `.store.table.delete` | CRITICAL | Bypasses store.delete_by_doc_id() |
| `.store.table.add` | CRITICAL | Bypasses store.add() |

### Forbidden Scripts
| Script | Severity | Reason |
|--------|----------|--------|
| `extraction/extract_text.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/extract_images.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/extract_tables.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/extract_graphs.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/caption_images.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/build_metadata.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/pipeline.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/extract_groq_vision.py` | HIGH | Use extract_with_docid.py instead |
| `extraction/hybrid_extractor.py` | HIGH | Use extract_with_docid.py instead |

---

## Bootstrap Enforcement

Every executable script MUST import bootstrap before any other code:

```python
from core.bootstrap import require_bootstrap; require_bootstrap()
```

This ensures the runtime context is loaded and architecture validation runs.
The FastAPI server **refuses startup** if any violations are detected.

---

## Allowed Modules (lancedb import exception)

| Module | Reason |
|--------|--------|
| `core.vector_store_lance` | Canonical store wrapper |
| `core.health_monitor` | Read-only health checks with separate connection |

---

## Verification

```bash
python -c "from core.architecture_validator import run_architecture_validation; run_architecture_validation(exit_on_fail=True)"
```

Expected output: `[ArchitectureValidator] PASS — All canonical architecture rules enforced`
