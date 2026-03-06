# RAG System Evaluation

This directory contains evaluation scripts and test datasets for the RAG system.

## Overview

The evaluation framework uses **RAGAS** (Retrieval-Augmented Generation Assessment) metrics to evaluate the quality of the RAG system's responses.

**Important:** RAGAS **requires OpenAI API** - local models like GPT4All are **not compatible**.

### Why OpenAI API is Required

After extensive testing (see `RAGAS-GPT4ALL-INVESTIGATION.md`), we confirmed:
- ❌ **RAGAS 0.4.x:** Explicitly requires OpenAI-like API (deprecated LangchainLLMWrapper)
- ❌ **RAGAS 0.1.x-0.3.x:** LangChain's GPT4All wrapper has API incompatibility (`temperature` parameter error)
- ✅ **Solution:** Use OpenAI API for evaluation (cost: ~$0.50-$1.00 for 20 queries)

**Hybrid Architecture:**
- 🚀 **GPT4All for production queries:** Fast, local, GPU-accelerated, free (12-15s per query)
- 📊 **OpenAI for evaluation metrics:** Reliable, accurate, one-time cost (~$1 for full evaluation)

## Architecture

```
backend/
├── app/                    # Main RAG backend (FastAPI + GPT4All + ChromaDB)
│   └── venv/              # Main backend dependencies
└── evaluation/            # Separate evaluation environment
    ├── venv-eval/         # RAGAS evaluation dependencies (separate!)
    ├── requirements-eval.txt
    ├── setup_eval_env.sh  # One-command setup
    └── run_ragas_baseline.py
```

**Why separate environments?**
- **Main backend:** GPT4All for fast, local GPU inference (free, 12-15s per query)
- **RAGAS evaluation:** Requires OpenAI API (RAGAS 0.4.3 only supports InstructorLLM, not LangChain wrappers)
- **Architecture change:** RAGAS deprecated LangchainLLMWrapper in version 0.4.3
- **Cost:** OpenAI GPT-4o-mini is very cheap (~$0.02-0.05 for full 20-query evaluation)
- **Solution:** Hybrid approach - GPT4All for production, OpenAI for evaluation

## Quick Start

### 1. Setup Evaluation Environment (One-Time)

```bash
cd backend/evaluation
./setup_eval_env.sh
```

This creates `venv-eval/` with minimal dependencies: RAGAS, OpenAI, requests, datasets.

### 2. Run Evaluation (Query Results Only)

Without an OpenAI API key, the script will run all queries and save results:

```bash
source venv-eval/bin/activate
python run_ragas_baseline.py --input ../../data/test_queries/baseline_3.json
```

This will:
- ✅ Run all test queries through the RAG system
- ✅ Collect answers, contexts, and metadata
- ✅ Save results to JSON file
- ⚠️ Skip RAGAS metric calculation (requires OpenAI API)

### 3. Run Full RAGAS Evaluation (Recommended)

For complete evaluation with quality metrics:

```bash
source venv-eval/bin/activate

# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-api-key-here"

# Run evaluation
python run_ragas_baseline.py --input ../../data/test_queries/baseline_20.json
```

This will:
- ✅ Run all test queries
- ✅ Calculate RAGAS metrics (context_precision, faithfulness, answer_relevancy)
- ✅ Generate comprehensive evaluation report

**Expected time:** ~2-5 minutes for 20 queries with OpenAI API

**When done:**
```bash
deactivate  # Exit evaluation environment
```

## RAGAS Metrics Explained

### 1. Context Precision
- **Measures:** How relevant are the retrieved document chunks?
- **Range:** 0.0 - 1.0 (higher is better)
- **Interpretation:**
  - 0.8+ : Excellent retrieval, highly relevant contexts
  - 0.6-0.8 : Good retrieval, mostly relevant
  - <0.6 : Poor retrieval, many irrelevant chunks

### 2. Faithfulness
- **Measures:** Is the answer grounded in the retrieved contexts?
- **Range:** 0.0 - 1.0 (higher is better)
- **Interpretation:**
  - 0.9+ : Answer fully supported by contexts
  - 0.7-0.9 : Mostly faithful with minor additions
  - <0.7 : Contains hallucinations or unsupported claims

### 3. Answer Relevancy
- **Measures:** Does the answer address the question?
- **Range:** 0.0 - 1.0 (higher is better)
- **Interpretation:**
  - 0.8+ : Answer directly addresses question
  - 0.6-0.8 : Answer is relevant but could be more focused
  - <0.6 : Answer misses key aspects of the question

## Configuration Options

### Option 1: OpenAI API (Recommended)

**Pros:**
- ✅ Fast (1-2 seconds per query)
- ✅ Reliable and accurate metrics
- ✅ Standard RAGAS configuration
- ✅ Well-tested and documented

**Cons:**
- ❌ Requires API key (paid service)
- ❌ Sends data to external service

**Setup:**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

