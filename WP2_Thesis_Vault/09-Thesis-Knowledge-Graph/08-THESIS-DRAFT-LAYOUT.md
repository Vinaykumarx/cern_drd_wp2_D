# EPITA Internship Thesis — Draft Layout

**Working title:** Design and Development of a Local-First Multimodal Retrieval-Augmented Generation Platform for the CERN DRD8 WP2 Materials Database

**Author:** Vinay Kumar Jakanachary  
**Host:** CERN / DRD8 Work Package 2  
**Official WP2 context:** Low-mass Mechanics and Thermal Management  
**Internship:** 4 February 2026 – 4 August 2026  
**Status:** Working page plan; not final pagination

## Recommended length

EPITA sets maximum lengths for some sections, but does not prescribe one total
page count. A strong target is:

| Component | Recommended pages | EPITA constraint |
|---|---:|---|
| Main report, including front matter | 69 | Introduction ≤10; organizational chapter ≤25; first assessment ≤10 |
| Separate annex volume | 20–40 | Separate from report; only meaningful, referenced annexes |
| English abstract | 4–5 | Maximum 5 pages; separate PDF |

The layout below deliberately stays below the stated chapter limits. Figures and
tables should be counted inside the relevant chapter pages, not added without
checking the total.

## Page-by-page index

### Preliminary pages

| Page | Section | Contents and current evidence |
|---:|---|---|
| 1 | Cover | Final title, name, specialization, promotion, CERN, DRD8 WP2, dates, supervisor, logos. **[TO FILL: approved title, official roles, signatures]** |
| 2 | Approval | Supervisor/company validation and signature. **[TO FILL]** |
| 3 | Table of contents | Generated only after headings and pagination are stable. |
| 4 | Figures and tables | Final list of architecture diagrams, pipeline figures, benchmarks, and result tables. **[TO FILL]** |
| 5 | Abbreviations | CERN, DRD8, WP2, RAG, VLM, OCR, PDF, ANN, BGE, API, LLM, CDS, MaxRAD, IMHOTEP, etc. |
| 6 | Internship summary 1/2 | CERN/DRD8 context, problem, assignment, and objective. Use [[07-CONFIRMED-INTERNSHIP-FACTS]]. |
| 7 | Internship summary 2/2 | Approach, deliverables, current results, limitations, and value. **[TO FILL: final metrics]** |

### Chapter 1 — Introduction (pages 8–15; 8 pages, maximum 10)

| Page | Section | Contents and current evidence |
|---:|---|---|
| 8 | 1.1 Context | CERN, DRD8, WP2 low-mass mechanics and thermal management; materials qualification and database context. |
| 9 | 1.2 Scientific problem | Scientific knowledge is distributed across complex PDFs containing text, tables, figures, graphs, equations, and captions. |
| 10 | 1.3 Internship subject | Approved subject and final working title. **[TO FILL: exact agreement wording]** |
| 11 | 1.4 Initial versus final scope | Mac prototype, lightweight models, single-PDF RAG, then multimodal and multi-document expansion. |
| 12 | 1.5 CERN/project positioning | WP2 materials database activity, MaxRAD relationship, intended users and use cases. **[TO FILL: exact organizational relationship]** |
| 13 | 1.6 Starting knowledge and motivation | EPITA skills, previous experience, motivation, learning objectives. **[TO FILL: personal account]** |
| 14 | 1.7 Work environment | Mac constraints, local models, later compute/GPU direction, available documentation and collaborators. |
| 15 | 1.8 Introduction conclusion | Research/engineering question, objectives, deliverables, thesis structure. |

### Chapter 2 — Organizational aspects (pages 16–27; 12 pages, maximum 25)

