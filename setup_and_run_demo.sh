#!/bin/bash
# This script provides a complete setup for the project.
# It creates a virtual environment, installs dependencies,
# and runs the multi-document RAG example to demonstrate functionality.

set -e # Exit immediately if a command exits with a non-zero status.

VENV_DIR=".venv"
PYTHON_EXEC="python3"

echo "--- Starting Project Setup ---"

# 1. Create Virtual Environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "[1/4] Creating Python virtual environment in $VENV_DIR..."
    $PYTHON_EXEC -m venv "$VENV_DIR"
    echo "      Virtual environment created."
else
    echo "[1/4] Virtual environment already exists."
fi

# 2. Activate Virtual Environment
echo "[2/4] Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# 3. Install/Upgrade Dependencies from requirements.txt
echo "[3/4] Installing/upgrading dependencies from requirements.txt..."
pip install --upgrade pip
pip install -r requirements.txt
echo "      Dependencies are up to date."

# Check if the default PDF exists for the demo
DEFAULT_PDF="data/CERN_Yellow_Report_357576.pdf"
if [ ! -f "$DEFAULT_PDF" ]; then
    echo ""
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!! WARNING: Default demo PDF not found at '$DEFAULT_PDF'"
    echo "!! The demo may fail. Please ensure the file is available."
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo ""
fi

# 4. Run the multi-document example workflow
echo "[4/4] Running the multi-document RAG example..."
echo "      This will register, extract, ingest, and search a demo document."
echo "------------------------------------------------------------"
echo ""

python examples/multi_doc_example.py

echo ""
echo "------------------------------------------------------------"
echo "--- Demo Script Finished ---"
echo ""
echo "You can now explore the system."
echo "To run the interactive web app, use the following command:"
echo "  streamlit run app/streamlit_app.py"
echo ""
echo "To process a single PDF, use the run_pipeline.sh script:"
echo "  ./run_pipeline.sh path/to/your.pdf your_doc_id"
echo "--- Setup Complete ---"