# TODO — Confidence Naming Refactoring

## The Problem

The term `confidence` is used throughout the codebase and UI, but it is **not** answer-level confidence. It is a **retrieval relevance score** — a measure of how closely the retrieved chunks match the query, computed before the LLM ever runs.

### What it actually is

```
confidence = 1.0 - (cosine_distance / 2.0)
           = average across top-k retrieved chunks
           = computed from ChromaDB distances, before generation
```

This measures **query-chunk similarity in embedding space**. It answers: "how relevant are the retrieved documents to the question?" — not "how correct or trustworthy is the generated answer?"

### Why the distinction matters

| | What this codebase calls "confidence" | True answer-level confidence |
|---|---|---|
| Computed | Before LLM is called | After generation |
| Measures | Retrieval relevance (chunk ↔ query similarity) | Answer correctness / faithfulness |
| Used for | Gating: reject query if retrieval too weak | Telling the user how much to trust the answer |
| Influenced by | Embedding quality, chunk content, query wording | LLM reasoning, context faithfulness, factual accuracy |

> *"confidence is retrieval relevance score, and we cannot get answer-level confidence without using another LLM to evaluate"*

To compute a true answer-level confidence you would need one of:
- Ask the LLM to self-assess (unreliable; LLMs are poorly calibrated)
- Run a RAGAS `faithfulness` check post-generation (requires a second LLM call)
- Use a cross-encoder to score (answer, context) similarity

None of these are implemented. This project has a RAGAS evaluation pipeline (`evaluation/`), but that runs offline against a test set — not at request time.

### The existing inconsistency in the frontend

The frontend already uses two different labels for the same number — one correct, one not:

| Component | Label used | Accurate? |
|---|---|---|
| `SourceCard.jsx` | "High/Medium/Low **Relevance**" (per-chunk score) | ✅ correct |
| `ResponseDisplay.jsx` | "High/Medium/Low **Confidence**" (overall score) | ❌ misleading |
| `App.jsx` history list | raw `%` number, no label | neutral |

---

## Clarifications Needed Before Implementation

Before starting, these decisions need to be made:

**1. What is the new JSON field name?**
The API response currently has `"confidence": 0.847`. Three options:
- `"retrieval_relevance"` — most precise, self-documenting
- `"relevance_score"` — shorter, still clear
- `"relevance"` — simplest

Recommendation: **`"relevance_score"`** — mirrors the existing `Source.confidence` rename nicely and is consistent with how Pinecone/LangChain name it.

**2. Does `config.py` `confidence_threshold` get renamed?**
This is an env var (`CONFIDENCE_THRESHOLD=0.65` in `.env`). Renaming it is a deployment breaking change — anyone with `.env` files would need to update. Options:
- Rename to `RELEVANCE_THRESHOLD` (clean but breaks existing deployments)
- Keep env var name, only update the description string (safe)

Recommendation: **rename it** — since we're doing a version bump to 1.1 anyway, document it in release notes.

**3. Does `check_confidence()` method in `retrieval.py` get renamed?**
Internal method only, not exposed in the API. Renaming to `check_relevance()` is safe and consistent.

---

## Scope of Refactoring

This is a **terminology rename only** — no new features, no new computations. The number itself stays exactly the same.

**Version bump:** `1.0.0` → `1.1.0` (breaking API field rename warrants minor version increment).

### Backend

| Location | Current | Proposed |
|---|---|---|
| `app/__init__.py` | `__version__ = "1.0.0"` | `"1.1.0"` |
| `models.py` `Source` JSON field | `confidence` | `relevance_score` ⚠️ breaking |
| `models.py` `Source` field description | `"Relevance confidence score"` | `"Retrieval relevance score"` |
| `models.py` `QueryResponse` JSON field | `confidence` | `relevance_score` ⚠️ breaking |
| `models.py` `QueryResponse` field description | `"Overall confidence score"` | `"Overall retrieval relevance score"` |
| `config.py` env var | `CONFIDENCE_THRESHOLD` / `confidence_threshold` | `RELEVANCE_THRESHOLD` / `relevance_threshold` ⚠️ breaking |
| `config.py` description | `"Minimum confidence for known answers"` | `"Minimum retrieval relevance score to attempt answer generation"` |
| `retrieval.py` method | `check_confidence()` | `check_relevance()` |
| `retrieval.py` variable | `overall_confidence` | `overall_relevance` |
| `retrieval.py` dict key | `"confidence"` in returned dict | `"relevance_score"` |
| `main.py` variable | `overall_confidence` | `overall_relevance` |
| `main.py` dict access | `.get("confidence", 0.0)` (×5) | `.get("relevance_score", 0.0)` |
| `main.py` log messages | `"Semantic confidence …"` etc. | `"Semantic relevance …"` |

### Frontend

