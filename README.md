# CERN Multimodal RAG (Local LanceDB Version)

This project is a **multimodal RAG prototype** for CERN PDFs:

- Extracts **text** and **images** from PDFs using PyMuPDF
- Uses **BLIP** to caption figures
- Chunks text + figure captions
- Embeds chunks with **SentenceTransformer** (`all-MiniLM-L6-v2`)
- Stores vectors locally in **LanceDB**
- Exposes a **Streamlit** UI to ingest PDFs and run semantic search

## Project Structure

```text
cern-multimodel-rag/
├── app/
│   ├── streamlit_app.py
│   ├── __init__.py
│   └── ui_components/
│       └── __init__.py
├── core/
│   ├── config.py
│   ├── pdf_loader.py
│   ├── image_captioner.py
│   ├── chunker.py
│   ├── embedder.py
│   ├── vector_store_lance.py
│   └── rag_pipeline.py
├── data/
│   └── CERN_Yellow_Report_357576.pdf
├── uploads/
├── lancedb/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── scripts/
│   ├── test_lancedb.py
│   ├── test_pdf_extract.py
│   ├── test_embeddings.py
│   ├── clean_env.sh
│   └── debug_env.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md

## Getting Started

1. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Processing Remote PDFs or Web Pages**

   You don’t have to manually download a PDF first.  Give the project any
   URL that either directly points to a `.pdf` file or wraps it (e.g. a CERN
   record page), and the system will handle the rest.

   The entry point is `core.DocumentManager.add_remote_pdf(url, doc_id)`;
   calling this method will:
   1. hit the URL,
   2. if the response isn’t a PDF, scan the HTML for the first link ending in
      `.pdf` or containing `/files/`,
   3. download the resolved PDF,
   4. register it in `data/documents.json`.

   Once registered you can run extraction and ingestion exactly as in the
   examples:
   ```python
   from core.document_manager import DocumentManager
   from core.rag_pipeline import RAGPipeline

   url = "https://cds.cern.ch/record/205520?ln=en"
   doc_id = "cern_205520"

   pdf_path = DocumentManager().add_remote_pdf(url, doc_id)
   # …then run extraction/ingest as shown in examples/multi_doc_example.py

   pipeline = RAGPipeline()
   pipeline.ingest_from_doc_id_output(doc_id)
   results = pipeline.search("your query", top_k=5, doc_id=doc_id)
   ```

   In short: **just paste the link wherever you call `add_remote_pdf`** and the
   rest of the pipeline will automatically integrate, extract and index the
   document so it can answer your future queries.

### Using the Streamlit UI

Run the app with `streamlit run app/streamlit_app.py` (the server is already
running in your workspace).  The left‑hand sidebar now includes a simple form
for registering documents:

1. **Paste a URL** (direct PDF or landing page) or **upload a PDF file**.
2. Optionally provide a `Doc ID` – otherwise the filename/stem is used.
3. Click **Download/Register**.  The document will be saved under `data/` and
   recorded in `data/documents.json`.
4. A new button **Extract & Ingest last doc** appears once a document is
   registered.  Clicking it runs the full extraction + LanceDB ingestion
   pipeline.  (Progress is shown in a spinner and status message.)

After ingestion you can simply chat with the model in the main panel; the
search is automatically scoped to all indexed documents (or you can filter by
`doc_id` via code if you prefer).

The UI thus eliminates any need to manually edit files: just paste the link or
upload a PDF and use the buttons.  You can still script things by editing
`examples/multi_doc_example.py` if you want batch processing, but the
interactive sidebar covers the common case.
