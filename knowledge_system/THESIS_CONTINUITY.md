# Thesis Continuity and Reuse Register

This file is the project-level memory for all future thesis-writing sessions and orchestrators. Read it together with `latest_state.md`, `session_index.json`, the evidence map, and the claims register before changing the manuscript.

## Non-negotiable project framing

- The Mac was the lightweight prototype environment, not the intended deployment target.
- “Local-first” means self-hosted execution under project control: local/owned GPU or server resources, without a defining dependency on third-party cloud LLM or API services.
- The production target may be hosted on a server and accessed remotely by multiple users over the internet.
- The project evolved from a lightweight prototype to a production-oriented architecture after stronger compute became available or was requested.
- The original GPU failure led to a CERN compute-access phase involving Open Lab/ML Flow and related infrastructure such as Kubeflow.
- Earlier records mention an RTX 5090; the user also mentioned “1580”. The exact identifier remains unverified and must not be normalized without confirmation.
- Separate demonstrated, implemented, migrated, proposed, blocked, and untested work. Never present a roadmap item as a completed result.

## Confirmed thesis metadata

- Student: Vinay Kumar Jakanachary
- EPITA UID: 29900
- Programme: Master of Science in Artificial Intelligence Systems (MSc AIS)
- Internship host/context: CERN · EP-URD · DRD8 Collaboration · WP2 Materials Database
- Internship dates: 4 February 2026 – 4 August 2026
- CERN supervisor/project supervisor: Nicola Pacifico (use this working label unless the agreement requires another title)
- EPITA academic supervisor: Alaa Bakhti
- Working title: “Development of a Multimodal Retrieval-Augmented Generation Platform for the CERN DRD8 WP2 Materials Database”
- Official WP2 title: Low-mass Mechanics and Thermal Management

## Thesis writing rules

1. Define the chapter, subtopics, source files, evidence status, and visual plan before editing pages.
2. Use each source once for its main purpose; cross-reference rather than repeat the same narrative.
3. Label claims as implemented, demonstrated, proposed, migrated, blocked, or requiring validation.
4. Prefer evidence from code, project reports, presentations, screenshots, logs, and architecture files. Do not invent measurements, dates, roles, or deployment results.
5. Use one strong visual per concept. Put architecture diagrams in the technical-design chapter, workflow/screens in use cases or results, and detailed visual evidence in annexes when necessary.
6. Keep a page-density check: add relevant explanation, tables, or visuals where evidence supports it, but do not stretch pages with decorative or unsupported material.
7. After each DOCX edit, render every page, visually inspect the affected pages and pagination boundaries, and record the result here and in the session index.

## Visual assignment register

- Use-case workflow: `04-Architecture/images/result-with-context.png`
- Document registration/processing: `04-Architecture/images/document-processing-example.png`
- OCR recovery: `04-Architecture/images/ocr-correction-demo.png`
- Source/page verification: `04-Architecture/images/source-verification.png`
- Main technical data flow: `04-Architecture/images/end-to-end-multimodal.png`
- Prototype architecture: `04-Architecture/images/architecture-diagram.png`
- LanceDB schema: `04-Architecture/images/mermaid-lancedb_schema.png` (redraw or enlarge if unreadable)
- Query interface: `04-Architecture/images/query-interface.png`
- Runtime/telemetry: `04-Architecture/images/telemetry-dashboard.png`
- PDF comparison: `04-Architecture/images/comparison-1.jpeg` and `comparison-2.jpeg`
- Decorative illustration `end-to-end-data-flow.png` is not a primary thesis architecture figure because it is visually attractive but contains no readable technical labels.

## Chapter 3 evidence plan

- 3.1 Requirements and acceptance criteria: page 28, completed.
- 3.2 Use cases and researcher workflow: pages 29–30; use `result-with-context.png` and `document-processing-example.png` only where they directly support the workflow.
- 3.3–3.6: alternatives, prototype, hardware boundary, and production architecture; use `architecture-diagram.png` and `end-to-end-multimodal.png` without duplicating the same explanation.
- 3.7–3.10: extraction, multimodality, provenance, chunking, embeddings, LanceDB, retrieval, reranking, and agents; use the schema, OCR, source-verification, and pipeline visuals.
- 3.11–3.12: backend, frontend, and multi-document support; use interface, processing, telemetry, PDF-viewer, and comparison screenshots.

## Open gaps to preserve until evidence is supplied

- Exact contractual title and official wording of the internship subject.
- Exact GPU model, failure date, replacement/access dates, and compute topology.
- Exact dates and outcomes for CERN Open Lab/ML Flow/Kubeflow access.
- Which components were fully implemented, migrated, demonstrated, blocked, or only proposed.
- Final Docling migration status and fallback behavior.
- Dataset size, indexed document count, vector count, benchmark queries, retrieval metrics, latency, and resource measurements.
- Validated researcher personas, use cases, acceptance thresholds, domain-expert feedback, and usability results.
- Final deployment, authentication, multi-user isolation, and confidentiality procedure.
- Formal supervisor roles and approval wording if the Convention de stage differs from the working map.

## Canonical manuscript

`WP2_Thesis_Vault/10-Thesis-Documents/EPITA_WP2_Thesis_Manuscript.docx`

