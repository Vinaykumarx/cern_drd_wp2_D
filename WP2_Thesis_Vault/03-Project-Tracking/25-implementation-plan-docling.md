# Implementation Plan: Page-Level RAG Integration (Fully Local & Docling)

This plan outlines the integration of the supervisor's **Page-Level Citation RAG** methodology into the current **Agent Zero (CERN Multimodal RAG)** project, switching the defaults to be **fully local** and replacing the PDF parser with **IBM Docling**.

---

## 1. Architecture Comparison (Updated)

| Layer | Supervisor's Architecture | Our Workspace (Agent Zero) | Comparison & Evaluation |
| :--- | :--- | :--- | :--- |
| **PDF Extraction** | `fitz` page splitting + `marker` PDF-to-Markdown conversion. | `pymupdf4llm` + `pdfplumber` (tables) + `BLIP` (image captions) + OpenCV. | **Proposed Change:** We will replace `pymupdf4llm` and `marker` with **IBM Docling** to perform robust, layout-aware PDF extraction (see comparison below). We will preserve the exact page-level markers (`=== PAGE X ===`) during parsing. |
| **Metadata Tagging** | Inserts explicit `=== PAGE X ===` delimiters between pages. | Keeps page metadata per chunk via native PyMuPDF text location. | **Supervisor's edge:** Page delimiter strings make it extremely easy to parse, chunk, and index text on a strict page basis. We will adopt the `=== PAGE X ===` tag structure. |
| **Vector Database** | **Chroma DB** | **LanceDB** (Local-first, disk-backed) | **Our edge:** LanceDB is faster, production-ready, supports hybrid metadata queries, and scales much better. We will **keep LanceDB** but feed it page-aware metadata. |
| **Embeddings** | `nomic-embed-text` (Ollama) | `BAAI/bge-base-en-v1.5` (SentenceTransformer) | **Proposed Change:** To make the project **fully local by default**, we will switch to **local nomic-embed-text** running through our running Ollama instance, or use our pre-downloaded local BGE model (both run entirely on your local machine). |
| **Reranking** | None | `cross-encoder/ms-marco-MiniLM-L-6-v2` | **Our edge:** Reranking increases search accuracy significantly. We will keep this local reranker. |
| **Language Model** | `deepseek-r1:8b` (Local Ollama) | Groq (`llama-3.1-8b-instant`) / OpenRouter | **Proposed Change:** The backend will connect to the local Ollama instance on `http://localhost:11434/v1` using **`qwen3.6:35b`** (which is already downloaded and running locally on your hardware) as the default model, with a configuration option to select **`deepseek-r1:8b`** once pulled. |
| **Citation Prompting** | Formats context as `[filename - Page X]` and requests citations. | Formats context as `[C1] (Pg X)` and runs a self-reviewer. | **Supervisor's expectation:** Strict compliance with `[filename - Page X]` page citations. We will update our prompts to enforce this format. |

---

## 2. Docling vs. Marker Comparison

We evaluated **IBM Docling** against the supervisor's suggested **`marker`** tool:

| Dimension | IBM Docling | Marker |
| :--- | :--- | :--- |
| **Ease of Setup** | **High** (`pip install docling` is self-contained). | **Low** (Requires multiple heavy packages like Surya, Texify, layoutparser; complex dependency resolution). |
| **Table Extraction** | **Excellent** (Parses multi-column cells and complex layouts directly into Markdown/HTML tables). | **Moderate** (Can drift on complex tables or miss boundaries). |
| **Math & Formulas** | **Excellent** (Converts equations into clean LaTeX inline/block text). | **Excellent** (Specifically optimized for equations, but slower). |
| **Page Boundaries** | **Built-in** (Outputs a structured document tree representing explicit page coordinates for every element). | **Manual** (Requires splitting PDFs page-by-page to keep page indices). |
| **Resource Usage** | **Highly Efficient** (Runs quickly on CPU or GPU). | **Heavy** (High GPU memory requirement; slow on CPU). |

> [!TIP]
> **Decision:** We will use **IBM Docling** for PDF processing. It provides better table extraction, is much easier to maintain on local hardware, and allows us to insert page markers (`=== PAGE X ===`) naturally without having to split the PDF into physical separate files.

---

## 3. Web UI Overview

The frontend Web UI is built with **Next.js 15 (App Router)** and resides in the [frontend/](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/frontend) directory. 

* **Main Interface:** [frontend/src/app/page.tsx](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/frontend/src/app/page.tsx)
* **Backend Connection:** Requests sent to `/api/:path*` are proxied directly to the FastAPI server running on `http://localhost:8000/api/` via the Next.js rewrite configuration in [next.config.mjs](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/frontend/next.config.mjs).
* **Key Features:**
  1. **Telemetry Hub:** Tracks the RAG server health, active vectors, and CPU/GPU metrics.
  2. **Neural Chat:** Interactive chat panel with document filters, citation tooltips, and file drop support.
  3. **Force-Directed Graph:** Renders document hierarchies mapping Docs -> Topics -> Chunks.

---

## 4. Proposed Changes & Implementation Steps

### Step 1: Default to Fully Local
We will update the [.env](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/.env) file to configure the LLM provider to be fully local by default:
```bash
# Local Ollama Default Configuration
LLM_BASE_URL=http://localhost:11434/v1
CHAT_LLM_MODEL=qwen3.6:35b
AGENT_LLM_MODEL=qwen3.6:35b
```

### Step 2: Implement Docling Page Parser
We will write a parser utility that runs Docling, extracts the structured page contents, and outputs a merged markdown file with explicit `=== PAGE X ===` page boundaries.

#### [NEW] [docling_parser.py](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/core/docling_parser.py)
* Encapsulates the Docling document converter.
* Saves Markdown with page markers.

### Step 3: Implement Page-Aware Chunking & Ingestion
We will modify the ingestion pipeline to parse documents based on the page markers, ensuring chunk splitting happens cleanly per-page.

#### [MODIFY] [semantic_chunker.py](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/core/semantic_chunker.py)
* Update to split by page markers and then apply header-based recursive text chunking.

#### [MODIFY] [rag_pipeline.py](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/core/rag_pipeline.py)
* Adjust `build_chunks_from_metadata` to map page chunks into LanceDB tables with correct `page` fields.

### Step 4: Update Citations Prompting & Formatter
We will update the backend RAG pipeline and prompts to generate the `[filename - Page X]` style citations.

#### [MODIFY] [backend/main.py](file:///home/drd8/Vinay/projects/cern-multimodel-rag-lancedb-migration/backend/main.py)
* Update `call_local_summary` context formatting and update the system prompt to enforce the supervisor's citation format.

---

## 5. Verification Plan

### Automated Tests
- Run `python core/docling_parser.py` on a sample document to verify extraction.
- Run `python core/semantic_chunker.py` to check that chunks do not bleed across page borders.

### Manual Verification
- Ingest a multi-page PDF through the Next.js UI, monitor real-time ingestion status, and query the local model (Qwen 35B) to check that it cites the source using the exact format: `[CERN_Yellow_Report.pdf - Page 5]`.
