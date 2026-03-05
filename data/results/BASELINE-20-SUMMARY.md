# Baseline 20-Query RAGAS Evaluation Summary

**Date:** March 5, 2026  
**Evaluation Timestamp:** 2026-03-05 09:19:22  
**Query Timestamp:** 2026-03-05 09:14:06

## Overview

Completed full 3-stage RAGAS evaluation on 20 baseline queries covering FastAPI documentation.

### Dataset Composition
- **Total Queries:** 20
- **Successful Queries:** 20 (100%)
- **Failed Queries:** 0
- **Difficulty Breakdown:**
  - Easy: 6 queries (basics, installation, setup)
  - Medium: 10 queries (features, validation, middleware, dependencies)
  - Hard: 4 queries (authentication, best practices, performance, structure)

## Aggregated Metrics

| Metric | Mean | Min | Max | Count |
|--------|------|-----|-----|-------|
| **Faithfulness** | 0.634 | 0.0 | 1.0 | 20 |
| **Answer Relevancy** | 0.772 | 0.0 | 1.0 | 20 |
| **Context Precision** | 0.948 | 0.0 | 1.0 | 20 |
| **Context Recall** | N/A* | 0.125 | 1.0 | 20 |
| **Context Entity Recall** | 0.519 | 0.0 | 1.0 | 20 |

*Note: Context Recall mean shows NaN due to empty reference in one query (ASGI - no context retrieved)

## Key Findings

### ✅ Strengths
1. **Excellent Retrieval Quality (Context Precision: 0.948)**
   - RAG system retrieving highly relevant chunks
   - Top-k selection working well
   - Very few irrelevant documents in results

2. **High Answer Relevancy (0.772)**
   - Answers generally address the questions asked
   - Good query understanding

### ⚠️ Areas for Improvement

1. **Faithfulness Issues (0.634 - BELOW 0.7 THRESHOLD)**
   - **Critical:** Multiple queries with faithfulness = 0.0
   - System making claims beyond retrieved context
   - Hallucination detected (similar to 3-query test)
   - **Action Required:** Implement Option A (Prompt Engineering) from planning
     - Migrate to LangChain PromptTemplate
     - Add few-shot examples
     - Strengthen "DO NOT infer" rules

2. **Moderate Entity Recall (0.519)**
   - Only capturing ~50% of important entities
   - May need entity-aware retrieval

3. **Some Queries with Zero Scores**
   - Several queries scored 0.0 across metrics
   - Need investigation (Query 4: ASGI had no contexts)

## Distribution Analysis (Planned for Stage 2B Hour 12)

Enhanced analytics will include:
- Percentile calculations (P10, P25, P75, P90)
- Bad case rate (queries <0.4 threshold)
- Failure categorization (retrieval, hallucination, ambiguous)
- Worst 5-10 cases per metric identification

## Next Steps

### Immediate (Stage 2B Hour 12-13)
1. ✅ Create `run_ragas_analysis.py` with enhanced statistics
2. ✅ Identify worst-performing queries
3. ✅ Categorize failure patterns
4. ✅ Implement targeted improvements based on faithfulness <0.7

### Priority Improvements
- **Option A (Prompt Engineering):** Address faithfulness issues
- **Monitor:** Track bad_case_rate after improvements
- **Re-evaluate:** Run same 20 queries after improvements

## CI/CD Gates (Proposed)

Based on industry best practices:
- ✅ **Context Precision > 0.75:** PASSED (0.948)
- ❌ **Faithfulness > 0.75:** FAILED (0.634)
- ✅ **Answer Relevancy > 0.70:** PASSED (0.772)
- ⚠️ **Bad Case Rate < 10%:** TO BE CALCULATED

## Cost & Performance

- **OpenAI API Cost:** ~$1.00 (reference generation + evaluation)
- **Total Time:** ~15 minutes
- **Backend Query Time:** ~5 minutes (Stage 1A)
- **Reference Generation:** ~3 minutes (Stage 1B)
- **RAGAS Evaluation:** ~1 minute (Stage 2)

## Files Generated

1. `baseline_20_stage1.json` - RAG query results
2. `baseline_20_with_refs.json` - Results with ground truth references
3. `baseline_20_full_eval.json` - Complete evaluation with all 5 metrics
4. `BASELINE-20-SUMMARY.md` - This summary (for quick reference)

---

**Conclusion:** Retrieval quality excellent (0.948), but faithfulness issues (0.634) require immediate attention through prompt engineering improvements. System ready for Stage 2B improvement iteration.
