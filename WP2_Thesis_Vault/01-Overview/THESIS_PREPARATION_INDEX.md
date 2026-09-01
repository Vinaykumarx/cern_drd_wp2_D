# CERN DRD8 WP2 — Thesis Preparation Archive

**Author:** Vinay Kumar  
**Project:** AI-Assisted Knowledge Structuring for Radiation-Damage Materials  
**Work Package:** WP2 — Low-mass Mechanics and Thermal Management  
**Institution:** EPITA / CERN DRD8 Collaboration  
**Date:** 2026-08-31

---

## 📁 Folder Structure

```
thesis-preparation/
├── THESIS_PREPARATION_INDEX.md          # This file
├── documentation/                        # Technical documentation & audit reports
├── presentations/                        # Stakeholder presentation decks
├── architecture-diagrams/                # System architecture visuals
├── reference-materials/                  # CERN reports, papers, references
├── project-tracking/                     # Project management, tasks, status
├── chat-history/                         # ChatGPT export conversations
├── conversation-logs/                    # OpenCode/Codex conversation databases
└── source-code-reference/                # Key source files (copied separately)
```

---

## 📄 Documentation (`documentation/`)

| File | Description | Source |
|------|-------------|--------|
| `01-production-assessment.md` | Production readiness assessment, scaling bottlenecks, roadmap | `cernbox/Maxrad-database/cern_rag_production_presentation.md` |
| `02-presentation-slide-guide.md` | Slide-by-slide presentation guide with UI screenshots | `cernbox/Documents/wp2/cern_rag_presentation_assets.md` |
| `03-architectural-audit.md` | 1000+ line architectural audit with scaling analysis | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/cern-rag-prototype-development.md` |
| `04-my-role-and-status.md` | Your CERN role, responsibilities, current status | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/cern-role-and-status.md` |
| `05-cern-docs-and-certificates.md` | CERN documentation and certificates | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `06-cern-accelerator-shutdown.md` | Accelerator shutdown 2025 info | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `07-cern-campus-overview.md` | CERN campus overview | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `08-cern-pre-registration.md` | Pre-registration process | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `09-cern-registration-issue.md` | Registration issues | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `10-cern-role-and-status.md` | Duplicate of 04 | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `11-cern-ssh-troubleshooting.md` | SSH connection troubleshooting | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `12-cern-yellow-reports.md` | CERN Yellow Reports reference | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `13-cern-full-form.md` | CERN full form | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `14-cern-rag-prototype-dev.md` | Duplicate of 03 | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `15-cern-xr-ai-collaboration.md` | XR/AI collaboration notes | `cern/Master-Knowledge-Vault/CERN-DRD8-WP4/` |
| `00-Master-Knowledge-Vault-Index.md` | Master knowledge vault index | `cern/Master-Knowledge-Vault/Index.md` |
| `00-Master-Knowledge-Vault-README.md` | Master knowledge vault README | `cern/Master-Knowledge-Vault/README.md` |

## 🕸️ Thesis Knowledge Graph (`09-Thesis-Knowledge-Graph/`)

This non-destructive synthesis layer connects the archive to the thesis timeline,
architecture evolution, EPITA chapter structure, evidence sources, and unresolved
questions. Start with `00-MASTER-MAP.md` and open the folder in Obsidian Graph view.

| File | Purpose |
|------|---------|
| `00-MASTER-MAP.md` | Central navigation and thesis argument |
| `01-PROJECT-TIMELINE.md` | Chronological project evolution |
| `02-ARCHITECTURE-EVOLUTION.md` | Technical stages and decisions |
| `03-THESIS-EVIDENCE-MAP.md` | Chapter-to-source mapping |
| `04-GAPS-AND-QUESTIONS.md` | Missing facts and memory questionnaire |
| `05-CLAIMS-REGISTER.md` | Confidence and wording safeguards |
| `06-OBSIDIAN-GRAPH.md` | Mermaid diagram and graph instructions |
| `07-CONFIRMED-INTERNSHIP-FACTS.md` | Confirmed dates, official WP2 context, presentation evidence, and provisional team map |
| `08-THESIS-DRAFT-LAYOUT.md` | Recommended page budget, page-by-page report index, populated evidence, and gap placeholders |
| `10-Thesis-Documents/EPITA_WP2_Thesis_Manuscript.docx` | Formal 69-page thesis manuscript populated from the vault, with only unsupported facts left for completion |

