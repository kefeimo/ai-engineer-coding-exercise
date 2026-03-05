#!/bin/bash
# Setup script for RAGAS evaluation environment
# This creates a separate environment to avoid conflicts with the main backend

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=================================================="
echo "Setting up RAGAS Evaluation Environment"
echo "=================================================="

# Check if venv-eval exists
if [ -d "venv-eval" ]; then
    echo "✓ Virtual environment already exists: venv-eval/"
else
    echo "[1/3] Creating virtual environment..."
    python -m venv venv-eval
    echo "✓ Created venv-eval/"
fi

echo ""
echo "[2/3] Installing dependencies..."
source venv-eval/bin/activate
pip install --upgrade pip -q
pip install -r requirements-eval.txt

echo ""
echo "[3/3] Verifying installation..."
python -c "
from ragas import evaluate
from ragas.metrics.collections import context_precision, faithfulness, answer_relevancy
from datasets import Dataset
import openai
import requests
print('✓ All packages installed successfully!')
print(f'  - RAGAS: {__import__(\"ragas\").__version__}')
print(f'  - OpenAI: {openai.__version__}')
print(f'  - Requests: {requests.__version__}')
"

echo ""
echo "=================================================="
echo "✓ Setup complete!"
echo "=================================================="
echo ""
echo "To use the evaluation environment:"
echo "  1. Activate: source venv-eval/bin/activate"
echo "  2. Set API key: export OPENAI_API_KEY='your-key-here'"
echo "  3. Run evaluation: python run_ragas_baseline.py"
echo ""
echo "Deactivate when done: deactivate"
echo "=================================================="
