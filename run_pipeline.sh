#!/bin/bash

# Activate the virtual environment explicitly to avoid (base) conda conflicts
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
else
    echo "Warning: virtual environment not found at .venv/. Please run the setup script first."
fi

# Ensure all dependencies are installed from the central requirements file.
echo "Ensuring dependencies are installed..."
pip install -r requirements.txt

# Check for required arguments
if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <pdf_path> <doc_id> [--force]"
    echo "Example: $0 data/9004018.pdf 9004018"
    exit 1
fi

# Run the document extraction pipeline
echo "Running VLM extraction pipeline..."
python extraction/extract_with_docid.py "$@"
