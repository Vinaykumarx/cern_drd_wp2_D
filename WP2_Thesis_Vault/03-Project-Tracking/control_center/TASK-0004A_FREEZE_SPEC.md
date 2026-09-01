# TASK-0004A Migration Freeze Specification

**Status:** Draft  
**Date:** 2026-06-15  
**Author:** AI Agent (TASK-0004A)  
**Phase:** A — Freeze, Baseline, Shadow Mode Contract  
**Next Phase:** TASK-0004B — Implementation (gated by this document's criteria)

---

## Table of Contents

1. [Final Freeze Contract](#1-final-freeze-contract)
2. [Golden Baseline Design](#2-golden-baseline-design)
3. [Shadow Mode Architecture](#3-shadow-mode-architecture)
4. [Diff & Validation Contract](#4-diff--validation-contract)
5. [Migration Gate Criteria](#5-migration-gate-criteria)

---

## 1. Final Freeze Contract

### 1.1 Scope of Phase 1 Changes

Phase 1 replaces 5 of the 6 extraction sub-functions in `extract_with_docid.py` with Docling-native capabilities. The replaced functions and their Docling equivalents:

| # | Current Function | Current Tool | Docling Replacement | Output File |
|---|-----------------|-------------|-------------------|-------------|
| 1 | `_extract_tables_docid()` | pdfplumber + Camelot | `table.export_to_dataframe(doc)` → CSV | `tables_index.json` + CSV files |
| 2 | `_extract_images_docid()` | PyMuPDF `page.get_images()` | `picture.get_image(doc)` → PIL → PNG | `figures_index.json` + PNG files |
| 3 | `_extract_graphs_docid()` | OpenCV contour heuristic | `PictureAnnotation.predicted_classes` | embedded in `figures_index.json` |
| 4 | `_caption_images_docid()` | BLIP (transformers) | `picture.caption_text` | embedded in `figures_index.json` |
| 5 | `_extract_markdown_tables_from_text()` | regex-based | eliminated (tables from `doc.tables` directly) | (removed) |
| — | `pymupdf4llm` fallback | lines 268–302 | eliminated (Docling only) | (removed from requirements.txt) |

The `_extract_markdown_docid()` function is **enhanced**, not replaced. Its Docling already-in-place body (lines 202–263) is extended to also walk `doc.tables`, `doc.pictures`, and to handle 10+ additional `DocItemLabel` values.

### 1.2 What Must NOT Change (Hard Constraints)

| Constraint | Rationale |
|-----------|-----------|
| **No changes to `backend/main.py`** | Architecture lock — canonical entry point |
| **No changes to `core/rag_pipeline.py`** | Downstream consumer — must be transparent |
| **No changes to `core/vector_store_lance.py`** | Final storage — no schema changes |
| **No changes to `core/semantic_chunker.py`** | Chunking logic must remain identical |
| **No changes to `core/document_manager.py`** | Document state management unchanged |
| **No changes to `core/docling_parser.py`** | Standalone prototype — keep as reference |
| **No changes to `control_center/`** | Dashboard, validator, bootstrap, architecture lock |
| **No changes to `knowledge_system/`** | Memory layer — not involved in extraction |
| **No changes to `extraction/extract_vlm_layout.py`** | VLM recovery — not affected by this phase |
| **No changes to `requirements.txt` structure** | Only add `docling>=2.102`, remove `pymupdf4llm`; do not reorder other deps |
| **No removal of `_recover_sparse_text_pages()`** | Kept for Phase 2 (OCR integration) |
| **No changes to `outputs/{doc_id}/` directory structure** | Every file path must remain the same |
| **No changes to FastAPI endpoint signatures** | `/api/ingest_document`, `/api/query`, etc. unchanged |
| **No changes to dashboard panels or API** | Dashboard is read-only, must stay consistent |

### 1.3 Files Allowed to Modify

| File | Modification Scope |
|------|-------------------|
| `extraction/extract_with_docid.py` | Replace 5 sub-functions, enhance `_extract_markdown_docid` walker |
| `requirements.txt` | Add `docling>=2.102`, remove `pymupdf4llm` |
| `core/docling_parser.py` | **Optional** — align with new extraction pattern (non-essential) |
| `docs/ARCHITECTURE.md` | **Optional** — update architecture diagram references |
| `README.md` | **Optional** — update dependency list |

No other files may be touched.

### 1.4 Output Schema Invariants

The `metadata.json` output at `outputs/{doc_id}/metadata.json` must be structurally identical to the current schema. Downstream consumers (`rag_pipeline.py:build_chunks_from_metadata`) must receive the exact same keys and nesting.

#### Invariant: `metadata.json` top-level structure

```json
{
  "doc_id": "<string>",
  "pages": [
    {
      "page": <int>,
      "text": "<string>",
      "doc_id": "<string>"
    }
  ],
  "tables": {
    "<table_id>": {
      "page": <int>,
      "index": <int>,
      "csv_file": "<string>",
      "doc_id": "<string>"
    }
  },
  "figures": {
    "<figure_id>": {
      "page": <int>,
      "image_path": "<string>",
      "doc_id": "<string>",
      "caption": "<string>",
      "kind": "<string>"
    }
  }
}
```

#### Invariant Rules

| Field | Rule |
|-------|------|
| `doc_id` | Must match input `doc_id` |
| `pages` | Must be a list (not dict). Every page from 1..N must appear. Page order must be ascending. |
| `pages[].page` | 1-based integer |
| `pages[].text` | String, may be empty. Must pass page ordering invariants (see §4.3). |
| `tables` | Must be a dict keyed by `page_{page_num}_table_{index}` |
| `tables[].page` | Must match page number where table was found |
| `tables[].csv_file` | Path must exist at `outputs/{doc_id}/{table_id}.csv` |
| `tables[].index` | 1-based table index on that page |
| `figures` | Must be a dict keyed by `page_{page_num}_img_{index}` (same naming as current) |
| `figures[].page` | Must match page number where figure was found |
| `figures[].image_path` | Path to PNG file that must exist |
| `figures[].caption` | String, may be empty |
| `figures[].kind` | One of `"image"` or `"graph"` (must match current classification) |
| No extra keys | No undocumented top-level keys. No undocumented keys inside pages/tables/figures entries. |

### 1.5 Rollback Conditions

A rollback is triggered if **any** of the following occur:

1. **Schema drift**: `metadata.json` from Phase 1 differs structurally from the golden baseline for any test PDF
2. **Page count mismatch**: Any test PDF produces different `len(pages)` 
3. **Table count regression**: Any test PDF produces fewer detected tables than baseline (≥10% reduction)
4. **Figure count regression**: Any test PDF produces fewer detected figures than baseline (≥10% reduction)
5. **Caption quality regression**: Automated similarity between Docling-native captions and baseline BLIP captions falls below 0.5 (cosine/BERTScore)
6. **Reading order violation**: Adjacent pages out of order or text content missing/extraneous
7. **Runtime regression**: Phase 1 extraction is slower than current pipeline by >2x for any single PDF
8. **CRITICAL validation violation**: Architecture validator detects forbidden patterns in `extract_with_docid.py` (e.g., `import lancedb`, `lancedb.connect()`)
9. **Downstream failure**: `build_chunks_from_metadata()` raises errors with Phase 1 output

**Rollback procedure:**
1. Revert `extraction/extract_with_docid.py` to pre-Phase-1 state
2. Revert `requirements.txt` (remove docling, restore pymupdf4llm)
3. Re-run baseline on all test PDFs to confirm restoration
4. File a rollback report in `control_center/DECISIONS.md`

---

## 2. Golden Baseline Design

### 2.1 Baseline Capture Strategy

The golden baseline is the set of all extraction outputs produced by the **current** `extract_with_docid.py` on a curated set of CERN PDFs. These outputs are frozen and used as the reference for shadow mode comparison.

### 2.2 Dataset Selection Strategy

Select 12 PDFs covering the diversity of CERN document types:

| # | Document Type | Example | Rationale |
|---|--------------|---------|-----------|
| 1 | Standard CERN report (text-heavy) | CERN-205520 | Typical use case |
| 2 | Multi-column layout | CERN-89-12 | Tests reading order |
| 3 | Table-dense (experimental data) | CERN-XXX (with tables) | Tests table extraction |
| 4 | Figure-dense (schematics) | CERN-YYY (with diagrams) | Tests figure extraction |
| 5 | Mixed formula + text | CERN-ph-XXX | Tests formula handling |
| 6 | Scanned PDF (no text layer) | CERN-scan-XXX | Tests OCR path |
| 7 | Single page | Any simple PDF | Edge case |
| 8 | Very large (100+ pages) | CERN-annual-report | Performance test |
| 9 | Table with merged cells | CERN-XXX | Tests table structure |
| 10 | Document with footnotes/references | CERN-ph-YYY | Tests furniture handling |
| 11 | Document with rotated pages/landscape | CERN-XXX-rotated | Edge case |
| 12 | Document with multiple authors/metadata | CERN-XXX-frontmatter | Tests metadata |

**Selection criteria:**
- PDFs already present in `data/` directory are preferred (zero download)
- At least 2 PDFs must have existing non-empty `outputs/{doc_id}/` directories
- At least 1 PDF must trigger the sparse-text recovery path (scanned)
- PDFs must be under 50MB each (practical limit)

**If 12 CERN-specific PDFs are not available locally, use the available subset (min 5).** The baseline can be extended later.

### 2.3 Baseline Artifacts

For each PDF, capture the following artifacts:

#### Primary Artifacts (output of `extract_pdf_with_docid()`)

```
outputs/{doc_id}/
├── metadata.json
├── pages_text.json
├── {doc_id}_with_pages.md
├── tables_index.json
├── figures_index.json
├── page_*_table_*.csv         (one per table)
└── page_*_img_*.png           (one per figure)
```

#### Derived Artifacts (output of `rag_pipeline.ingest_from_doc_id_output()`)

```
baseline/{doc_id}/
├── chunks.json                 (list of Chunk objects from build_chunks_from_metadata)
├── embeddings.npy              (numpy array of embeddings)
└── ingested.flag               (empty marker file, confirms ingestion completed)
```

#### Snapshot Artifacts

```
baseline/
├── manifest.json               (PDF list, file hashes, sizes, extraction timestamps)
├── schema_dump.json            (structural schema of metadata.json as JSON Schema)
├── summary_stats.json          (per-doc: page count, table count, figure count, runtime)
└── SYSTEM_SNAPSHOT.txt         (pip freeze, torch version, GPU info)
```

### 2.4 Capture Procedure

```python
# Pseudocode — not to be executed now
for pdf_path in PDF_LIST:
    doc_id = derive_doc_id(pdf_path)
    if not force_reprocess and already_processed:
        skip  # use existing outputs
    metadata = extract_pdf_with_docid(pdf_path, doc_id)
    copy outputs/{doc_id}/ to baseline/{doc_id}/
    rag = RAGPipeline()
    rag.load_metadata(baseline/{doc_id}/metadata.json)
    chunks = rag.build_chunks_from_metadata(doc_id)
    save chunks.json
    save embeddings.npy
compute manifest.json, schema_dump.json, summary_stats.json
```

**Freeze rule:** Once baseline is captured, the `baseline/` directory is read-only. No subsequent changes to baseline artifacts are permitted.

---

## 3. Shadow Mode Architecture

### 3.1 Concept

Shadow mode runs the enhanced Docling extraction **in parallel** with the current pipeline, **without** feeding its output to retrieval. Both pipelines receive the same PDF. The current pipeline's output is used for retrieval as always. The Docling output is written to a separate shadow directory and compared against the golden baseline.

### 3.2 Pipeline Flow

```
PDF
├──→ CURRENT PIPELINE (unchanged)
│   ├──→ outputs/{doc_id}/          ← used for retrieval as always
│   └──→ baseline/{doc_id}/         ← golden reference (captured once)
│
└──→ DOCLING PIPELINE (new, isolated)
    ├──→ shadow/{doc_id}/           ← Docling outputs (not used for retrieval)
    └──→ reports/{doc_id}/          ← diff reports vs baseline
```

### 3.3 Isolation Boundaries

| Boundary | Rule |
|----------|------|
| **File system** | Docling writes to `shadow/{doc_id}/`. Never touches `outputs/{doc_id}/`. |
| **Database** | Docling pipeline never calls `rag.ingest()` or `vector_store_lance`. No LanceDB writes. |
| **API** | Docling pipeline is never triggered by FastAPI endpoints. Only runnable via standalone script. |
| **Dashboard** | Dashboard reads from `outputs/` and `control_center/`. Never reads `shadow/`. |
| **Memory layer** | Docling pipeline does not update session_index or knowledge_system. |
| **Architecture validator** | Must pass with 0 violations. Docling pipeline is not a new entry point — it's an internal refactor. |

### 3.4 Shadow Directory Structure

```
shadow/
├── {doc_id}/
│   ├── metadata.json
│   ├── pages_text.json
│   ├── {doc_id}_with_pages.md
│   ├── tables_index.json
│   ├── figures_index.json
│   ├── page_*_table_*.csv
│   └── page_*_img_*.png
├── shadow_manifest.json          (which PDFs have been shadow-processed)
└── shadow_summary_stats.json     (per-doc stats for comparison)
```

### 3.5 Logging Structure

```
shadow/logs/
├── {doc_id}/
│   ├── comparison_report.json    (structured diff output)
│   ├── comparison_log.txt        (human-readable diff)
│   └── errors.log                (any extraction errors)
├── shadow_run_{timestamp}.log    (master run log)
└── validation_summary.json       (aggregate pass/fail per PDF)
```

#### `comparison_report.json` Schema

```json
{
  "doc_id": "<string>",
  "timestamp": "<ISO8601>",
  "pdf_size_bytes": <int>,
  "baseline": {
    "page_count": <int>,
    "table_count": <int>,
    "figure_count": <int>,
    "extraction_time_seconds": <float>
  },
  "docling": {
    "page_count": <int>,
    "table_count": <int>,
    "figure_count": <int>,
    "extraction_time_seconds": <float>,
    "docling_version": "<string>"
  },
  "diffs": {
    "page_count_match": <bool>,
    "page_content_diffs": [
      {
        "page": <int>,
        "char_diff_count": <int>,
        "levenshtein_ratio": <float>,
        "diff_type": "added|removed|modified"
      }
    ],
    "table_diffs": [
      {
        "table_id_from_current": "<string>",
        "table_id_from_docling": "<string>",
        "page": <int>,
        "columns_match": <bool>,
        "row_count_match": <bool>,
        "cell_accuracy": <float>,
        "matched": <bool>
      }
    ],
    "figure_diffs": [
      {
        "figure_id_from_current": "<string>",
        "figure_id_from_docling": "<string>",
        "page": <int>,
        "caption_similarity": <float>,
        "caption_similarity_method": "bert_score|cosine",
        "kind_match": <bool>,
        "image_dimensions_match": <bool>,
        "matched": <bool>
      }
    ]
  },
  "overall": {
    "pass": <bool>,
    "severity": "pass|warn|fail",
    "reasons": ["<string>"]
  }
}
```

### 3.6 Shadow Runner

The shadow runner is a standalone script — the only new file created during Phase 1:

```
scripts/run_shadow_comparison.py
```

**Properties:**
- Reads `control_center/TASK-0004A_FREEZE_SPEC.md` for validation parameters (tolerance thresholds, etc.)
- Iterates over PDFs listed in `baseline/manifest.json`
- For each PDF:
  1. Runs `extract_pdf_with_docid()` with Docling Phase 1 changes
  2. Writes output to `shadow/{doc_id}/`
  3. Generates `comparison_report.json`
  4. Logs to `shadow/logs/`
- Produces `validation_summary.json` with per-PDF pass/fail
- **Exits non-zero** if any PDF fails gate criteria

This script is **only run by the developer** (not by CI, not by FastAPI startup, not by bootstrap).

---

## 4. Diff & Validation Contract

### 4.1 Schema Diff Rules

| Rule | Condition | Verdict |
|------|-----------|---------|
| R1 | `metadata.json` top-level keys differ | **FAIL** |
| R2 | `pages` is not a list | **FAIL** |
| R3 | `tables` is not a dict | **FAIL** |
| R4 | `figures` is not a dict | **FAIL** |
| R5 | Any page entry missing `page`, `text`, or `doc_id` | **FAIL** |
| R6 | Any table entry missing `page`, `index`, `csv_file`, or `doc_id` | **FAIL** |
| R7 | Any figure entry missing `page`, `image_path`, `caption`, `kind`, or `doc_id` | **FAIL** |
| R8 | Undocumented key present at top level or in any entry | **WARN** (tolerated but flagged) |
| R9 | `doc_id` value does not match expected | **FAIL** |
| R10 | `csv_file` or `image_path` path points outside `outputs/{doc_id}/` | **FAIL** |

### 4.2 Table Equivalence Rules

| Rule | Condition | Verdict |
|------|-----------|---------|
| T1 | Table count differs by >10% from baseline | **FAIL** |
| T2 | Table count differs by ≤10% (any direction) | **WARN** |
| T3 | Baseline table has no matching Docling table on same page (within IoU ≥0.5) | **WARN** per unmatched table |
| T4 | Matching tables: column count differs | **WARN** |
| T5 | Matching tables: row count differs | **WARN** |
| T6 | Matching tables: cell content accuracy < 0.8 (character-level match rate across all cells) | **WARN** |
| T7 | Matching tables: cell content accuracy < 0.5 | **FAIL** |
| T8 | All baseline tables have a match AND all Docling tables have a match in baseline | **PASS** |
| T9 | Docling detects tables that baseline missed (≥1 extra on a page where pdfplumber found 0) | **INFO** (positive signal) |

**Matching algorithm:** Two tables match if they appear on the same page AND their bounding boxes (IoU ≥ 0.5) OR (if bounding boxes unavailable) their first-row column headers match by text similarity ≥ 0.7.

### 4.3 Page Ordering Invariants

| Rule | Condition | Verdict |
|------|-----------|---------|
| P1 | Page numbers in `pages[]` are not strictly ascending | **FAIL** |
| P2 | Total page count differs from baseline | **FAIL** |
| P3 | Any page number is missing (gap in sequence) | **FAIL** |
| P4 | Any page number is duplicated | **FAIL** |
| P5 | Per-page text content length differs from baseline by >50% | **WARN** |
| P6 | Per-page text content length differs from baseline by >80% | **FAIL** |
| P7 | Per-page first 100 characters differ entirely (suggesting reading-order shift) | **WARN** |
| P8 | Page text is completely empty while baseline had content | **FAIL** |
| P9 | `=== PAGE X ===` marker count in `{doc_id}_with_pages.md` does not match page count | **FAIL** |

### 4.4 Figure Equivalence Rules

| Rule | Condition | Verdict |
|------|-----------|---------|
| F1 | Figure count differs by >10% from baseline | **FAIL** |
| F2 | Figure count differs by ≤10% | **WARN** |
| F3 | Baseline figure has no matching Docling figure on same page | **WARN** per unmatched figure |
| F4 | Matching figures: `kind` field differs | **WARN** |
| F5 | Matching figures: caption text differs | Compare via BERTScore (see §4.5) |
| F6 | Image dimensions (width × height) differ by >20% | **WARN** |
| F7 | Docling detects figures that baseline missed | **INFO** (positive signal) |
| F8 | All image_path files exist and are valid PNG | **FAIL** if missing or corrupt |

**Matching algorithm:** Two figures match if they appear on the same page AND either (a) their bounding boxes overlap (IoU ≥ 0.3) or (b) their captions have similarity ≥ 0.5.

### 4.5 Tolerance Thresholds

| Metric | Tolerance | Breach Action |
|--------|-----------|---------------|
| Page count mismatch | 0% (exact match) | FAIL |
| Table count change | ±10% | WARN; ±10% = FAIL |
| Figure count change | ±10% | WARN; ±10% = FAIL |
| Cell content accuracy | ≥0.8 match rate | WARN; <0.5 = FAIL |
| Caption BERTScore | ≥0.5 vs BLIP baseline | WARN; <0.3 = FAIL |
| Page text length diff | ≤50% per page | WARN; >80% = FAIL |
| Image dimension diff | ≤20% per axis | WARN; >20% = FAIL |
| Runtime increase | ≤2x baseline | WARN; >2x = FAIL (not gate-blocking) |
| Empty pages | 0 vs baseline | FAIL if baseline had content |
| Missing CSV files | 0 | FAIL if any |
| Missing PNG files | 0 | FAIL if any |

### 4.6 Validation Summary Severity

| Severity | Meaning | Action |
|----------|---------|--------|
| **PASS** | All rules pass within tolerance | Gate criteria met |
| **WARN** | Non-critical diffs detected (tolerated) | Review logs; proceed with caution |
| **FAIL** | Critical diff detected (violates invariant) | Gate criteria NOT met; rollback |

---

## 5. Migration Gate Criteria

### 5.1 Conditions to Proceed to TASK-0004B

**ALL** of the following must be true:

| # | Criterion | Verification Method |
|---|-----------|-------------------|
| G1 | All 12 (or available subset) PDFs in `baseline/manifest.json` have been shadow-processed | `shadow/shadow_manifest.json` lists all PDFs with status `processed` |
| G2 | Every PDF has `overall.pass == true` in its `comparison_report.json` | Aggregate check |
| G3 | Zero schema FAIL verdicts across all PDFs (rules R1–R10) | Aggregate check |
| G4 | Zero page FAIL verdicts across all PDFs (rules P1–P9) | Aggregate check |
| G5 | Zero table FAIL verdicts across all PDFs (rules T1, T7) | Aggregate check |
| G6 | Zero figure FAIL verdicts across all PDFs (rules F1, F8) | Aggregate check |
| G7 | WARN verdicts across all categories ≤20% of total checks | Aggregate check |
| G8 | Architecture validator passes with 0 CRITICAL violations on Phase 1 code | `core/architecture_validator.py` scan |
| G9 | `build_chunks_from_metadata()` succeeds with shadow `metadata.json` for all PDFs | Dry-run chunking test |
| G10 | No rollback conditions triggered (§1.5) | Manual confirmation |
| G11 | All WARN verdicts have been reviewed and documented in a decision record | `control_center/DECISIONS.md` entry |
| G12 | Documents TASK-0004A results in latest_state.md and session_index.json | State files updated |

### 5.2 Failure Conditions

A failure occurs if **any** of the following is true at gate evaluation time:

| # | Condition | Action |
|---|-----------|--------|
| FC1 | G1 not met (incomplete shadow processing) | Do not proceed. Complete shadow run. |
| FC2 | G2 not met (at least one PDF fails) | Do not proceed. Investigate per-PDF report. |
| FC3 | G8 not met (architecture violation) | Do not proceed. Fix violation. |
| FC4 | G9 not met (chunking failure) | Do not proceed. Fix schema compatibility. |
| FC5 | G10 triggered (rollback condition) | Execute rollback procedure (§1.5). |
| FC6 | G11 not met (unreviewed warnings) | Do not proceed. Review and document each WARN. |
| FC7 | Any `comparison_report.json` has `overall.severity == "fail"` | Do not proceed. Fix root cause. |

### 5.3 Rollback Triggers

Rollback must be initiated immediately if:

| # | Trigger | Detection |
|---|---------|-----------|
| RBT1 | A production PDF ingestion produces different chunks than pre-Phase-1 | Manual QC |
| RBT2 | User reports degraded retrieval quality within 48 hours of Phase 1 deployment | User feedback |
| RBT3 | Architecture validator finds a CRITICAL violation in Phase 1 code that was not present pre-Phase-1 | CI or startup check |
| RBT4 | `rag_pipeline.ingest_from_doc_id_output()` raises unexpected exception in production | Error logs |
| RBT5 | Dashboard metrics show >20% drop in retrieval recall or precision | Dashboard monitoring |

**Rollback is always preferred over hotfix.** If any RBT fires, revert to pre-Phase-1 state within 1 hour. The rollback report must be filed within 24 hours.

### 5.4 Gate Evaluation Procedure

```text
1. Run: python scripts/run_shadow_comparison.py
2. Check: shadow/logs/validation_summary.json
3. For each PDF:
   a. Read comparison_report.json
   b. Verify overall.pass == true
   c. Log any WARN items to review log
4. Run: python -c "from core.architecture_validator import scan_project; issues = scan_project(); assert len([i for i in issues if i.severity == 'CRITICAL']) == 0"
5. Run: python -c "from core.rag_pipeline import RAGPipeline; r = RAGPipeline(); r.load_metadata('shadow/{doc_id}/metadata.json'); chunks = r.build_chunks_from_metadata('{doc_id}'); assert len(chunks) > 0"
6. Review all WARN items from step 3
7. Document approval in control_center/DECISIONS.md
8. Update knowledge_system/ and session_index.json
9. Proceed to TASK-0004B
```

---

## Appendix A: Dependency Changes

### Added to `requirements.txt`
```
docling>=2.102
```

### Removed from `requirements.txt`
```
pymupdf4llm==0.0.5
```

### Unchanged (still required for Phase 2)
```
PyMuPDF          # still used by _recover_sparse_text_pages()
pytesseract      # still used by _recover_sparse_text_pages()
pdfplumber       # fallback only (kept for safety)
transformers     # still used by VLM recovery
opencv-python    # still used by VLM recovery (extract_vlm_layout.py)
```

## Appendix B: Phase 1 File Modification Summary

| File | Action |
|------|--------|
| `extraction/extract_with_docid.py` | Replace `_extract_tables_docid` with Docling tables; replace `_extract_images_docid` with `doc.pictures`; replace `_extract_graphs_docid` with `PictureAnnotation`; replace `_caption_images_docid` with `picture.caption_text`; enhance item walker in `_extract_markdown_docid` to handle 10+ labels; remove `_extract_markdown_tables_from_text`; remove `pymupdf4llm` import and fallback block (lines 268–302) |
| `requirements.txt` | Add `docling>=2.102`, remove `pymupdf4llm==0.0.5` |
| `scripts/run_shadow_comparison.py` | NEW — standalone shadow runner script |
| `docs/ARCHITECTURE.md` | Optional — update references from pdfplumber/pymupdf4llm to Docling |

## Appendix C: References

- Docling API: https://docling-project.github.io/docling/reference/docling_document/
- Docling Table Export Example: https://docling-project.github.io/docling/_generated/examples/export_tables/
- Docling Figure Export Example: https://docling-project.github.io/docling/_generated/examples/export_figures/
- Docling Code/Formula Enrichment: https://docling-project.github.io/docling/_generated/examples/code_formula_granite_docling/
- System Lock: `control_center/SYSTEM_LOCK.md`
- Architecture Validator: `core/architecture_validator.py`
