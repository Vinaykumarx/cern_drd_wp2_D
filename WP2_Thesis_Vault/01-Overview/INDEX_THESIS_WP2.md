# CERN DRD8 WP2 — Thesis Preparation Vault

**Author:** Vinay Kumar  
**Project:** AI-Assisted Knowledge Structuring for Radiation-Damage Materials  
**Work Package:** WP2 — Low-mass Mechanics and Thermal Management  
**Institution:** EPITA / CERN DRD8 Collaboration  
**Date:** 2026-08-31  

---
## 📋 Vault Purpose

This Obsidian vault consolidates all project files related to the CERN DRD8 WP2 thesis, providing a unified view across:
- **Timeline** — Key dates, milestones, and progression
- **Block-wise implementation** — Pipeline phases and components
- **Implementation plans** — Task breakdown and priorities
- **All MD files** — Documentation, tracking, and references
- **Project connections** — How each piece fits together

---
## 🗓️ Project Timeline

| Date | Phase | Milestone |
|------|-------|-----------|
| **2026-01-29** | — | Initial CERN RAG Prototype Development (audit date) |
| **2026-02-20** | — | Architecture audit completed; scaling challenges identified |
| **2026-02-23** | — | User requests slide-by-slide explanation |
| **2026-02-27** | — | Gemini block generated project context (MongoDB, Milvus, LangChain) |
| **2026-03-10** | — | Assistant helps refine presentation points |
| **2026-03-31** | — | Assistant demo prepared; chunking improvements |
| **2026-05-07** | **Phase 0** | Implementation plan executor started; 13 tasks loaded |
| **2026-05-07** | **Phase 1** | Critical fixes initiated: LanceDB sync, async/await, knowledge graph memory leak |
| **2026-05-27** | **Phase 2** | Multi-document RAG implemented; DocumentManager, extract_with_docid, enhanced RAG pipeline |
| **2026-08-31** | **Current** | Thesis vault created; all project files consolidated |

---
## 🏗️ Block-wise Implementation Architecture

The system consists of **5 primary blocks** (from architectural audit):

### 1. **Ingestion & Extraction Block** (Section 2.3)
- `pymupdf4llm` → Markdown extraction
- `pdfplumber` + `Camelot` → Table extraction (CSV)
- `Qwen2-VL` → Layout recovery for scanned pages
- `OpenCV` → Graph contour detection
- `BLIP` → Figure captioning
- Output: `outputs/{doc_id}/` with metadata.json, pages_text.json, tables_index.json, figures_index.json

### 2. **Vectorization & Storage Block** (Section 2.4)
- **LanceDB Schema** (32 fields): id, text, source, page, chunk_index, doc_id, section_type, image_path, table_csv, kind, title, topic, summary, keywords, quality_score, vector (768-dim)
- **Chunking Strategy**: Deterministic header chunks + LLM-based enrichment + virtual chunks for tables/figures
- **Storage Scale**: ~3 KB/chunk; 50-page PDF → ~350 chunks → ~1.1 MB

### 3. **Retrieval & Reranking Block** (Section 2.5)
1. Dense query embedding (BGE-base-en-v1.5, 768-D)
2. ANN search (top_k * 5 candidates)
3. Cross-Encoder reranking (ms-marco-MiniLM-L-6-v2)
4. Categorical separation: text_hits, figure_hits, table_hits

### 4. **Agent & Swarm Orchestration Block** (Section 2.6)
- **Research Agent**: Local vector search + CDS API fallback
- **Verification Agent**: Citation validation, confidence scoring
- **Synthesis Agent**: Grounded response with [C1] citations
- **Secondary AI Reviewer**: Safety guardrail filter

### 5. **User Interface Block** (Section 2.1)
- **Telemetry Hub**: Real-time vector DB metrics
- **Neural Chat**: Scientific inquiries with inline source citations
- **Neuro Map**: Force-directed graph of vector clusters

---
## 📁 Vault Structure & File Mapping