**Cost:** OpenAI API pricing:
- GPT-3.5-turbo: ~$0.002 per query
- 20 queries: ~$0.04
- Negligible for evaluation purposes

### Option 2: Local LLM (Not Compatible)

**Status:** ❌ **Not compatible with RAGAS due to version conflicts**

**What we discovered:**
1. ✅ GPT4All works perfectly standalone (0.4s generation, GPU accelerated)
2. ❌ **Version conflict when using GPT4All with RAGAS:**
   ```
   TypeError: GPT4All.generate() got an unexpected keyword argument 'temperature'
   ```

**Root cause - Dependency conflict:**
- **Main backend:** Uses `langchain 0.1.0` + `langchain-community 0.0.13` (compatible with `gpt4all 2.8.2`)
- **RAGAS 0.4.3:** Requires `langchain 1.2.10` + `langchain-community 0.4.1` (incompatible with GPT4All)
- LangChain's GPT4All wrapper changed its API between versions
- RAGAS passes parameters that newer GPT4All doesn't accept
- Tested: Even after 60s timeout, evaluation fails with TypeError

**Solution: Separate Environments**
- **Main backend (`venv/`):** GPT4All + older LangChain → Fast GPU inference
- **Evaluation (`venv-eval/`):** RAGAS + OpenAI → Reliable evaluation
- No version conflicts, each optimized for its purpose

**Why not just upgrade LangChain in main backend?**
- Would break GPT4All GPU acceleration
- Main backend needs to be stable and fast
- Evaluation is separate concern
- OpenAI API is industry standard for RAGAS anyway

**Recommendation:** Use separate evaluation environment with OpenAI API (fast, cheap, reliable).

## Test Datasets

### baseline_3.json
- **Purpose:** Quick smoke test
- **Queries:** 3 (1 easy, 1 medium, 1 hard)
- **Use case:** Verify system works before full evaluation
- **Time:** ~30 seconds (without RAGAS), ~10 seconds (with OpenAI)

### baseline_20.json
- **Purpose:** Comprehensive baseline evaluation
- **Queries:** 20 (6 easy, 10 medium, 4 hard)
- **Categories:** basics, routing, validation, security, deployment, etc.
- **Use case:** Full system evaluation, benchmark for improvements
- **Time:** ~5 minutes (without RAGAS), ~2 minutes (with OpenAI)

## Command-Line Options

```bash
python evaluation/run_ragas_baseline.py [OPTIONS]

Options:
  --input PATH   Path to test queries JSON file (default: ../data/test_queries/baseline_20.json)
  --output PATH  Path to save results JSON file (default: ../data/results/baseline_ragas_results.json)

Examples:
  # Run 3-query smoke test
  python evaluation/run_ragas_baseline.py --input ../data/test_queries/baseline_3.json
  
  # Run full 20-query evaluation
  python evaluation/run_ragas_baseline.py --input ../data/test_queries/baseline_20.json
  
  # Custom output location
  python evaluation/run_ragas_baseline.py --output ../data/results/my_results.json
```

## Output Format

The evaluation script generates a JSON file with:

### With RAGAS metrics:
```json
{
  "test_name": "RAGAS Baseline Evaluation",
  "timestamp": "2024-03-05 10:30:00",
  "test_results": {
    "total_queries": 20,
    "successful_queries": 20,
    "failed_queries": 0
  },
  "ragas_scores": {
    "context_precision": 0.82,
    "faithfulness": 0.89,
    "answer_relevancy": 0.85
  },
  "per_query_metrics": [...]
}
```

### Without RAGAS metrics (query results only):
```json
{
  "test_name": "RAG Query Evaluation (RAGAS metrics skipped)",
  "timestamp": "2024-03-05 10:30:00",
  "status": "queries_complete_ragas_skipped",
  "note": "RAGAS evaluation requires OpenAI API key",
  "test_results": {
    "total_queries": 20,
    "successful_queries": 20,
    "failed_queries": 0
  },
  "query_results": [
    {
      "id": 1,
      "query": "What is FastAPI?",
      "difficulty": "easy",
      "category": "basics",
      "answer": "FastAPI is a modern, fast (high-performance), web framework...",
      "contexts_count": 5,
      "expected_aspects": ["web framework", "Python", "API"]
    },
    ...
  ]
}
```

## Troubleshooting

### "RAGAS evaluation skipped"
- **Cause:** No OpenAI API key found
- **Solution:** Set `OPENAI_API_KEY` environment variable or accept query-only results

### Slow evaluation with local LLM
- **Cause:** GPT4All/local LLM inference is CPU/GPU intensive
- **Solution:** Use OpenAI API for faster evaluation

### "Collection not initialized" error
- **Cause:** ChromaDB not set up
- **Solution:** Run document ingestion first:
  ```bash
  curl -X POST http://localhost:8000/api/v1/ingest \
       -H "Content-Type: application/json" \
       -d '{"document_path": "../data/documents"}'
  ```

## Next Steps

See `docs/EVALUATION-REPORT.md` for baseline results and analysis.
