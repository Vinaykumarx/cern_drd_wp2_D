# CERN DRD8 WP2 Internship Thesis - Working Index

**Author:** Vinay Kumar Jakanachary  
**Institution:** EPITA / CERN DRD8 collaboration  
**Working subject:** AI-assisted knowledge structuring for radiation-damage materials  
**Status:** First structure mapped from EPITA guidelines and the local WP2 archive  

This is a working index. The final title, dates, CERN organizational description,
confidentiality treatment, page allocation, and supervisor-approved wording must be
confirmed before submission.

## Preliminary pages

1. Cover page
   - Student name, specialization, promotion, internship dates, organization,
     subject, EPITA logo, CERN logo, and supervisor.
2. Supervisor approval/signature page
3. Table of contents
4. List of figures and tables
5. List of abbreviations and technical terms
6. Two-page internship summary

## 1. Introduction (maximum 10 pages)

### 1.1 Internship subject and final purpose

- State the approved subject precisely.
- Explain the objective: transform fragmented CERN radiation-material reports into
  a searchable, structured, multimodal knowledge layer.
- Define the engineering deliverable: a local-first RAG platform with extraction,
  indexing, retrieval, reranking, grounded answers, and citations.

### 1.2 Evolution of the initial subject

- Explain the evolution from MaxRAD/material database and semantic search toward a
  multimodal scientific RAG platform.
- Explain the transition from a prototype architecture to multi-document support,
  operational hardening, and Docling migration.
- Separate the original approved subject from later extensions.

### 1.3 CERN and DRD8 context

- CERN's research and engineering environment.
- DRD8 purpose and WP2 context.
- Radiation-damage materials and detector-construction knowledge.
- Relationship between legacy reports, MaxRAD, IMHOTEP, and the proposed assistant.

### 1.4 Maturity of the organization and teams

- Existing CERN material-data practices and sources.
- Existing databases and reports.
- Role of the internship supervisor and collaborating teams.
- What was already available before the internship and what was missing.

### 1.5 Starting knowledge and motivation

- EPITA knowledge applied: software engineering, AI/ML, databases, APIs,
  visualization, and systems design.
- Previous experience relevant to RAG, data processing, XR, and visualization.
- Motivation for solving scientific-document accessibility problems.

### 1.6 Value and positioning of the internship for CERN

- Why manual PDF search is insufficient.
- How structured retrieval can preserve institutional knowledge.
- Expected value for material selection, radiation-damage analysis, and future
  detector work.
- Boundaries: this is a research infrastructure prototype, not yet CERN-wide
  production infrastructure.

### 1.7 Precise working context

- Mac/local development environment and available hardware.
- CERN systems, documents, APIs, and supervisor access.
- Software stack and local/cloud model constraints.
- GPU interruption and later GPU-resource request.
- Communication, review, and validation conditions.

## 2. Organizational aspects (maximum 25 pages)

### 2.1 Breakdown of the internship

Describe phases, deliverables, dependencies, and parallel work. Include a Gantt or
activity diagram.

Suggested phases:

1. Understand MaxRAD, material data, CERN reports, and project requirements.
2. Establish the initial RAG prototype and PDF-processing workflow.
3. Build multimodal extraction for text, tables, figures, graphs, and OCR pages.
4. Build the FastAPI, frontend, LanceDB, and citation workflow.
5. Add multi-document registration, document IDs, remote CDS import, and filtering.
6. Validate with CERN reports and material-property queries.
7. Audit production risks and implement stability fixes.
8. Consolidate the repository and persistent project-state system.
9. Begin Docling/page-aware extraction migration.
10. Prepare thesis, presentation, and defense evidence.

### 2.2 Schedule adherence and critique

- Compare planned work with actual dates and deliverables.
- Explain scope expansion and reprioritization.
- Explain why some roadmap items remain unfinished.
- Critique whether the work should have prioritized retrieval evaluation earlier.

### 2.3 Internal controls and review points

- Supervisor discussions and technical reviews.
- Architecture audits.
- Startup validation and health checks.
- Multi-document test workflow.
- Repository control-center updates.
- Presentation reviews and source-verification checks.

### 2.4 Management of technical and organizational crises

- GPU/infrastructure interruption.
- Limited local hardware and memory constraints.
- OCR and scientific-layout extraction failures.
- OpenRouter/provider availability and local fallback decisions.
- Retrieval confusion across similar documents.
- Scope and architecture complexity management.

## 3. Scientific, technical, and methodological aspects

For every major realization, explicitly answer: objective, alternatives, constraints,
chosen proposal, difficulties, result/status, impact, and personal contribution.

### 3.1 Problem definition and requirements

- Scientific PDFs contain text, tables, graphs, figures, formulas, and OCR noise.
- Researchers need material-specific answers with traceable citations.
- Requirements: local-first operation, document provenance, page metadata,
  multimodal extraction, multi-document search, and grounded generation.

### 3.2 State of the art and alternatives

- Keyword search and manual PDF reading.
- Structured databases such as MaxRAD and IMHOTEP.
- Traditional flat RAG.
- Chroma versus LanceDB.
- PyMuPDF/pymupdf4llm, Marker, and Docling.
- BLIP/Qwen2-VL versus direct visual retrieval such as ColPali.
- Local Ollama versus cloud providers.
- Deterministic chunking versus LLM-based chunking.

### 3.3 Scientific document ingestion

- PDF registration and document IDs.
- Text extraction and sparse-page recovery.
- OCR fallback.
- Table extraction and CSV outputs.
- Image and graph extraction.
- Figure captioning.
- Metadata aggregation and output directory structure.
- Current Docling primary path and remaining fallback/migration work.

