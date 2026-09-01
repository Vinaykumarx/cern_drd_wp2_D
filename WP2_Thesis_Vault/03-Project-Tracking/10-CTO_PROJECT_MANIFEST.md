# CTO Project Manifest: Agent Zero (Cern Multimodal RAG)

## 🎯 Vision & Goals
To build a state-of-the-art, local-first scientific RAG system capable of high-fidelity extraction from complex CERN physics reports. The system provides "Agentic" intelligence—meaning it doesn't just search; it organizes, categorizes, and recommends data autonomously.

## 🏗️ Architecture Stack (Verified)

### 1. Frontend (The Swarm Dashboard)
- **Framework**: Next.js 15 (App Router).
- **Styling**: Tailwind CSS + Framer Motion.
- **Components**: Lucide Icons, React Markdown (GFM support).
- **Connection**: Axios (communicating with FastAPI on :8000).

### 2. Backend (Agent Zero Orchestrator)
- **Framework**: FastAPI (Python 3.13).
- **Inference**: Ollama (serving Local Gemma 4 / Llama 3.x).
- **Concurrency**: BackgroundTasks for long-running multimodal extractions.

### 3. Intelligence Layer (The Brain)
- **Agentic Chunking**: Uses `core/llm_client.py` to semantically divide text. 
- **Decision Policy**: LLM decides where to break chunks based on logic/concept shifts, not character counts.
- **Search Models**: BGE-base-en-v1.5 (Embeddings) + Cross-Encoder Reranker (Standard ms-marco).

### 4. Extraction & Vision Swarm
- **Layout**: `pymupdf4llm` (Markdown priority).
- **Vision**: `Qwen2-VL` + `BLIP` (Image captioning).
- **Data**: `pdfplumber` (Table-to-CSV) + `OpenCV` (Graph detection).

## 🔄 Core Data Flow
1. **Import**: PDF registered in `data/documents.json`.
2. **Extraction**: `extract_with_docid.py` produces `metadata.json` + assets.
3. **Chunking**: Agent Zero pipes Markdown to Ollama -> Semantic JSON Chunks.
4. **Vectorization**: Chunks stored in **LanceDB** with Topic/Category metadata.
5. **Retrieval**: HyDE (Ollama) -> Vector Search (LanceDB) -> Rerank (Cross-Encoder).
6. **Synthesis**: Gemma 4 summarizes with citations [C1].

## 🛡️ CTO Methodology & Safety Rules
1. **No-Break Principle**: Existing metadata schemas must remain backward compatible. Any new fields (Topic, Summary) must be nullable/optional.
2. **Local-First Reliability**: Ollama is the primary brain. Cloud fallbacks are only for development/debugging.
3. **Verification First**: All Core changes MUST pass `scripts/test_agentic_chunker.py` before being committed to the API.

## 🚀 Future Roadmap
- [ ] **Native PDF Navigation**: Deep-linking to #page=N from citations.
- [ ] **Agentic Discovery**: Recommending registered but un-indexed PDFs.
- [ ] **Physics-Aware Prompts**: Refining the semantic splitter for CERN terminology.
- [ ] **Swarm Monitoring**: Real-time logging of "Agent Thought" in the Dashboard.

---
*Locked & Signed: Antigravity AI (CTO Persona) - 2026-04-20*
