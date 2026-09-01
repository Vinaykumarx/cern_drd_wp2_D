# Claims Register

## Documented and safe to use, subject to citation

- The initial architecture used lightweight multimodal components, custom
  chunking, SentenceTransformers, Qdrant, and Streamlit.
- The project later migrated toward LanceDB and a modular FastAPI/Next.js system.
- BGE embeddings and cross-encoder reranking are documented in the current state.
- The project includes multimodal extraction goals for text, tables, figures,
  graphs, equations, and captions.
- Docling is the intended primary extraction path in the current migration task.
- The archive documents concrete debugging, restructuring, and validation work.

## Use with qualification

- “Production-ready” appears in some assessments, but current bugs and pending
  benchmarks mean the thesis should say “production-oriented” or “prototype
  assessed for production,” unless a supervisor confirms otherwise.
- “Extracted every piece of information” should be avoided. The system attempts
  comprehensive extraction, but visual coverage, table normalization, and page
  grouping remain incomplete.
- The project used an owned/local GPU-server interpretation of “local-first”:
  models and data were intended to run under project control without requiring a
  third-party cloud LLM/API, while the final server could be accessed remotely by
  users. The original GPU failure and subsequent CERN Open Lab/ML Flow/Kubeflow
  compute-access phase should be described as part of the project timeline.
- The production-grade architecture and migration plan were prepared for stronger
  compute, but not every planned component was fully tested. The thesis must label
  each capability as implemented, demonstrated, migrated, planned, blocked, or
  benchmarked rather than treating the production design as proof of completion.
- Exact completed workloads, infrastructure dates, and the precise GPU model/name
  still need confirmation from records. Earlier project evidence refers to an RTX
  5090; the newly supplied wording says “1580,” so this identifier must be checked
  before publication.

## Do not expose

- Credentials, tokens, private URLs, or secrets that may appear in archived
  project-context files.
- Unverified personal or organizational claims from unrelated conversations.