### 3.4 Chunking and metadata design

- Header-based deterministic Markdown chunking.
- Page and document provenance.
- Text, table, and figure virtual chunks.
- Topic, summary, keywords, and quality score.
- Failure modes: missing headers, oversized sections, weak keywords, and topic
  over-generalization.

### 3.5 Vector storage and retrieval

- LanceDB schema and 768-dimensional BGE vectors.
- ANN candidate retrieval.
- Cross-encoder reranking.
- Text/figure/table result categories.
- Document-specific filtering.
- Citation metadata and source preview.

### 3.6 LLM generation and scientific orchestration

- Research, verification, and synthesis stages.
- Reviewer stage for citation and hallucination control.
- OpenRouter/cloud and Ollama/local fallback behavior.
- Difference between structured orchestration and fully autonomous agents.

### 3.7 User interface and observability

- Next.js dashboard.
- Chat and PDF upload.
- Citation overlays and source verification.
- Telemetry hub.
- Neuro-Map knowledge graph.
- Graph pagination and browser-memory fix.

### 3.8 Validation and results

- Startup validation suite.
- CERN Yellow Report extraction test.
- Material 557 / CERN 89-12 query example.
- Multi-document ingestion and filtering test.
- Measured extraction, chunk, embedding, and search behavior.
- What was validated manually versus what still lacks a benchmark.

### 3.9 Engineering decisions and personal contribution

For each major decision, document alternatives, constraints, decision rationale,
implementation, and your contribution:

- LanceDB selection.
- BGE and cross-encoder selection.
- Deterministic chunker migration.
- Multi-document `doc_id` design.
- Local/cloud LLM fallback.
- Background ingestion and async wrappers.
- Knowledge-graph limits.
- Repository organization and persistent state.
- Docling migration direction.

## 4. First assessment (maximum 10 pages)

### 4.1 Value and contribution to CERN

- What problem is solved today.
- What components are demonstrably operational.
- Reusability for CERN document collections.
- Contribution to future material-data access and analysis.
- Remaining work before production deployment.

### 4.2 Personal technical and organizational benefit

- Scientific-document understanding.
- RAG and information-retrieval engineering.
- Python/FastAPI/Next.js systems integration.
- Vector databases and model routing.
- Testing, observability, documentation, and project organization.
- Communication and presentation of complex engineering work.

### 4.3 Critical conclusion and retrospective

- What worked well.
- What should have been done differently.
- Where architecture became more complex than retrieval quality justified.
- What the GPU interruption taught about infrastructure assumptions.
- Which improvements are realistic future work.
- Relevance of EPITA training to the internship.

## 5. Bibliography, glossary, and index

### 5.1 Bibliography

Every source must state how it contributed to a technical or scientific decision.
Include CERN reports, RAG/document-understanding references, model documentation,
and software documentation.

### 5.2 Glossary

Define CERN, DRD8, WP2, MaxRAD, IMHOTEP, RAG, OCR, VLM, ANN, embedding,
reranking, LanceDB, CDS, Docling, BGE, BLIP, Qwen2-VL, Ollama, OpenRouter,
ColPali, and any domain-specific materials terminology.

### 5.3 Index

Index important technical concepts, documents, materials, models, and system
components.

## 6. Separate annex document

The annexes must be physically separate from the main report and referenced from it.
Do not include raw source code as a catalogue.

Suggested annexes:

- A. Approved subject and scope evolution
- B. Internship organization and Gantt chart
- C. System architecture diagrams
- D. Ingestion and output schemas
- E. LanceDB schema and retrieval flow
- F. CERN Yellow Report / CERN 89-12 validation examples
- G. Selected UI and telemetry screenshots
- H. Test and validation results
- I. Hardware and compute profile
- J. Selected project-management evidence
- K. Additional technical documentation

## Separate English abstract (maximum 5 pages)

- English cover page with the same information as the main report.
- Company and team presentation.
- Initial assignment and required skills.
- Existing hardware, software, and project state.
- Weekly timeline with a chart.
- General appreciation of the work and working conditions.
- Engineering skills acquired.
- Critical conclusion including positive and negative aspects.

## Evidence map

| Thesis need | Main local evidence |
|---|---|
| Formal structure and grading | `02-Documentation/20260116-DOC-ConsignesStageFinDEtudesPromo2026 2.pdf` |
| Defense criteria | `02-Documentation/20260116-MOD-PVSoutenancePromo2026.pdf` |
| Supervisor evaluation | `02-Documentation/20260116-DOC-EvaluationDesCompetencesStagePromo2026.pdf` |
| MSc synthesis | `02-Documentation/20260116-DOC-FicheDeSynthèseMscPromo2026.doc` |
| Technical audit | `thesis-preparation/documentation/03-architectural-audit.md` |
| Production assessment | `thesis-preparation/documentation/01-production-assessment.md` |
| Project progress | `thesis-preparation/documentation/22-project-report.md` |
| Multi-document implementation | `thesis-preparation/project-tracking/14-MULTIDOC_IMPLEMENTATION.md` |
| Current repository truth | `control_center/PROJECT_STATE.md`, `control_center/TASKS.json`, `control_center/BUGS.md` |
| Current implementation | `backend/`, `core/`, `extraction/`, `frontend/`, `tests/` |
| Presentation evidence | `05-Presentations/` |
| Architecture visuals | `04-Architecture/` |
| Project history | `thesis-preparation/chat-history/`, `thesis-preparation/conversation-logs/` |
