# CERN Multimodal RAG System Architecture

## Overview
The CERN Multimodal RAG (Retrieval-Augmented Generation) system processes technical PDF reports (especially scanned/image-heavy documents) to extract text, tables, figures, and enable semantic search. The system combines traditional parsing with vision-language model (VLM) fallback for robust document understanding.

## Core Pipeline Stages

### 1. Document Processing (`extraction/extract_with_docid.py`)
Processes PDFs with unique `doc_id` to generate structured outputs.

**Key Steps:**
1. **PDF Handling**: Copies PDF to temporary location for processing
2. **Native Markdown Extraction**: Uses `pymupdf4llm` for layout-aware Markdown text per page
3. **Sparse Text Recovery** (triggered when >60% pages have <80 chars):
   - Plain-text extraction via PyMuPDF
   - OCR via Tesseract (if available)  
   - **VLM Fallback**: Qwen2-VL generates Markdown from page images
4. **Table Extraction**:
   - Primary: `pdfplumber` (finds tables via whitespace/lines)
   - Fallback: `Camelot` (lattice then stream) for complex ruled tables
5. **Image Extraction**: PyMuPDF extracts raster images (PNG/JPEG)
6. **Graph Detection**: OpenCV contour analysis (>5 contours = graph)
7. **Image Captioning**: BLIP model generates descriptive captions
8. **Metadata Aggregation**: Combines all data into `metadata.json`

### 2. VLM-Based Layout Parser (`extraction/extract_vlm_layout.py`)
Activated when native text extraction fails (scanned PDFs).

**Implementation:**
- **Model**: Qwen2-VL-2B-Instruct (CPU-optimized, strong document understanding)
- **Processing**: Converts PDF pages to images → VLM generates Markdown
- **Output**: Saves per-page Markdown to `pages_text.json`
- **Advantages**: 
  - Runs locally without API costs
  - Understands document layout (tables, headings, reading order)
  - Superior to pure OCR for complex/scanned documents

### 3. Table Extraction from VLM Text
When VLM produces Markdown output, the system extracts tables using pattern matching:

```
| Header1 | Header2 |
|---------|---------|
| cell1   | cell2   |
```

Converts Markdown tables to pandas DataFrames and saves as CSV files, ensuring tabular data is preserved even when native extractors fail.

### 4. Figure & Graph Indexing
All extracted images are recorded in `figures_index.json` with:
- Page number and file path
- `kind`: `graph` (detected via contour analysis) or `image` 
- Generated caption from BLIP model
- Associated `doc_id` for traceability

### 5. Metadata Structure (`metadata.json`)
The unified metadata file contains:
```json
{
  "doc_id": "CERN_89_12",
  "pages": [
    { "page": 1, "text": "...", "doc_id": "...", "pdf_source": "..." }
  ],
  "tables": {
    "page_5_table_1": {
      "page": 5,
      "index": 1,
      "csv_file": "outputs/CERN_89_12/page_5_table_1.csv",
      "doc_id": "CERN_89_12"
    }
  },
  "figures": {
    "page_7_img_3": {
      "page": 7,
      "image_path": "outputs/CERN_89_12/page_7_img_3.png",
      "doc_id": "CERN_89_12", 
      "caption": "Graph showing tensile strength vs radiation dose",
      "kind": "graph"
    }
  }
}
```
Note: The `pdf_source` field tracks the originating PDF for UI popup functionality.

### 6. Vector Indexing (`core/rag_pipeline.py` + `core/vector_store_lance.py`)
**Embedding Model**: BAAI/bge-base-en-v1.5 (sentence-transformers)

**Chunk Types Created:**
- **Text Chunks**: Sentence-window chunking (~100 tokens) with overlap
- **Table Chunks**: CSV data serialized to Markdown, treated as text
- **Figure/Graph Chunks**: BLIP captions used as text content (image embedding planned)

**Chunk Metadata Includes:**
- `chunk_id`, `text`, `source`, `page`, `doc_id`
- `metadata`: Additional context (source type, bbox if available)
- `pdf_source`: Source PDF filename for popup links
- Agentic metadata (title, topic, summary, keywords, quality_score)

**Storage**: LanceDB table enabling:
- Hybrid search: Vector similarity + BM25 keyword scoring
- Metadata filtering (by doc_id, page, type, source)
- Persistent, zero-server operation