```
01-Overview/
  └── INDEX_THESIS_WP2.md  ← This file — master connection map

02-Documentation/
  ├── 01-production-assessment.md    ← Production blockers & roadmap
  ├── 02-presentation-slide-guide.md ← Slide-by-slide presentation guide
  ├── 03-architectural-audit.md      ← 1000+ line audit with all analyses
  └── 04-my-role-and-status.md       ← CERN role & responsibilities

04-Architecture/
  ├── 01-cernGroundedRagArchitecture.png
  ├── 02-CERN-Multimodal-RAG-Architecture-Report.html
  ├── 03-CERN-Multimodal-RAG-Detailed-Compute-Report.docx
  ├── 04-CERN-Multimodal-RAG-Blueprint.pdf
  ├── 05-CERN-RAG-Final-Architecture.pages
  ├── 06-endToendMultimodel.png
  ├── 07-RagArchitecture.png
  └── 08-CERN-RAG-Chemical-Pipeline.png

05-Presentations/
  ├── 01-JUNE03DRD8-WP2.pptx          ← Main WP2 presentation (7.5MB)
  ├── 02-DRD8Workshop-WP2.2.pptx      ← DRD8 Workshop WP2.2 (4.1MB)
  ├── 03-AI-Assisted-Knowledge-Structuring.pptx
  ├── 04-AI-Assisted-Knowledge-StructuringPPT.pptx
  ├── 05-AI-Assisted-Knowledge-StructuringPPT-full.pptx  ← Full version (48MB)
  ├── 06-Agent-Zero-Engineering-Roadmap.pptx
  ├── 07-Multimodal-Scientific-RAG.pptx
  └── 08-DRD8-WP4-XR-Software.pptx

06-Reference-Materials/
  ├── CERN-98-01.pdf                  ← CERN Yellow Report 98-01
  ├── CERN-98-01-2.pdf                  ← CERN Yellow Report 98-01 (duplicate)
  ├── CERN-2001-006.pdf                 ← CERN Report 2001-006
  ├── CERN-89-12.pdf                    ← CERN Report 89-12
  ├── CERN-Yellow-Report-357576.pdf     ← CERN Yellow Report 357576
  └── omni-model-catalog.md           ← Model catalog reference

07-Chat-History/
  ├── hermes-integration.md           ← opencode + Hermes integration config
  ├── codex-goals.sqlite
  ├── codex-logs.sqlite
  ├── codex-memories.sqlite
  ├── codex-queue.sqlite
  └── codex-thread-history.sqlite

08-Source-Code/
  ├── backend/main.py                 ← FastAPI backend (hardcoded persona)
  ├── core/rag_pipeline.py            ← RAG retrieval & reranking
  ├── core/semantic_chunker.py        ← Markdown header-based chunking
  ├── core/vector_store_lance.py      ← LanceDB schema & operations
  ├── core/agents/swarm_orchestrator.py ← 3-agent swarm orchestration
  └── extraction/extract_with_docid.py ← Ingestion pipeline with doc tracking
```

---
## 🔗 Key Connections & Cross-References

### Critical Production Blockers (from `01-production-assessment.md`)
1. **Synchronous Core Queries** — FastAPI endpoints call synchronous LanceDB search, blocking event loop at 20+ concurrent users
2. **File Descriptor Leakage** — Socket exhaustion without connection pooling
3. **Graph Rendering Memory Blowup** — Knowledge graph fetches all vectors; browser OOM at >200 vectors
4. **Hardcoded Persona** — "Claude Agentic Physics Copilot" overrides system prompts regardless of model

### Implementation Plan Phases (from `13-IMPLEMENTATION_LOG.txt`)
- **Phase 1 (Critical, 26 hrs)**: TASK-0001 LanceDB Sync, TASK-0002 Async/Await, TASK-0003 Memory Leak
- **Phase 2 (High, 60 hrs)**: TASK-0004 Docling Integration, TASK-0005 Error Handling, TASK-0006 Logging
- **Phase 3 (Medium, 60 hrs)**: TASK-0007 Performance, TASK-0008 Unit Tests, TASK-0009 Component Coupling
- **Phase 4 (Low, 20 hrs)**: TASK-0010 API Docs, TASK-0011 Deployment Guide

### Multi-Document RAG Implementation (from `14-MULTIDOC_IMPLEMENTATION.md`)
- **DocumentManager** (`core/document_manager.py`) — Registry management
- **Extract Wrapper** (`extraction/extract_with_docid.py`) — PDF processing with doc_id tracking
- **Enhanced RAG Pipeline** (`core/rag_pipeline.py`) — Updated for multi-document search
- **Vector Store Schema** — Added `doc_id` field for document filtering

### Hardcoded Persona Issue (in `08-Source-Code/backend/main.py`)
- Lines 268-271: System prompt forces "You are the Local Agentic Physics Copilot" regardless of model
- Lines 1110-1118: Document query endpoint uses "Claude Agentic Physics Copilot" persona
- **Fix needed**: Replace with configurable `AGENT_SYSTEM_PROMPT` environment variable

---
## 📊 Critical Metrics for Thesis

| Metric | Value |
|--------|-------|
| **Storage** | ~3 KB/chunk in LanceDB |
| **50-page PDF** | ~350 chunks → ~1.1 MB |
| **GPU VRAM** | ~1.2 GB for embeddings + reranking |
| **CPU RAM** | ~5 GB for Qwen2-VL on CPU |
| **Response target** | <1.5s (optimized), currently fails at 20+ concurrent users |
| **Vector DB** | LanceDB (local, serverless) |
| **Embeddings** | BAAI/bge-base-en-v1.5 (768-dim) |
| **Reranking** | cross-encoder/ms-marco-MiniLM-L-6-v2 |

