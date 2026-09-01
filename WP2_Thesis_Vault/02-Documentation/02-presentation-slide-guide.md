# CERN Multimodal RAG: Presentation Slide Assets & Screen Guide

This guide is structured to map the active screens of the CERN Multimodal RAG platform directly to presentation slides for stakeholders, clients, and technical teams.

---

## 1. System Telemetry & Hardware Hub
This screen provides real-time system monitoring, ensuring high reliability and performance under heavy RAG compute workloads.

![CERN RAG Telemetry Dashboard](/home/drd8/.gemini/antigravity/brain/4b384b94-12c8-4869-9a01-e032a83cc50d/artifacts/screenshot_1_dashboard.png)

### Key Features
- **Server Health Indicators**: Dynamic tracking of CPU utilization, RAM usage, storage availability, and database size.
- **Active Memory Footprint**: Crucial for tracking multi-GB local vector indexing limits in LanceDB.
- **Background Event Log**: Real-time logging of background ingestions, vector generation, and API health checks.

### Presentation Use Cases & Talking Points
- **System Integrity**: Show how the platform allows admins and scientists to verify that the local infrastructure (CPU/RAM) isn't bottlenecked during high-throughput ingestion.
- **Enterprise-Ready Infrastructure**: Emphasize that the system runs entirely on-premise/locally, with transparent telemetry that doesn't leak metadata to public clouds.

---

## 2. Interactive Physics Chat Workspace
The portal entry-point where researchers manage sessions, select intelligence cores, and begin physics inquiries.

![CERN RAG Chat Workspace](/home/drd8/.gemini/antigravity/brain/4b384b94-12c8-4869-9a01-e032a83cc50d/artifacts/screenshot_2_chat_empty.png)

### Key Features
- **Active Core Selector**: Dropdown to switch model configurations seamlessly (e.g. cloud-scale Llama 3.3 70B vs local Ollama Llama 3.1).
- **Session Sidebar**: Session list loaded directly from the SQLite metadata database, allowing researchers to pick up past inquiries.
- **Fast-Drop PDF Ingestion Zone**: Drag-and-drop box for uploading local scientific literature on the fly.

### Presentation Use Cases & Talking Points
- **Multi-Model Orchestration**: Explain that researchers are not locked into one LLM provider; they can switch between secure offline local fallbacks (Ollama) and high-reasoning cloud APIs.
- **Frictionless Onboarding**: Detail how scientists can drop new PDFs to instantly index them into their personal vector space without requiring developer assistance.

---

## 3. Multimodal Document Extraction Swarm
The automated ingestion pipeline showing how unstructured scientific papers are ingested, parsed, and semantically sliced.

![CERN RAG PDF Upload and Extraction UI](/home/drd8/.gemini/antigravity/brain/4b384b94-12c8-4869-9a01-e032a83cc50d/artifacts/screenshot_upload_ui.png)

### Key Features
- **Visual Ingestion Flow**: Step-by-step progress logging (Extracting, Captioning, Vectorizing, Indexing).
- **Tabular & Image Extraction**: Automatically runs layout parsers to pull complex tables into CSV format and extract figures with visual captions.
- **Metadata Tagging**: Extracts topics, titles, and summaries from the text to populate the search database.

### Presentation Use Cases & Talking Points
- **Unstructured to Structured**: Highlight the platform's ability to extract charts and tables that standard text-only RAG pipelines typically miss or corrupt.
- **Semantic Chunking**: Explain how the parser slices documents by sections and titles rather than arbitrary character splits, preserving context.

---

## 4. Agentic Knowledge Search & Self-Correction
This screen highlights the active generation phase, showing the agent scanning databases and performing self-evaluation.

![CERN RAG Generation State](/home/drd8/.gemini/antigravity/brain/4b384b94-12c8-4869-9a01-e032a83cc50d/artifacts/screenshot_3_synthesizing.png)

### Key Features
- **Low-Confidence Trigger**: Automatically launches external database scans (CERN Document Server API) if local confidence scores fall below thresholds.
- **Two-Stage Review Process**: The primary model drafts an answer, and a secondary review agent evaluates it against source context to eliminate hallucinations before display.

### Presentation Use Cases & Talking Points
- **Hallucination Prevention**: Reassure clients that the platform uses an automated self-reviewer step to verify every claim against indexed data.
- **Federated API Search**: Demonstrate that the system is not isolated; it automatically fetches external scientific abstracts when local resources are insufficient.

---

## 5. Context-Grounded Responses & Auto-Citations
The resulting synthesized answer, featuring precise grounding, citations, and suggested follow-ups.

![CERN RAG Context Grounded Chat Response](/home/drd8/.gemini/antigravity/brain/4b384b94-12c8-4869-9a01-e032a83cc50d/artifacts/screenshot_4_response.png)

### Key Features
- **Inline Citation Tags**: Labeled tags (e.g. `[C1]`, `[C2]`) that trace claims directly back to their source document page.
- **Suggested Follow-Ups**: Dynamically generated, logically sequenced questions that prompt researchers on next research steps.
- **Citations List**: Clear bibliographical footnotes detailing the source document and page number for quick verification.

### Presentation Use Cases & Talking Points
- **Scientific Auditability**: Highlight that every claim can be audited in seconds. No "black-box" summaries.
- **Continuous Exploration**: Detail how the dynamic follow-up questions help scientists uncover hidden connections without needing to formulate queries from scratch.

---

## 6. Dynamic Interactive Bibliography & Modal Preview
The side-by-side verification pane that appears when researchers click a citation badge.

![CERN RAG Interactive Source Viewer Modal](/home/drd8/.gemini/antigravity/brain/4b384b94-12c8-4869-9a01-e032a83cc50d/artifacts/screenshot_5_pdf.png)

### Key Features
- **Context Modal**: Displays the exact text chunk, the system-generated page summary, and topic classification.
- **Direct PDF Rendering**: Renders the source document page side-by-side with the chat, highlighting the matching text.

### Presentation Use Cases & Talking Points
- **Frictionless Fact-Checking**: Emphasize how scientists can verify citations without opening separate PDF readers or searching their local hard drives.
- **Context Preserved**: Showcase how the interface keeps the researcher in the flow, combining reading and reasoning in one view.
