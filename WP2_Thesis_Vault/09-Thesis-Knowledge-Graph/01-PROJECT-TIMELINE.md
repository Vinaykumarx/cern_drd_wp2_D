# WP2 Project Timeline

## 2026-02-04 to 2026-08-04 — Internship period

The confirmed internship period is six months, from 4 February to 4 August 2026.
The exact phase boundaries inside this period still need to be reconstructed from
calendar, commits, meeting notes, and deliverables.

## 2025-11-24 — Initial Mac prototype

The first concrete RAG project discussions describe an **Option A** architecture:
LayoutLMv3, BLIP2, PDF text extraction, custom hierarchical/text-only chunking,
SentenceTransformers embeddings, Qdrant Cloud, and Streamlit. The design was
single-PDF oriented and compatible with lightweight local experimentation. Docling
and MinIO were not part of the initial design.

Evidence: [[../07-Chat-History|Chat history]], [[../08-Source-Code|source snapshots]], and the architecture material in [[../04-Architecture|04-Architecture]].

## Late November 2025 — Prototype debugging and first migration pressure

Work exposed Docker import-path problems, Qdrant API incompatibilities, network
timeouts, slow model downloads, and local resource constraints. The project then
shifted toward LanceDB for a more controllable local-first vector store.

## Late 2025 to early 2026 — Multimodal features

The pipeline expanded with image saving, BLIP captions, figure-aware search,
image previews, hybrid text/caption similarity, multi-PDF ingestion, LLM summary
experiments, and filtering of misleading raster images such as thumbnails or
full-page previews.

## 2026-01-29 — Formal CERN/EPITA prototype framing

The project was framed as a multimodal RAG prototype for CERN scientific PDFs and
Yellow Reports. The target content included text, tables, figures, graphs,
equations, captions, multi-panel visuals, and vector plots. The documented
priority was still CPU-friendly, single-PDF development with figure-aware retrieval.

## February–May 2026 — Production-oriented architecture

The system moved toward FastAPI, Next.js, LanceDB, BGE embeddings, cross-encoder
reranking, document IDs, multi-document filtering, citation grounding, local/cloud
LLM fallback, verification, synthesis, telemetry, and knowledge-graph concepts.
The project changed from a demonstrator into a modular platform design.

## May 2026 — Large-document validation and limitations

An archived assessment records a test around 176 pages, 183 tables, 110 images,
and 249 chunks with fast search. The same history records limited visual captioning
(including a BLIP image cap), so the result demonstrates pipeline capability but
not perfect extraction of every visual element.

## 2026-06-15 to 2026-06-16 — Hardening and architecture lock

The repository was consolidated around persistent project state, validation,
control-center files, runtime safety, and a canonical pipeline. Important fixes
included LanceDB count desynchronization, blocking asynchronous behavior, and
large graph-memory usage. Docling became the intended primary extraction path.

## 2026 — Compute transition

The history records the need for stronger compute, an RTX 5090 incident, discussion
of CERN GPU resources, and compute request `RQF3798846` for the `drd8-llm` context.
This marks the transition from Mac-constrained experimentation toward GPU-assisted
VLM, OCR, batch extraction, and large-document processing.

## 2026-07-03 — CERN WP2 Materials Database LLM presentation

The CERN Indico programme records a presentation titled **WP2 Materials Database
LLM** with Nicola Pacifico and Vinay Kumar Jakanachary as speakers. This provides
official evidence connecting the software project to DRD8 WP2's materials-database
activity.

## Current state

Docling migration and extraction audit remain active. The repository still has
fallback extraction paths, while ColPali, improved hybrid chunking, graph
pagination, end-to-end testing, benchmarking, and several production hardening
items remain future or in-progress work.