| Page | Section | Contents and current evidence |
|---:|---|---|
| 16 | 2.1 Organization | CERN, DRD8, WP2, project/team structure. **[TO FILL: official team chart]** |
| 17 | 2.2 Roles | Vinay, Nicola, Archana, Sushrut, Diego. Use provisional labels until formally verified. |
| 18 | 2.3 Development plan | Initial objectives, expected deliverables, dependencies, and priorities. **[TO FILL]** |
| 19 | 2.4 Timeline/Gantt | 4 Feb–4 Aug 2026 with prototype, migration, multimodal, production, compute, and thesis phases. **[TO FILL: exact dates]** |
| 20 | 2.5 Phase 1 | Requirements, CERN/WP2 understanding, initial Mac prototype. |
| 21 | 2.6 Phase 2 | Qdrant, Docker, model-download, and local-resource debugging. |
| 22 | 2.7 Phase 3 | LanceDB migration, schema corrections, multimodal extraction. |
| 23 | 2.8 Phase 4 | FastAPI, Next.js, BGE, reranking, citations, multi-document support. |
| 24 | 2.9 Phase 5 | Production audit, validation, control-center hardening, compute transition. |
| 25 | 2.10 Phase 6 | Docling audit/migration and remaining roadmap. |
| 26 | 2.11 Quality and communication | Meetings, reviews, version control, tests, documentation, confidentiality. **[TO FILL]** |
| 27 | 2.12 Organizational assessment | Planned versus actual schedule, scope changes, crises, adaptation, and lessons. |

### Chapter 3 — Scientific, technical, and methodological work (pages 28–55; 28 pages)

| Page | Section | Contents and current evidence |
|---:|---|---|
| 28 | 3.1 Requirements | Functional and non-functional requirements: multimodality, provenance, local-first operation, multi-document search, citations. |
| 29 | 3.2 Use cases | Materials-data search, scientific question answering, source verification, and document exploration. **[TO FILL: validated user scenarios]** |
| 30 | 3.3 Alternatives | Manual search, keyword search, text-only RAG, multimodal RAG, database-only approaches. |
| 31 | 3.4 Initial architecture | LayoutLMv3, BLIP2, text extraction, custom chunks, SentenceTransformers, Qdrant, Streamlit. |
| 32 | 3.5 Mac constraints | CPU-first development, memory limits, lightweight models, slow downloads, local reproducibility. |
| 33 | 3.6 Qdrant and Docker difficulties | API changes, network timeouts, import paths, and reasons for reconsidering the design. |
| 34 | 3.7 LanceDB decision | Alternatives, local-first constraints, schema control, migration rationale, PyArrow issues. |
| 35 | 3.8 Extraction pipeline | PyMuPDF/pymupdf4llm, pdfplumber, Camelot, OCR, OpenCV, BLIP, VLM recovery. |
| 36 | 3.9 Figures and graphs | Image extraction, captions, filtering thumbnails/full-page rasters, multi-panel and graph limitations. |
| 37 | 3.10 Tables and equations | Table extraction, CSV outputs, equation/scanned-page challenges. **[TO FILL: examples and accuracy]** |
| 38 | 3.11 Docling migration | Why Docling became primary, page-aware grouping, native tables, metadata preservation, fallback reduction. |
| 39 | 3.12 Document identity | `doc_id`, page metadata, provenance, output directories, source-to-answer traceability. |
| 40 | 3.13 Chunking | Header-based chunks, semantic enrichment, virtual table/figure chunks, chunk limitations. |
| 41 | 3.14 Embeddings | SentenceTransformers prototype, BGE 768-dimensional vectors, model/resource rationale. |
| 42 | 3.15 LanceDB schema | Vector and metadata fields, storage model, table operations, persistence. |
| 43 | 3.16 Retrieval | Dense query embedding, ANN candidates, document filtering, result categories. |
| 44 | 3.17 Reranking | Cross-encoder selection, candidate expansion, relevance improvement. **[TO FILL: measured comparison]** |
| 45 | 3.18 Agent orchestration | Research, verification, synthesis, reviewer concepts; separate implemented behavior from proposals. |
| 46 | 3.19 Grounded answers | Citation format, page/source references, confidence and verification workflow. |
| 47 | 3.20 Backend | FastAPI routes, ingestion, query handling, async safety, document manager. |
| 48 | 3.21 Frontend | Streamlit prototype and Next.js evolution, upload/search/source-preview workflow. |
| 49 | 3.22 Multi-document support | Registry, document filtering, extraction wrapper, enhanced RAG pipeline. |
| 50 | 3.23 Compute transition | Mac-to-GPU motivation, CERN resource request, VLM/OCR/batch-processing needs. |
| 51 | 3.24 Validation architecture | Startup validation, bootstrap enforcement, control center, persistent state. |
| 52 | 3.25 Large-document test | Around 176 pages, 183 tables, 110 images, 249 chunks, fast search. **[TO FILL: exact source and reproducibility]** |
| 53 | 3.26 Error analysis | BLIP image cap, graph memory, async blocking, count desynchronization, weak keywords, redundant assets. |
| 54 | 3.27 Technical decision synthesis | Objective/alternatives/constraints/decision/difficulty/result/impact for each major realization. |
| 55 | 3.28 Personal contribution | Code, architecture, debugging, experiments, presentations, documentation. **[TO FILL: your exact contribution]** |

