#!/usr/bin/env python3
"""Test RAGAS 0.2.x with GPT4All using parameter filtering"""
import os
import sys
import time
from typing import Any, Dict, List, Optional

# Set CUDA library paths
site_packages = [p for p in sys.path if 'site-packages' in p]
if site_packages:
    sp = site_packages[0]
    cuda_runtime = os.path.join(sp, 'nvidia', 'cuda_runtime', 'lib')
    cuda_blas = os.path.join(sp, 'nvidia', 'cublas', 'lib')
    cuda_libs = []
    if os.path.exists(cuda_runtime): cuda_libs.append(cuda_runtime)
    if os.path.exists(cuda_blas): cuda_libs.append(cuda_blas)
    if cuda_libs:
        os.environ['LD_LIBRARY_PATH'] = ':'.join(cuda_libs) + ':' + os.environ.get('LD_LIBRARY_PATH', '')

from langchain_community.llms import GPT4All
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

# Create a wrapper that filters out invalid parameters
class GPT4AllFixed(GPT4All):
    """GPT4All wrapper that filters out 'temperature' parameter"""
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        # Filter out 'temperature' and convert it to 'temp' if present
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key == 'temperature':
                # Convert 'temperature' to 'temp' (GPT4All's parameter name)
                filtered_kwargs['temp'] = value
                print(f"  [FIX] Converted 'temperature' to 'temp': {value}")
            elif key != 'temperature':
                filtered_kwargs[key] = value
        
        # Call parent with filtered kwargs
        return super()._call(prompt, stop=stop, run_manager=run_manager, **filtered_kwargs)

from ragas.llms import LangchainLLMWrapper
from ragas.metrics import faithfulness
from datasets import Dataset

print("=" * 60)
print("Test: RAGAS 0.2.x + GPT4All with parameter filtering")
print("=" * 60)
print(f"RAGAS: 0.2.15")
print(f"LangChain: 1.2.10")
print(f"Pydantic: 2.12.5")
print(f"GPT4All: 2.8.2 (with temperature→temp fix)")
print("=" * 60)

print("\n[1/4] Initializing GPT4All (CPU mode for test)...")
start = time.time()
llm = GPT4AllFixed(
    model="/home/kefei/.cache/gpt4all/mistral-7b-instruct-v0.1.Q4_0.gguf",
    device='cpu',
    max_tokens=100
)
print(f"✓ Initialized in {time.time() - start:.2f}s")

print("\n[2/4] Testing direct generation...")
start = time.time()
response = llm.invoke("What is 2+2?")
print(f"Response: {response.strip()}")
print(f"✓ Generated in {time.time() - start:.2f}s")

print("\n[3/4] Wrapping for RAGAS with LangchainLLMWrapper...")
try:
    ragas_llm = LangchainLLMWrapper(llm)
    faithfulness.llm = ragas_llm
    print(f"✓ Wrapped successfully")
    print(f"  Wrapper type: {type(ragas_llm)}")
except Exception as e:
    print(f"✗ Failed to wrap: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[4/4] Running RAGAS faithfulness metric...")
# RAGAS 0.2.x field names
test_data = {
    "user_input": "What is 2+2?",
    "response": "2+2 equals 4.",
    "retrieved_contexts": ["Basic math: 2+2=4"],
}

print("(Timeout after 180s - this may take a while)")
start = time.time()
try:
    import warnings
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    result = faithfulness.score(test_data)
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"✓ SUCCESS! RAGAS 0.2.x + GPT4All works with fix!")
    print(f"{'=' * 60}")
    print(f"Faithfulness Score: {result}")
    print(f"Evaluation Time: {elapsed:.2f}s")
    print(f"\n🎉 BREAKTHROUGH: temperature parameter fix works!")
    print(f"   GPT4All CAN work with RAGAS using parameter filtering!")
    print(f"{'=' * 60}")
except Exception as e:
    elapsed = time.time() - start
    print(f"\n{'=' * 60}")
    print(f"✗ FAILED after {elapsed:.2f}s")
    print(f"{'=' * 60}")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