| Location | Current | Proposed |
|---|---|---|
| `App.jsx` line 82 | `confidence: data.confidence` | `relevance_score: data.relevance_score` ⚠️ breaking |
| `App.jsx` line 313 | `item.confidence >= 0.8` | `item.relevance_score >= 0.8` |
| `App.jsx` line 319 | `item.confidence * 100` | `item.relevance_score * 100` |
| `ResponseDisplay.jsx` line 56 | `"Low Confidence Response"` | `"Low Relevance Score"` |
| `ResponseDisplay.jsx` line 58 | `"The system has low confidence … in this answer"` | `"The retrieved documents have low relevance to this question"` |
| `ResponseDisplay.jsx` line 89 | `"High/Medium/Low Confidence"` badge | `"High/Medium/Low Relevance"` badge |
| `ResponseDisplay.jsx` all `response.confidence` refs | `response.confidence` | `response.relevance_score` ⚠️ breaking |
| `SourceCard.jsx` all `source.confidence` refs | `source.confidence` | `source.relevance_score` ⚠️ breaking |
| `SourceCard.jsx` labels | Already says "High/Medium/Low Relevance" | ✅ label correct, only field name changes |

### Evaluation Pipeline

| Location | Current | Proposed |
|---|---|---|
| `evaluation/run_ragas_stage1_query.py` line 82 | `rag_response.get('confidence', 0.0)` | `rag_response.get('relevance_score', 0.0)` |
| `evaluation/run_ragas_stage1_query.py` line 102 | `"confidence": confidence` in output JSON | `"relevance_score": relevance_score` |
| `evaluation/run_ragas_stage1_query.py` line 112 | `print(f"Confidence: {confidence:.3f}")` | `print(f"Relevance score: {relevance_score:.3f}")` |

### Tests

| Location | Current | Proposed |
|---|---|---|
| `backend/tests/test_retrieval.py` | `test_confidence_calculation_inline` | rename to `test_relevance_calculation_inline` |
| `backend/tests/test_retrieval.py` | `test_check_confidence_method` | rename to `test_check_relevance_method` |
| `backend/tests/test_retrieval.py` | `assert "confidence" in results` | `assert "relevance_score" in results` |
| `backend/tests/test_retrieval.py` | `results["confidence"]` (×3) | `results["relevance_score"]` |
| `backend/tests/test_retrieval.py` | mock dicts with `"confidence": 0.95` | `"relevance_score": 0.95` |

### Docs

#### `docs/RAG-REFERENCE.md`
| Location | Fix needed |
|---|---|
| Semantic retriever section | "Confidence threshold: 0.65" — clarify it is a retrieval relevance gate, not answer confidence |

#### `README.md`
The most misleading instance in any file:

| Location | Current (wrong) | Proposed |
|---|---|---|
| Line 135 heading | `"Understanding Confidence Scores"` | `"Understanding Retrieval Relevance Scores"` |
| Line 137 | `"confidence scores to indicate **answer quality**"` | `"retrieval relevance scores that indicate how well the retrieved documents match your query"` |
| Line 138–140 | `"Strong match, highly relevant sources"` etc. | Already partially accurate — just change label from "confidence" to "relevance" |
| Line 143–145 | `"Low Confidence Warning … answer may be uncertain"` | `"Low Relevance Warning … retrieved documents weakly match your query"` |
| Line 113 | `"Display answer with confidence score"` | `"Display answer with retrieval relevance score"` |

#### `docs/technical-report.md`
These are lower priority (technical audience, not user-facing) but still imprecise:

| Location | Current | Note |
|---|---|---|
| Line 27 | `"Confidence Check (threshold: 0.65 — reject or proceed)"` | Could add `"(retrieval relevance check)"` parenthetical |
| Line 30 | `"Response with sources + confidence score"` | Should say `"retrieval relevance score"` |
| Lines 53–54 | `"52.7% confidence"`, `"74.4% confidence"` | These are retrieval relevance scores used as evidence for the acronym problem — label as such |
| Line 89 | `"confidence score displayed per response with colour-coded warnings"` | Should clarify it is retrieval relevance |
| Line 107 | `"retrieval confidence is below threshold"` | ✅ Already uses "retrieval confidence" — closest to correct, leave as-is |

#### `docs/solution-deep-dive.md`
| Location | Current | Note |
|---|---|---|
| Architecture box | `"Confidence UI"`, `"Confidence calc"` | Could say `"Relevance UI"`, `"Relevance calc"` |
| RAG Pipeline step 5 | `"Confidence Check (1 − mean(distances), threshold 0.65)"` | The formula is correct and explained — just rename to `"Retrieval Relevance Check"` |
| Case study table | `"Semantic Conf"`, `"Hybrid Conf"` columns | Could rename to `"Semantic Relevance"`, `"Hybrid Relevance"` |

---

## What This Is NOT

- ❌ Not adding answer-level confidence (would require post-generation LLM evaluation)
- ❌ Not changing the threshold value (0.65 stays the same)
- ❌ Not changing the computation formula
- ❌ Not changing the API JSON key name (to avoid breaking changes) — only fix human-readable descriptions and UI labels
