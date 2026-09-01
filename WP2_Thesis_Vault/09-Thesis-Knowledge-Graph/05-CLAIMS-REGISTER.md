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
- GPU/CERN compute access is documented as a transition and request context;
  exact completed workloads need confirmation.

## Do not expose

- Credentials, tokens, private URLs, or secrets that may appear in archived
  project-context files.
- Unverified personal or organizational claims from unrelated conversations.