### 7. Retrieval & Generation (`app/streamlit_app.py`)
**Search Process:**
1. User query processed through same embedding model
2. Hybrid search (vector + BM25) returns top-k chunks
3. Optional re-ranking available
4. Context built from top chunks with source citations
5. LLM prompt: 
   ```
   Answer based only on this context:
   {context}
   
   Question: {question}
   Answer:
   ```

**UI Features:**
- Interactive table display (DataFrames)
- Figures with captions
- Clicking search results opens source PDF at exact page via `#page=` parameter
- Query processing with progress indicators

## Actual Implemented Components & Improvements

### Technologies Used (from requirements.txt)
- **Core**: lancedb, pyarrow, sentence-transformers, numpy, pandas
- **VLM/Image**: torch, torchvision, transformers, qwen-vl-utils, PyMuPDF, pdfplumber, opencv-python-headless, Pillow
- **Processing**: pymupdf4llm==0.0.5 (Markdown extraction)
- **Web**: streamlit, python-dotenv, groq, requests, fastapi
- **Models**: BAAI/bge-base-en-v1.5 (embedding), Salesforce/blip-image-captioning-base (captioning), Qwen/Qwen2-VL-2B-Instruct (VLM)

### Key Improvements Over Baseline
1. **Hybrid Table Extraction**: pdfplumber + Camelot fallback handles more table types than either alone
2. **Intelligent Sparse Recovery**: Tiered approach (text → OCR → VLM) avoids unnecessary VLM usage
3. **VLM Table Recovery**: Extracts tables from VLM-generated Markdown when native methods fail
4. **Context Preservation**: `pdf_source` tracking enables accurate PDF popups
5. **Rich Metadata**: Agentic chunk metadata (title, topic, etc.) improves retrieval relevance
6. **Graph Detection**: OpenCV-based heuristic identifies plots/diagrams in figures

### Design Choices Justified
| Component | Choice | Why Selected |
|-----------|--------|--------------|
| **Text Extraction** | pymupdf4llm → Markdown | Preserves layout better than plain text; Markdown enables further parsing |
| **Sparse Recovery** | Plain-text → OCR → VLM | Cost-effective: avoids VLM unless truly needed |
| **Table Extraction** | pdfplumber + Camelot | Covers widest range of table types without heavy ML models |
| **VLM Model** | Qwen2-VL-2B-Instruct | CPU-runnable, open-source, strong document understanding |
| **Vector Store** | LanceDB | Zero-config, hybrid search, persistent - ideal for self-contained system |
| **Embedding** | BAAI/bge-base-en-v1.5 | Strong performance, good balance of size/quality |
| **Captioning** | BLIP | Efficient image-to-text model sufficient for indexing needs |
| **UI Framework** | Streamlit | Rapid development, minimal boilerplate for internal tools |

## Data Flow
```
PDF Input
    ↓
[extract_with_docid.py]
    ├── Native Markdown (pymupdf4llm)
    ├── Sparse Recovery (if needed): Plain-text → OCR → VLM (Qwen2-VL)
    ├── Table Extraction (pdfplumber + Camelot fallback) 
    ├── Image Extraction (PyMuPDF)
    ├── Graph Detection (OpenCV contours)
    ├── Image Captioning (BLIP)
    └── Metadata Aggregation → metadata.json
    ↓
[RAG Pipeline]
    ├── Chunking (text, tables, figures)
    ├── Embedding (BAAI/bge-base-en-v1.5)
    └── Vector Storage (LanceDB)
    ↓
[Query Processing]
    User Query → Embedding → Hybrid Search (LanceDB) → Context Building → LLM Response
    ↓
[Streamlit UI]
    Display answer, tables, figures with source PDF links
```

## Current Limitations & Future Work
- **Graph Detection**: Contour heuristic could be replaced with ML-based detector
- **Multimodal Search**: Plan to add CLIP embeddings for direct image search
- **Advanced RAG**: Query expansion, reranking, iterative retrieval planned
- **Scalability**: Migration path to remote vector DBs (Milvus/Weaviet) for larger corpora
- **LLM Integration**: Plug-and-play support for local/open LLMs via standard APIs

## Verification Commands
```bash
# Process a document
python extraction/extract_with_docid.py data/CERN_89_12.pdf CERN_89_12

# Build search index  
python -m core.rag_pipeline ingest --doc-id CERN_89_12

# Launch UI
streamlit run app/streamlit_app.py
```

This architecture provides a robust, extensible foundation for processing technical documents while maintaining efficiency through intelligent fallback strategies and local-first model usage.