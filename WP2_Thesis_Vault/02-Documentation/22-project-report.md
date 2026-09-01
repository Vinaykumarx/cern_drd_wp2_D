# Progress Report: Multimodal RAG System for Scientific PDFs
**CERN DRD8 — WP2 | May 2026**

---

## 1. Project Overview

This project develops a Retrieval-Augmented Generation (RAG) system designed to extract structured information from CERN scientific PDFs and answer user queries through a web-based interface. It is part of the CERN DRD8 WP2 work package. The system ingests PDF documents, extracts text and structural elements, stores vector embeddings in a local database, and retrieves relevant passages to ground LLM-generated responses with source citations.

## 2. Current Implementation Status

The system is operational as a stable text-focused prototype. The architecture consists of three layers: a **Next.js frontend** providing a dashboard and chat interface, a **FastAPI backend** handling API routing and LLM orchestration, and a **LanceDB vector store** for embedding storage and retrieval.

The extraction pipeline (`extract_with_docid.py`) processes PDFs through five stages: Markdown text extraction via `pymupdf4llm`, table extraction via `pdfplumber`, image extraction via PyMuPDF, graph detection via OpenCV, and image captioning via BLIP. Each document produces a `metadata.json` file aggregating all extracted artefacts. A sparse-page recovery mechanism detects pages with insufficient text output and re-extracts them using plain-text fallback or OCR.

Retrieval uses `BAAI/bge-base-en-v1.5` for embedding and `cross-encoder/ms-marco-MiniLM-L-6-v2` for reranking. The backend supports both cloud LLMs (via OpenRouter/Groq) and a local Ollama fallback. A two-stage answer generation pipeline drafts an initial response, then passes it through a reviewer stage that checks for hallucinated data or uncited sources before returning the final answer. The frontend renders Markdown responses with `[CX]` citation tags mapped to source documents.

## 3. Key Changes and Improvements

The chunking strategy was migrated from an LLM-based "agentic" approach to a **deterministic Markdown header-based splitter** (`SemanticChunker`). This eliminated the dependency on expensive LLM calls during ingestion, improved reproducibility, and reduced failure rates during bulk processing. Each chunk is annotated with a title, topic label, naive summary, and keyword set derived heuristically from the section content.

The LLM backend was decoupled from a single local model (Ollama/Gemma) to support **configurable cloud providers** (OpenRouter, Groq), with automatic local fallback if the cloud call fails. A **self-review stage** was added to the answer generation pipeline to reduce hallucination of experimental parameters or PDF sources not present in the retrieved context.

The vector store schema was extended to include semantic metadata fields (`topic`, `summary`, `keywords`, `quality_score`) alongside the original text and page-level fields. PDF upload was added as an API endpoint, enabling users to drop any PDF into the system and query it after background ingestion completes.

## 4. Current Challenges

**Retrieval precision** remains the primary limitation. The current chunking heuristic assigns coarse topic labels (e.g., "General" vs. "Radiation/Safety") based on simple keyword presence in headers, which does not capture the semantic nuance of physics subdomains. When queries fall outside these narrow keyword matches, the retrieved context can be irrelevant — for example, returning conference logistics instead of safety protocol data.

**Chunk quality** is inconsistent across document types. The header-based splitter works well for structured reports but produces oversized or fragmented chunks for documents with irregular formatting. The naive summary (first sentence) and keyword extraction (frequency-based) provide limited semantic value for embedding enrichment.

**Ingestion robustness** needs improvement. The sparse-page recovery path relies on available OCR libraries and does not always produce clean text for scanned or image-heavy pages. The BLIP captioning step, while functional, generates generic captions that add limited retrieval value for domain-specific scientific figures.

## 5. Next Steps

Near-term work will focus on **improving chunking quality** by introducing overlap between header-based sections and filtering out boilerplate content (headers, footers, page numbers) before chunking. **Topic classification** will be enhanced — either by expanding the keyword-matching vocabulary for CERN-specific domains or by using a lightweight classifier to assign more granular labels.

**Metadata-aware retrieval** will be explored: weighting search results by quality score and topic relevance rather than relying solely on vector distance and reranking. The frontend citation system will be connected to a PDF viewer that deep-links to the specific page of each cited source. Finally, the ingestion pipeline will be hardened with better error handling and progress reporting to support reliable batch processing of large document collections.

---
*Prepared by: V. Kumar — CERN DRD8 WP2*