### Chapter 4 — First assessment (pages 56–63; 8 pages, maximum 10)

| Page | Section | Contents and current evidence |
|---:|---|---|
| 56 | 4.1 State of the art | Position against keyword search, text RAG, multimodal RAG, Docling, VLM, and visual retrieval alternatives. |
| 57 | 4.2 Contribution to CERN | Better access to materials and technical knowledge; local-first research infrastructure. |
| 58 | 4.3 Achieved results | Implemented components, tested workflows, architecture and presentation evidence. |
| 59 | 4.4 Quantitative assessment | Ingestion, extraction, retrieval, memory, latency, and storage measurements. **[TO FILL: benchmark table]** |
| 60 | 4.5 Limitations | Incomplete visual coverage, table normalization, citation grouping, fallbacks, scalability, and benchmark gaps. |
| 61 | 4.6 Remaining work | Docling completion, ColPali, hybrid chunking, graph pagination, E2E tests, benchmarking, deployment. |
| 62 | 4.7 Personal assessment | Technical, scientific, organizational, and professional learning. **[TO FILL]** |
| 63 | 4.8 Critical conclusion | What was successful, what was not, and the recommended next engineering step. |

### Closing pages

| Page | Section | Contents |
|---:|---|---|
| 64 | General conclusion 1/2 | Answer the thesis question, summarize the evolution and contribution. |
| 65 | General conclusion 2/2 | Future work, transferability, personal perspective, and final critical statement. |
| 66 | Bibliography | CERN/DRD8 sources, scientific RAG literature, model and library documentation. |
| 67 | Glossary | RAG, VLM, OCR, ANN, embedding, reranking, provenance, multimodal extraction, etc. |
| 68 | Index | Technical terms, figures, tables, documents, and major concepts. |
| 69 | Final checklist | Supervisor approval, page limits, links to annexes, spelling, confidentiality, and submission format. Remove this page from the final report if unnecessary. |

## Separate annex volume

The annexes should not become a code catalogue. Each must be referenced from the
main report and briefly justified.

1. Detailed Gantt/activity diagram
2. CERN/DRD8/WP2 organizational context
3. Initial and final architecture diagrams
4. Extraction pipeline and output schema
5. LanceDB schema and metadata example
6. Chunking examples
7. Figure, graph, OCR, table, and equation examples
8. Retrieval and reranking examples
9. Citation verification examples
10. Benchmark methodology and raw results
11. Error analysis and failed cases
12. Selected UI screenshots
13. Deployment and hardware notes
14. Supervisor-approved technical documents where permitted

## Empty sections to fill first

- Exact approved title and official role names
- Original assignment and scope-change explanation
- Detailed phase dates and Gantt chart
- Team, meeting, review, and quality procedures
- Personal contribution by module
- Reproducible benchmark results
- User/test queries and ground truth
- Company value and personal learning assessment
- Abstract, bibliography, glossary, annex references, and defense script

## Drafting rule

Every technical realization must use the EPITA pattern: objective, alternatives,
company constraints, accepted/rejected proposals, difficulties, results/status,
impact, and investment. Claims about “production” or “complete extraction” must
be qualified unless supported by a reproducible measurement.
