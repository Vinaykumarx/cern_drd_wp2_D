# Architecture Evolution

## Stage A — Mac-compatible prototype

```text
PDF → PyMuPDF/text extraction → LayoutLMv3 + BLIP2
    → custom chunks → SentenceTransformers → Qdrant Cloud → Streamlit
```

Constraint: low-memory, CPU-first experimentation on the Mac.

## Stage B — Local multimodal restructuring

```text
PDF → text/table/image extraction → captions and filtering
    → text/figure/table chunks → embeddings → LanceDB → Streamlit previews
```

Decision drivers: Qdrant API/network friction, local reproducibility, explicit
schemas, and easier control of multimodal metadata.

## Stage C — Modular production direction

```text
Next.js → FastAPI → document manager
  → PyMuPDF/pymupdf4llm + pdfplumber + OCR/VLM
  → semantic chunks + provenance metadata
  → BGE 768-d vectors → LanceDB → cross-encoder reranking
  → grounded generation and citations
```

Additional concepts: document IDs, multi-document filtering, verification,
synthesis, local/cloud model fallback, telemetry, and knowledge-graph views.

## Stage D — Compute-enabled extraction direction

```text
PDF → Docling primary parser
    → page-aware text/tables/figures + VLM recovery where required
    → normalized multimodal items and citations
    → embeddings/retrieval/reranking → grounded answers
```

This is the target direction, not a claim that every component is complete.

## Key transformations

| Concern | Early prototype | Later direction |
|---|---|---|
| Storage | Qdrant Cloud | Local LanceDB, scalable alternatives considered |
| UI | Streamlit | FastAPI + Next.js; Streamlit deprecated |
| Embeddings | SentenceTransformers | BGE, 768 dimensions |
| Retrieval | Vector search | Vector search + cross-encoder reranking |
| Extraction | PyMuPDF/LayoutLMv3/BLIP2 | Docling + OCR/VLM + legacy fallbacks |
| Scope | Single PDF | Multi-document, document IDs, filtering |
| Answering | Basic RAG | Research, verification, synthesis, citations |
| Hardware | Mac/CPU/lightweight models | CERN/GPU-oriented batch and VLM processing |

## Thesis interpretation

The important contribution is not one library choice. It is the controlled
evolution of the system in response to hardware, scientific-document complexity,
reproducibility, scalability, and citation requirements.
