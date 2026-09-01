# 🏗️ Architecture Review & Roadmap

This document serves as a "lock-in" of the current state of the CERN Multimodal RAG (Agent Zero) project, identifying what works well, exposing underlying flaws, and outlining a strategic roadmap for future implementations.

## 🟢 1. Current Verified State (What is Working)

The project successfully orchestrates a complex, multimodal Retrieval-Augmented Generation pipeline.

### Core Strengths & "Skills" Demonstrated:
*   **Dual-Interface System**: Both Next.js (Premium UI) and Streamlit (Rapid Prototype) can interact with the FastAPI backend successfully.
*   **Multi-Document RAG Implementation**: The system correctly indexes, stores, and segregates data using `doc_id` tracking in LanceDB.
*   **Failover Intelligence**: Implementation of automatic LLM fallback (from OpenRouter/Groq to Local Ollama `gemma4`) ensures the system remains operational during API outages or credit exhaustion.
*   **Deterministic Chunking**: The introduction of `SemanticChunker` (Markdown header-based splitting) significantly reduces the bottleneck of LLM-based chunking, increasing ingestion speed.
*   **Agentic Retrieval**: The RAG pipeline employs a pre-search discovery phase, scanning registered documents and falling back to the CERN CDS API when local context is insufficient.

---

## 🔴 2. Identified Flaws & Architectural Bottlenecks

While functional, several architectural decisions introduce friction or limit scalability.

### Extraction & Chunking Flaws
*   **Naive Chunking Heuristics**: The `SemanticChunker` uses simple Markdown regex to split chunks. If a PDF converts poorly to Markdown (missing headers), the chunker will ingest massive, unbroken pages, destroying retrieval accuracy. 
*   **Vision Extraction Bottleneck**: `BLIP` captioning is currently hardcoded to process a maximum of 3 images due to performance constraints. Highly visual scientific papers lose critical data.
*   **Metadata Hallucination**: The `SemanticChunker._create_chunk()` method generates "naive keywords" and sets topics to "General" or "Radiation/Safety" based on hardcoded strings. This breaks the intelligence of the graph mapping.

### Data Flow & Database Flaws
*   **LanceDB Synchronization**: The backend `dashboard_status` counts vectors directly from LanceDB, but the `knowledge_graph` endpoint tries to load *all* vectors (`limit(200)` band-aid) to build nodes. As the database grows, the Next.js `ForceGraph2D` will freeze the browser.
*   **Redundant Asset Storage**: Extracting images and tables to physical files `outputs/{doc_id}/` while also storing representations in LanceDB risks state desynchronization if a document is deleted.

### Infrastructure Flaws
*   **Multiple Frontends**: Maintaining both Streamlit and Next.js creates technical debt. Features implemented in one (e.g., Graph visualization) are missing in the other.
*   **Sync vs Async Mismatch**: The FastAPI backend uses async endpoints, but tools like the `SemanticChunker` and underlying vector searches run synchronously, blocking the event loop under heavy load.

---

## 🚀 3. Strategic Roadmap & Recommendations

To increase efficiency, simplify the codebase, and scale, consider the following implementation strategies.

### A. Recommended Tool Replacements
1.  **PDF Parsing**: Replace `pymupdf4llm` + `pdfplumber` with **Docling** or **Unstructured.io**. These specialized libraries handle tables, multi-column layouts, and mathematical formulas much more reliably for scientific papers.
2.  **Vision Retrieval**: Instead of extracting images and captioning them with BLIP (slow and error-prone), investigate **ColPali**. It embeds visual patches of the PDF directly into vector space, allowing you to search visually without OCR/Captioning.
3.  **UI Consolidation**: Deprecate the Streamlit app entirely. Move the PDF upload drag-and-drop strictly into the Next.js frontend to maintain a single source of truth for the UX.

### B. Architecture Refactoring
1.  **Asynchronous LanceDB**: Ensure all LanceDB queries (`rag.table.search()`) are wrapped in `asyncio.to_thread` to prevent the FastAPI server from locking up when multiple users query the database.
2.  **Hybrid Chunking Strategy**: 
    *   *Step 1*: Use deterministic Markdown splitting (fast).
    *   *Step 2*: Run a lightweight local model (like `nomic-embed-text` or a small `phi3`) in the background specifically to generate high-quality `topic` and `keywords` metadata for the chunk, rather than naive regex.
3.  **Graph Pagination**: The `get_knowledge_graph` endpoint must be refactored to query only nodes related to the *current user query* or a specific `doc_id`, rather than dumping random vectors to the frontend.

### C. Prompt & Intelligence Tuning
*   Update the `call_reviewer_stage` prompt. Currently, it acts as a strict filter against hallucinations. You can enhance it to act as a **Router**: If it detects missing context, it shouldn't just apologize—it should trigger a background task to query the CERN CDS API, download the missing paper, and alert the user that "New context is being ingested."
