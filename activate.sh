#!/bin/bash
# Source this file to activate the project virtual environment.
# Usage: source activate.sh

VENV_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "❌ Virtual environment not found at $VENV_DIR"
    echo "   Run: python3 -m venv .venv && pip install -r requirements.txt"
    return 1
fi

source "$VENV_DIR/bin/activate"
echo "✅ Virtual environment activated: $(python --version)"
echo "   Interpreter: $(which python)"
