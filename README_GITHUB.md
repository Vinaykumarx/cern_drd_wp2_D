# CERN DRD8 WP2 Multimodal RAG Platform

This repository contains the software, thesis evidence, architecture records, and selected technical source documents for a multimodal knowledge-retrieval platform developed in the CERN DRD8 WP2 context.

## Project context

DRD8 Work Package 2 is concerned with **Low-mass Mechanics and Thermal Management**. The project explores how scientific PDFs and related technical documents can be converted into searchable, traceable evidence using document extraction, multimodal representations, vector retrieval, reranking, and grounded generation.

## Repository map

| Path | Purpose |
| --- | --- |
| `WP2_Thesis_Vault/` | Canonical Obsidian thesis vault, evidence map, timeline, gaps, and editable manuscript |
| `backend/` | FastAPI services and retrieval-facing backend code |
| `frontend/` | Next.js user interface |
| `core/` | Shared retrieval, orchestration, and project logic |
| `extraction/` | PDF/document extraction components and migration work |
| `control_center/` | Project state, task tracking, bugs, and architecture controls |
| `knowledge_system/` | Persistent project memory and session logs |
| `docs/wp2-source-materials/` | Selected WP2 and materials-database presentations |
| `docs/project-history/` | Project evolution, compute, architecture, and deployment records |
| `tests/` | Automated and validation tests |

## Project evolution

The work evolved from a lightweight Mac-compatible prototype into a more modular, production-oriented platform. The main transitions were:

1. Local PDF extraction and lightweight-model prototyping.
2. Multimodal processing of text, tables, figures, and scanned pages.
3. Migration toward LanceDB, document identity, metadata, and source previews.
4. FastAPI and Next.js modularization with embeddings and reranking.
5. Runtime validation, architecture auditing, telemetry, and compute planning.
6. Evaluation of Docling as the primary document-understanding path.

## Thesis manuscript

The current editable manuscript is:

`WP2_Thesis_Vault/10-Thesis-Documents/EPITA_WP2_Thesis_Manuscript.docx`

It follows the EPITA internship-report structure and contains populated chapters, tables, architecture diagrams, project screens, PDF extraction evidence, and explicit completion fields for facts that still require supervisor confirmation or measured benchmarks.

## What is intentionally excluded

The public repository does not include personal CVs, signed internship agreements, immigration documents, receipts, the complete ChatGPT export, local credentials, model caches, virtual environments, databases, generated output, or the full CERNBox archive. Those remain in their original protected storage.

## Reproducibility note

The repository is a research and engineering record. Results should be interpreted together with the limitations and open issues recorded in `control_center/BUGS.md` and the thesis evidence map. Large source archives and runtime datasets are intentionally managed outside ordinary Git history.
