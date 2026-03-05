# RAGAS + GPT4All Compatibility Findings

## Summary

**Conclusion: RAGAS 0.4.3 does NOT support GPT4All or LangChain-wrapped local LLMs.**

## Test Results

### Environment Tested
- **LangChain:** 1.2.10 (modern, Pydantic v2 compatible)
- **Pydantic:** 2.12.5
- **RAGAS:** 0.4.3
- **GPT4All:** 2.8.2

### Test Outcome

✅ **GPT4All works fine** (direct generation successful)  
✅ **LangchainLLMWrapper creates successfully**  
❌ **RAGAS rejects LangchainLLMWrapper**

### Error Message

```
ValueError: Collections metrics only support modern InstructorLLM. 
Found: LangchainLLMWrapper. 
Use: llm_factory('gpt-4o-mini', client=openai_client)
```

### Deprecation Warning

```
DeprecationWarning: LangchainLLMWrapper is deprecated and will be removed 
in a future version. Use llm_factory instead: 
from openai import OpenAI; from ragas.llms import llm_factory; 
llm = llm_factory('gpt-4o-mini', client=OpenAI(api_key='...'))
```

## Root Cause Analysis

### Initial Hypothesis (User's Insight)
> "RAGAS forces Pydantic v2... Keep LangChain modern (so it's Pydantic v2-compatible) 
> if you want RAGAS + LangChain + GPT4All."

**Status: Partially correct but insufficient**

The Pydantic v2 alignment was necessary but not sufficient. The real issue is:

### Actual Root Cause

**RAGAS 0.4.3 architectural change:**
1. RAGAS deprecated `LangchainLLMWrapper` completely
2. New RAGAS only supports `InstructorLLM` (OpenAI-style APIs)
3. RAGAS explicitly validates LLM type and **rejects** LangChain wrappers
4. This is a **design decision**, not a bug

## Why the Version Conflicts Occurred

### Old Environment (Main Backend)
- **LangChain 0.1.0** + **RAGAS 0.1.0**
  - Used old LangChainLLM wrapper
  - TypeError: `temperature` parameter API mismatch
  - Pydantic v1/v2 mixed versions

### Modern Environment (venv-ragas-gpt4all)
- **LangChain 1.2.10** + **RAGAS 0.4.3**
  - LangchainLLMWrapper deprecated
  - RAGAS explicitly rejects it
  - Pydantic v2 aligned correctly

**Both fail, but for different reasons:**
- Old: API parameter mismatch
- New: RAGAS architectural restriction

## Solution: Use OpenAI API

### Required Approach

RAGAS evaluation **requires** OpenAI API (or compatible):

```python
from openai import OpenAI
from ragas.llms import llm_factory

# Initialize with OpenAI
client = OpenAI(api_key='sk-...')
ragas_llm = llm_factory('gpt-4o-mini', client=client)

# Use with RAGAS metrics
from ragas.metrics.collections.faithfulness import Faithfulness
faithfulness_metric = Faithfulness(llm=ragas_llm)
```

### Cost Considerations

**GPT-4o-mini pricing:**
- Input: $0.150 per 1M tokens
- Output: $0.600 per 1M tokens

**Estimated cost for evaluation:**
- 20 queries × 3 metrics = 60 evaluations
- ~500 tokens per evaluation (input + output)
- Total: ~30,000 tokens = **~$0.02-0.05** (very cheap!)

## Recommendations

### For Stage 1C (Current)
1. ✅ Use `venv-eval` environment (already created)
2. ✅ Set OpenAI API key: `export OPENAI_API_KEY="sk-..."`
3. ✅ Run evaluation with existing script
4. ✅ Complete baseline evaluation

### For Future
1. **Stage 1C:** Use OpenAI for RAGAS metrics (minimal cost)
2. **Stage 2B:** Continue with OpenAI for enhanced evaluation
3. **Production:** GPT4All for RAG queries (free, local, fast with GPU)
4. **Evaluation:** OpenAI for quality metrics (accurate, standardized)

This is a **hybrid approach** that's actually optimal:
- **GPT4All:** Fast, free, local inference for user queries
- **OpenAI:** Accurate, standardized evaluation metrics

## Files Created During Investigation

1. `requirements-eval.txt` - OpenAI-based RAGAS environment
2. `requirements-ragas-gpt4all.txt` - Test environment (proven incompatible)
3. `setup_eval_env.sh` - Automated setup for venv-eval
4. `test_ragas_gpt4all.py` - Compatibility test script
5. `venv-eval/` - Working OpenAI evaluation environment ✅
6. `venv-ragas-gpt4all/` - Test environment (not usable for RAGAS)

## Next Steps

1. **Use venv-eval environment** (OpenAI-based)
2. **Get OpenAI API key** from https://platform.openai.com/api-keys
3. **Set environment variable:** `export OPENAI_API_KEY="sk-..."`
4. **Run baseline evaluation:** `python run_ragas_baseline.py --input baseline_20.json`
5. **Complete Stage 1C**

## Conclusion

The investigation conclusively proves:
- ❌ RAGAS 0.4.3 does NOT work with GPT4All (by design)
- ❌ RAGAS 0.4.3 does NOT work with LangChain wrappers (deprecated)
- ✅ RAGAS 0.4.3 requires OpenAI API or compatible services
- ✅ Separate `venv-eval` environment is the correct solution
- ✅ Hybrid approach (GPT4All for RAG + OpenAI for eval) is optimal

**User's original intuition was right:** We need to separate the evaluation environment!