## 📝 Internship Defense Documents (Jan 16, 2026)

Four key administrative documents from your CERN EPITA internship, all dated **2026-01-16**, that define the final requirements for your radiation-damage materials RAG system:

| Document | Format | Purpose |
|----------|--------|---------|
| `20260116-DOC-ConsignesStageFinDEtudesPromo2026 2` | PDF (348KB) | **Final internship study guidelines** — rules and procedures for completing the internship |
| `20260116-MOD-PVSoutenancePromo2026` | PDF | **Modified presentation defense guidelines** — updated criteria for the final defense presentation |
| `20260116-DOC-FicheDeSynthèseMscPromo2026` | DOC (2.1MB) | **MSc synthesis sheet** — structured document to synthesize your work for the Master's degree |
| `20260116-DOC-EvaluationDesCompetencesStagePromo2026` | PDF (1MB) | **Competency evaluation** — assessment of skills gained during the internship |

**Timeline connection**: These documents were created **two weeks before** the implementation plan executor was started (2026-05-07), placing them in the early phase of your WP2 thesis work. They define the formal requirements that your RAG system must satisfy for the Master's degree defense.

**Thesis chapter relevance**:
- **Chapter 1 (Introduction)**: Reference these documents for official CERN/EPITA requirements
- **Chapter 7 (Production Readiness Assessment)**: Use the evaluation criteria from these docs to assess if your system meets the competency standards
- **Chapter 9 (Future Work)**: Any gaps between your system's capabilities and these doc requirements become "future work" items

---
## 🎯 Recommended Thesis Chapter Workflow

Based on vault organization, follow this progression:

### Chapter 1: Introduction
- CERN DRD8 context, WP2 goals, radiation-damage materials challenge
- Reference: `04-my-role-and-status.md`, `10-CTO_PROJECT_MANIFEST.md`
- Internship defense docs: `02-Documentation/20260116-DOC-ConsignesStageFinDEtudesPromo2026 2.pdf`, `02-Documentation/20260116-MOD-PVSoutenancePromo2026.pdf`, `02-Documentation/20260116-DOC-FicheDeSynthèseMscPromo2026.doc`, `02-Documentation/20260116-DOC-EvaluationDesCompetencesStagePromo2026.pdf`

### Chapter 2: Literature Review
- RAG systems, multimodal extraction, scientific document understanding
- Reference: `06-Reference-Materials/` (CERN reports), `omni-model-catalog.md`

### Chapter 3: System Architecture
- Use `03-architectural-audit.md` §2.1–2.7 for full architecture
- Diagrams from `04-Architecture/` and `05-Presentations/07-Multimodal-Scientific-RAG.pptx`

### Chapter 4: Multimodal Extraction Pipeline
- Use `03-architectural-audit.md` §2.3 for pipeline details
- Reference: `14-MULTIDOC_IMPLEMENTATION.md` for multi-document extension

### Chapter 5: Retrieval & Reranking
- Use `03-architectural-audit.md` §2.5
- Key metrics from vault metrics table

### Chapter 6: Agentic Swarm Orchestration
- Use `03-architectural-audit.md` §2.6
- Note hardcoded persona issue and proposed fixes

### Chapter 7: Production Readiness Assessment
- Use `01-production-assessment.md` for block-wise assessment
- Critical blockers and roadmap

### Chapter 8: Scaling Challenges & Solutions
- Use `01-production-assessment.md` §4 (bottlenecks)
- Use `03-architectural-audit.md` §4.1–4.3 (memory leak, async blocking, concurrency)
- Reference multi-document implementation solutions

### Chapter 9: Future Work
- Use `01-production-assessment.md` roadmap (Phases 1–4)
- Reference `13-IMPLEMENTATION_LOG.txt` for remaining tasks

### Chapter 10: Conclusion
- Summary of achievements and limitations
- Impact on radiation-damage materials research

---
## 🔍 Quick Navigation Tips

### In Obsidian:
1. **Use cmd+P** (or ctrl+P) to quickly jump to any file
2. **Link files** using `[[01-Overview/INDEX_THESIS_WP2]]` for the master index
3. **Create backlinks** — most files already reference each other
4. **Search across vault** with cmd+Shift+F (ctrl+Shift+F)

### Key Quick-Start Links:
- `[[01-Overview/INDEX_THESIS_WP2]]` — Master connection map
- `[[03-Project-Tracking/13-IMPLEMENTATION_LOG.txt]]` — Execution log with task breakdown
- `[[03-Project-Tracking/14-MULTIDOC_IMPLEMENTATION.md]]` — Multi-document RAG (complete)
- `[[02-Documentation/03-architectural-audit.md]]` — Comprehensive audit (1000+ lines)
- `[[08-Source-Code/backend/main.py]]` — Hardcoded persona issue location

---
*Vault last updated: 2026-08-31*  
*For thesis defense preparation — all files organized for easy cross-referencing*