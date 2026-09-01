#!/usr/bin/env bash
# ------------------------------------------------------------
# run_all.sh – one‑stop script for the Cern‑Multimodel‑RAG project
# ------------------------------------------------------------
# Usage:
#   ./run_all.sh <pdf_path> <doc_id> [--force]
# Example:
#   ./run_all.sh data/9004018.pdf 9004018 --force
# ------------------------------------------------------------
set -euo pipefail

# 1️⃣ Activate virtual environment (creates it if missing)
if [ ! -d ".venv" ]; then
  echo "[1/5] Creating virtual environment…"
  python3 -m venv .venv
fi

# Activate
source .venv/bin/activate
echo "✅ Activated .venv (Python $(python --version))"

# 2️⃣ Install / upgrade dependencies (idempotent)
echo "[2/5] Installing/upgrading dependencies…"
pip install --upgrade pip
pip install -r requirements.txt

# 3️⃣ Run the extraction pipeline (requires PDF path & doc_id)
if [ "$#" -lt 2 ]; then
  echo "[ERROR] Missing arguments."
  echo "Usage: $0 <pdf_path> <doc_id> [--force]"
  exit 1
fi
PDF_PATH=$1
DOC_ID=$2
SHIFTED_ARGS="${@:3}"   # any extra flags like --force

echo "[3/5] Running extraction on $PDF_PATH (doc_id=$DOC_ID)…"
python extraction/extract_with_docid.py "$PDF_PATH" "$DOC_ID" $SHIFTED_ARGS

# 4️⃣ Ingest the newly extracted document into the vector store
# (optional – uncomment if you want automatic ingestion)
# echo "[4/5] Ingesting document into LanceDB…"
# python -c "from core.rag_pipeline import RAGPipeline; RAGPipeline().ingest_document('outputs/$DOC_ID')"

# 5️⃣ Launch the Streamlit UI (exposes the RAG demo)
# The UI will be reachable at http://localhost:8501
echo "[5/5] Starting Streamlit UI…"
streamlit run app/streamlit_app.py --server.address 0.0.0.0 --server.port 8501

# End of script – when you stop Streamlit (Ctrl+C) the script exits.
