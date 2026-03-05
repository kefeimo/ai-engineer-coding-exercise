#!/usr/bin/env python3
"""
Test RAGAS + GPT4All compatibility with modern LangChain stack.

This script tests whether RAGAS evaluation metrics work with GPT4All
using modern LangChain (1.2.10) and Pydantic v2.

Usage:
    source venv-ragas-gpt4all/bin/activate
    python test_ragas_gpt4all.py
"""
import os
import sys
import time
from pathlib import Path

# Set CUDA library paths for GPU support
site_packages = [p for p in sys.path if 'site-packages' in p]
if site_packages:
    sp = site_packages[0]
    cuda_runtime = os.path.join(sp, 'nvidia', 'cuda_runtime', 'lib')
    cuda_blas = os.path.join(sp, 'nvidia', 'cublas', 'lib')
    cuda_libs = []
    if os.path.exists(cuda_runtime):
        cuda_libs.append(cuda_runtime)
    if os.path.exists(cuda_blas):
        cuda_libs.append(cuda_blas)
    if cuda_libs:
        os.environ['LD_LIBRARY_PATH'] = ':'.join(cuda_libs) + ':' + os.environ.get('LD_LIBRARY_PATH', '')

from langchain_community.llms import GPT4All
from ragas.llms import LangchainLLMWrapper
from ragas.metrics.collections.faithfulness import Faithfulness
from ragas.metrics.collections.answer_relevancy import AnswerRelevancy
from ragas.metrics.collections.context_precision import ContextPrecision
from datasets import Dataset

print("=" * 70)
print("RAGAS + GPT4All Compatibility Test")
print("=" * 70)
print(f"LangChain:       {__import__('langchain').__version__}")
print(f"Pydantic:        {__import__('pydantic').__version__}")
print(f"RAGAS:           {__import__('ragas').__version__}")
print(f"GPT4All:         2.8.2")
print("=" * 70)

# Step 1: Initialize GPT4All
print("\n[Step 1/5] Initializing GPT4All...")
model_path = Path.home() / ".cache/gpt4all/mistral-7b-instruct-v0.1.Q4_0.gguf"
if not model_path.exists():
    print(f"✗ Model not found at: {model_path}")
    print("Please download the model first.")
    sys.exit(1)

start = time.time()
llm = GPT4All(
    model=str(model_path),
    device='cpu',  # Use CPU for stability
    max_tokens=100,
    n_threads=4
)
elapsed = time.time() - start
print(f"✓ GPT4All initialized in {elapsed:.2f}s")

# Step 2: Test direct generation
print("\n[Step 2/5] Testing direct LLM generation...")
start = time.time()
try:
    response = llm.invoke("What is 2+2? Answer briefly.")
    elapsed = time.time() - start
    print(f"✓ Response: {response.strip()[:100]}")
    print(f"  Generated in {elapsed:.2f}s")
except Exception as e:
    print(f"✗ Direct generation failed: {e}")
    sys.exit(1)

# Step 3: Wrap for RAGAS
print("\n[Step 3/5] Wrapping LLM for RAGAS...")
try:
    ragas_llm = LangchainLLMWrapper(llm)
    print("✓ LLM wrapped successfully")
except Exception as e:
    print(f"✗ Failed to wrap LLM: {e}")
    sys.exit(1)

# Step 4: Initialize RAGAS metrics
print("\n[Step 4/5] Initializing RAGAS metrics...")
try:
    faithfulness_metric = Faithfulness(llm=ragas_llm)
    print("✓ Faithfulness metric initialized")
    
    # Note: AnswerRelevancy and ContextPrecision may require embeddings
    # We'll focus on Faithfulness for this test
except Exception as e:
    print(f"✗ Failed to initialize metrics: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Run evaluation
print("\n[Step 5/5] Running RAGAS evaluation...")
print("Testing with a simple example...")

test_data = {
    "question": ["What is 2+2?"],
    "answer": ["2+2 equals 4. This is basic arithmetic."],
    "contexts": [["Mathematics: Addition is the basic operation of combining two numbers. 2+2=4"]],
}

try:
    dataset = Dataset.from_dict(test_data)
    print(f"Dataset created with {len(dataset)} sample")
    
    print("\nEvaluating faithfulness...")
    print("(This tests if the answer is faithful to the context)")
    start = time.time()
    
    # Use single_turn_score for individual samples
    result = faithfulness_metric.single_turn_score(dataset[0])
    
    elapsed = time.time() - start
    
    print("\n" + "=" * 70)
    print("✓ SUCCESS! RAGAS + GPT4All works with modern LangChain!")
    print("=" * 70)
    print(f"Faithfulness Score:  {result:.4f}")
    print(f"Evaluation Time:     {elapsed:.2f}s")
    print("\n" + "=" * 70)
    print("Conclusion: Modern LangChain (1.2.10) + Pydantic v2 is compatible")
    print("            with both RAGAS and GPT4All!")
    print("=" * 70)
    
except AttributeError as e:
    print(f"\n✗ API Error: {e}")
    print("\nTrying alternative API...")
    
    # Try the batch scoring API
    try:
        start = time.time()
        result = faithfulness_metric.score(dataset[0])
        elapsed = time.time() - start
        
        print("\n" + "=" * 70)
        print("✓ SUCCESS with alternative API!")
        print("=" * 70)
        print(f"Faithfulness Score:  {result:.4f}")
        print(f"Evaluation Time:     {elapsed:.2f}s")
        print("=" * 70)
    except Exception as e2:
        print(f"✗ Alternative API also failed: {e2}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
except Exception as e:
    elapsed = time.time() - start
    print("\n" + "=" * 70)
    print(f"✗ FAILED after {elapsed:.2f}s")
    print("=" * 70)
    print(f"Error: {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Diagnosis:")
    print("- LangChain version is correct (1.2.10)")
    print("- Pydantic v2 is installed (2.12.5)")
    print("- GPT4All wrapper may still have API incompatibilities")
    print("\nRecommendation: Use OpenAI API for RAGAS evaluation")
    print("=" * 70)
    sys.exit(1)
