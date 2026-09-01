# Thesis Evidence Map

| Thesis section | Main argument | Evidence to consult |
|---|---|---|
| Introduction | Scientific knowledge is fragmented across complex reports | `02-Documentation/01-production-assessment.md`, CERN references |
| CERN/DRD8 context | Why the material and radiation-damage domain matters | `02-Documentation/04-my-role-and-status.md`, presentations, references |
| Initial state | Mac-constrained multimodal prototype | Chat history, `08-Source-Code`, early diagrams |
| Requirements | Text, tables, figures, graphs, equations, citations | architecture reports and prototype context |
| Architecture | Evolution from Qdrant/Streamlit to LanceDB/FastAPI/Next.js | `02-ARCHITECTURE-EVOLUTION`, architecture folder |
| Extraction | PDF parsing, OCR, tables, figures, captions, VLM recovery | source code, architectural audit, Docling audit |
| Chunking/retrieval | Metadata, BGE vectors, LanceDB, reranking | `semantic_chunker.py`, `vector_store_lance.py`, audit |
| Orchestration | Research, verification, synthesis, grounded answers | `rag_pipeline.py`, `swarm_orchestrator.py`, audit |
| Validation | Large-document test, startup validation, retrieval behavior | production assessment, logs, presentations |
| Critical analysis | Image caps, citation grouping, async/graph/storage risks | `control_center/BUGS.md`, audit, current-state notes |
| Personal contribution | Decisions, implementation, debugging, restructuring | source snapshots plus memory questions in `04-GAPS-AND-QUESTIONS` |
| Conclusion | Prototype matured into a production-oriented research platform | timeline, architecture evolution, gap register |

## EPITA realization template

For every major technical or methodological realization, answer:

1. What was the objective?
2. What alternatives existed?
3. What constraints came from CERN, the documents, or the Mac/GPU environment?
4. Which proposals were accepted or rejected, and why?
5. What difficulties occurred?
6. What was implemented and measured?
7. What was the impact, investment, and remaining limitation?