---

## 🎯 Presentations (`presentations/`)

| File | Description | Source |
|------|-------------|--------|
| `01-JUNE03DRD8-WP2.pptx` | Main WP2 presentation (7.5MB) | `cernbox/Maxrad-database/JUNE03DRD8 WP2.pptx` |
| `02-DRD8Workshop-WP2.2.pptx` | DRD8 Workshop WP2.2 (4.1MB) | `cernbox/Maxrad-database/DRD8Workshop-WP2.2.pptx` |
| `03-AI-Assisted-Knowledge-Structuring.pptx` | AI-assisted knowledge structuring | `cernbox/Maxrad-database/AIAssisted-Knowledge-Structuring-for-RadiationDamage-Materials (1).pptx` |
| `04-AI-Assisted-Knowledge-StructuringPPT.pptx` | AI-assisted knowledge structuring PPT | `cernbox/Maxrad-database/AI-Assisted-Knowledge-StructuringPPT.pptx` |
| `05-AI-Assisted-Knowledge-StructuringPPT-full.pptx` | Full version (48MB) | `cernbox/Maxrad-database/AI-Assisted-Knowledge-StructuringPPT_full.pptx` |
| `06-Agent-Zero-Engineering-Roadmap.pptx` | Agent Zero engineering roadmap | `cernbox/Maxrad-database/Agent_Zero_Engineering_Roadmap.pptx` |
| `07-Multimodal-Scientific-RAG.pptx` | Multimodal Scientific RAG | `cernbox/Maxrad-database/Multimodal_Scientific_RAG.pptx` |
| `08-DRD8-WP4-XR-Software.pptx` | WP4 XR Software | `Desktop/022526 DRD8 WP4 XR Software.pptx` |

---

## 🏗️ Architecture Diagrams (`architecture-diagrams/`)

| File | Description | Source |
|------|-------------|--------|
| `01-cernGroundedRagArchitecture.png` | Grounded RAG architecture | `cernbox/Maxrad-database/cernGroundedRagArchitecture.png` |
| `02-CERN-Multimodal-RAG-Architecture-Report.html` | Full architecture report | `cernbox/Maxrad-database/CERN_Multimodal_RAG_Architecture_Report.html` |
| `03-CERN-Multimodal-RAG-Detailed-Compute-Report.docx` | Detailed compute requirements | `cernbox/Maxrad-database/CERN_Multimodal_RAG_Detailed_Compute_Report.docx` |
| `04-CERN-Multimodal-RAG-Blueprint.pdf` | Architecture blueprint | `cernbox/Maxrad-database/CERN_Multimodal_RAG_Blueprint.pdf` |
| `05-CERN-RAG-Final-Architecture.pages` | Final architecture (Pages) | `cernbox/Maxrad-database/CERN_RAG_Final_Architecture 2.pages` |
| `06-endToendMultimodel.png` | End-to-end multimodal flow | `cernbox/Maxrad-database/endToendMultimodel.png` |
| `07-RagArchitecture.png` | RAG architecture diagram | `cernbox/Maxrad-database/RagArchitecture.png` |
| `08-CERN-RAG-Chemical-Pipeline.png` | Chemical pipeline diagram | `cernbox/Maxrad-database/CERN RAG Chemical Pipeline-2026-02-10-034059.png` |

---

## 📚 Reference Materials (`reference-materials/`)

| File | Description |
|------|-------------|
| `CERN-98-01.pdf` | CERN Yellow Report 98-01 |
| `CERN-98-01-2.pdf` | CERN Yellow Report 98-01 (duplicate) |
| `CERN-2001-006.pdf` | CERN Report 2001-006 |
| `CERN-89-12.pdf` | CERN Report 89-12 |
| `CERN-Yellow-Report-357576.pdf` | CERN Yellow Report 357576 |
| `omni-model-catalog.md` | Model catalog reference |

---

## 📋 Project Tracking (`project-tracking/`)

| File | Description |
|------|-------------|
| `01-DMOS-PROJECT_STATUS.md` | DMOS project status (Phase 3 complete) |
| `02-DMOS-TASKS.md` | DMOS tasks |
| `03-DMOS-PHASE-0-BASELINE.md` | DMOS Phase 0 baseline |
| `04-DMOS-AGENTS.md` | DMOS agent instructions |
| `05-CLAUDE-DOMAIN-AUTH-PROJECT_STATUS.md` | Claude domain auth status |
| `06-CLAUDE-DOMAIN-AUTH-TASKS.md` | Claude domain auth tasks |
| `07-CLAUDE-DOMAIN-AUTH-PHASE-0-BASELINE.md` | Claude domain auth baseline |
| `08-PROJECT-AGENTS.md` | Project AGENTS.md |
| `09-ARCHITECTURE_REVIEW.md` | Architecture review |
| `10-CTO_PROJECT_MANIFEST.md` | CTO project manifest |
| `11-DELIVERABLES_SUMMARY.md` | Deliverables summary |
| `12-FINAL_SUMMARY.md` | Final summary |
| `13-IMPLEMENTATION_LOG.txt` | Implementation log |
| `14-MULTIDOC_IMPLEMENTATION.md` | Multi-document implementation |
| `15-PROJECT_AGENT_README.md` | Project agent README |
| `16-PROJECT_TRACKING_SETUP.md` | Project tracking setup |
| `17-QUICK_REFERENCE.md` | Quick reference |
| `18-QUICK_START_AGENT.md` | Quick start agent |
| `19-README.md` | Project README |
| `20-STARTUP_GUIDE.md` | Startup guide |
| `21-STARTUP_VERIFICATION.txt` | Startup verification |
| `22-CERN-AGENTS.md` | CERN AGENTS.md |
| `23-PROJECT_CONTEXT.md` | Project context |

---

## 💬 Chat History (`chat-history/`)

**ChatGPT Export (Full conversations):**
- `chatgpt-conversations-000.json` — Conversations batch 0
- `chatgpt-conversations-001.json` — Conversations batch 1
- `chatgpt-conversations-002.json` — Conversations batch 2
- `chatgpt-conversations-003.json` — Conversations batch 3
- `chatgpt-conversations-004.json` — Conversations batch 4
- `chatgpt-conversations-005.json` — Conversations batch 5
- `chatgpt-chat.html` — Full HTML export
- `chatgpt-export-manifest.json` — Export manifest
- `chatgpt-asset-file-names.json` — Asset file names
- `chatgpt-library-files.json` — Library files
- `chatgpt-shared-conversations.json` — Shared conversations
- `chatgpt-user.json` — User info

---

## 🗄️ Conversation Logs (`conversation-logs/`)

**OpenCode Database:**
- `opencode-history.db` — SQLite database with all OpenCode conversations

**Codex Databases:**
- `codex-thread-history.sqlite` — Thread history
- `codex-logs.sqlite` — Logs
- `codex-state.sqlite` — State
- `codex-memories.sqlite` — Memories
- `codex-goals.sqlite` — Goals
- `codex-queue.sqlite` — Queue

**Configuration:**
- `hermes-integration.md` — Hermes integration config

---

## 🔑 Key Technical Details for Thesis

### System Architecture
- **Frontend:** Next.js 15 (App Router) + Tailwind CSS
- **Backend:** FastAPI (Python) on port 8000
- **Vector DB:** LanceDB (local, serverless)
- **Embeddings:** BAAI/bge-base-en-v1.5 (768-dim)
- **Reranking:** cross-encoder/ms-marco-MiniLM-L-6-v2
- **LLM:** OpenRouter (Hermes-3-Llama-3.1-405B) → Ollama fallback
- **OCR/VLM:** Qwen2-VL-2B-Instruct, Tesseract, BLIP

### Multimodal Extraction Pipeline
1. `pymupdf4llm` → Markdown extraction
2. `pdfplumber` + `Camelot` → Table extraction (CSV)
3. `Qwen2-VL` → Layout recovery for scanned pages
4. `OpenCV` → Graph contour detection
5. `BLIP` → Figure captioning

### Agentic Swarm (3-Agent)
1. **Research Agent** — Local vector search + CDS API fallback
2. **Verification Agent** — Citation validation, confidence scoring
3. **Synthesis Agent** — Grounded response with [C1] citations

### Critical Production Blockers (from audit)
1. Hardcoded "Claude Physics Copilot" persona in `backend/main.py`
2. Sync LanceDB calls blocking FastAPI event loop
3. Knowledge graph fetches ALL vectors → browser OOM (>200 chunks)
4. No task queue (FastAPI BackgroundTasks only)
5. SQLite session locking under concurrency
6. Local filesystem storage (no S3/object storage)

### Roadmap
| Phase | Focus | Timeline |
|-------|-------|----------|
| 1 | Fix persona, paginate graph API | Immediate |
| 2 | Docling integration, Celery/Redis | Short-term |
| 3 | S3 storage, Qdrant cluster | Medium-term |
| 4 | vLLM inference server, ColPali | Long-term |

---

## 📝 Thesis Writing Guide

### Suggested Chapter Structure

1. **Introduction** — CERN DRD8 context, WP2 goals, radiation-damage materials challenge
2. **Literature Review** — RAG systems, multimodal extraction, scientific document understanding
3. **System Architecture** — Use `architecture-diagrams/` + `documentation/03-architectural-audit.md`
4. **Multimodal Extraction Pipeline** — Use `documentation/03-architectural-audit.md` §2.3
5. **Retrieval & Reranking** — Use `documentation/03-architectural-audit.md` §2.5
6. **Agentic Swarm Orchestration** — Use `documentation/03-architectural-audit.md` §2.6
6. **Production Readiness Assessment** — Use `documentation/01-production-assessment.md`
7. **Scaling Challenges & Solutions** — Use `documentation/03-architectural-audit.md` §4
8. **Future Work** — Use `documentation/01-production-assessment.md` roadmap
9. **Conclusion**

### Key Metrics to Cite
- **Storage:** ~3 KB/chunk in LanceDB
- **50-page PDF:** ~350 chunks → ~1.1 MB
- **GPU VRAM:** ~1.2 GB for embeddings + reranking
- **CPU RAM:** ~5 GB for Qwen2-VL on CPU
- **Response target:** <1.5s (optimized), currently fails at 20+ concurrent users

### Files to Reference in Thesis
- `documentation/03-architectural-audit.md` — Primary technical reference
- `documentation/01-production-assessment.md` — Production gaps
- `presentations/01-JUNE03DRD8-WP2.pptx` — Presentation slides for defense
- `architecture-diagrams/02-CERN-Multimodal-RAG-Architecture-Report.html` — Architecture visuals

---

## 🔍 Source Code Reference (in main project)

Key files to reference from the main codebase:
- `backend/main.py` — FastAPI endpoints, hardcoded persona
- `core/rag_pipeline.py` — RAG retrieval & reranking
- `core/agents/swarm_orchestrator.py` — 3-agent swarm
- `extraction/extract_with_docid.py` — Ingestion pipeline
- `core/semantic_chunker.py` — Markdown header-based chunking
- `core/vector_store_lance.py` — LanceDB schema & operations
- `validate_startup.py` — 8-component health checks
- `frontend/src/app/page.tsx` — Main dashboard (Telemetry/Chat/Neuro Map)

---

## ✅ Verification

All files copied from original locations to `thesis-preparation/` without deletion of originals.
Total: ~150+ files organized across 7 categories.
Ready for thesis writing and defense preparation.
