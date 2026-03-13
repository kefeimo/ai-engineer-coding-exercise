# REFERENCE: Prompt Engineering (Project-Oriented)

> Practical reference for implementation, based on this project's RAG prompt design.

---

## 1) Core Prompt Techniques

### Role-based prompting
Define:

- **Persona**: who the model is
- **Scope**: what domain/tasks it should handle
- **Behavior constraints**: how it must respond

In this project, role-based prompting is implemented in [backend/app/rag/generation.py](backend/app/rag/generation.py) via `PromptBuilder`.

### Few-shot prompting
Provide 1-3 examples of desired behavior/output format before the actual query.

Use when:
- output style is inconsistent
- model needs examples for edge behaviors (e.g., unknown handling)

### Chain-of-thought-style guidance (production-safe)
Use structured reasoning instructions, but keep final output concise.

Note: `CoT` means *Chain of Thought*.

Use when:
- answers need better reasoning discipline
- you want reliable grounded answers without verbose reasoning dumps

---

## 2) Mapping to Current Project Prompt

Current anchor line:

"You are a helpful AI assistant specialized in {domain}."

### What is what?

- **Persona**: "helpful AI assistant"
- **Scope**: "specialized in {domain}" + domain-specific guidance blocks (VCC/FastAPI/general)
- **Behavior constraints**: rules such as
  - answer from provided context
  - cite sources when possible
  - only use insufficient-info response when context is truly unrelated
  - handle minor typos/variations
  - interpret placeholders like `{{...}}` as intentional

---

## 3) Clarification: Is "helpful AI assistant" too general?

Yes, by itself it is generic.

But it is still a valid **base role**. In practice, role is layered:

1. base role: helpful assistant
2. domain role: VCC/FastAPI specialist
3. optional task role: API doc explainer, troubleshooting assistant, etc.

This project already strengthens the generic role with domain scope and explicit behavior constraints.

---

## 4) Prompt Techniques: When to Use Which

| Technique | Best for | Risk | Mitigation |
|---|---|---|---|
| Role-based | Consistent tone + domain alignment | Too generic role | Add precise scope + constraints |
| Few-shot | Enforcing answer format and edge-case behavior | Longer prompt/cost | Keep examples short and high-value |
| Chain-of-thought-style guidance | Better reasoning discipline | Verbose or off-format output | Ask for concise final answer only |

---

## 5) Project-Ready Examples

### A) Role-based (current style)

Use domain-specialist role + context-grounding rules.

Example wording:

- Persona: "You are a helpful AI assistant"
- Scope: "specialized in Visa Chart Components documentation"
- Constraints: "Answer from provided context; cite sources; if context is insufficient, say so clearly."

### B) Few-shot (recommended extension)

Add short examples inside prompt template:

- Example 1: API term question -> concise grounded answer + source mention
- Example 2: unrelated query -> explicit insufficient-context response

### C) Chain-of-thought-style (recommended extension)

Add internal structure instructions:

1. Identify relevant context chunks
2. Extract answer-supporting facts
3. Respond directly and concisely
4. If support is weak, state insufficient context

Then require final output as concise answer only.

---

## 6) Implementation Summary

This project currently uses role-based prompting with domain-specific scope and explicit behavior constraints. It can be extended with few-shot examples for output consistency and chain-of-thought-style structure for improved reasoning reliability while keeping final answers concise and grounded.

---

## 7) CoT vs HyDE (Important Distinction)

These techniques operate at different layers:

- **CoT (Chain of Thought)**: generation-time reasoning style
  - Applied after retrieval, during answer generation
  - Goal: improve reasoning quality over retrieved context

- **HyDE (Hypothetical Document Embeddings)**: retrieval-time query expansion
  - Applied before retrieval
  - Goal: improve recall by embedding a synthetic hypothetical answer/document

They can both appear in multi-step workflows, but they solve different problems:

- HyDE improves **what context you retrieve**
- CoT improves **how you reason over retrieved context**

---

## 8) Live Thinking UI vs Prompt Improvement

The frontend `ThinkingPanel` shows **live pipeline observability** -- not prompt engineering.

### How it works

- The backend exposes `POST /api/v1/query/stream` -- a Server-Sent Events (SSE) endpoint.
- As LangGraph executes each node (`planner` -> `semantic_retrieve` / `hybrid_retrieve` -> `evaluate` -> `generate`), the server emits a `{"type":"thinking","step":"..."}` event.
- The frontend reads these via `fetch` + `ReadableStream` (`queryRAGStream` in [frontend/src/utils/api.js](frontend/src/utils/api.js)).
- `ThinkingPanel` ([frontend/src/components/ThinkingPanel.jsx](frontend/src/components/ThinkingPanel.jsx)) renders steps as they arrive, auto-collapses after the final answer lands, and exposes expand/dismiss controls -- the same UX pattern as Copilot agent's "Thinking..." display.

### Why this is not CoT

| | Live Thinking UI | Chain-of-Thought |
|---|---|---|
| Layer | UX / observability | Prompt / generation |
| Happens | While graph nodes execute | Inside single LLM call |
| Purpose | Show user the pipeline is working | Improve answer reasoning quality |
| Affects answer quality? | No | Yes (when effective) |

### What does affect quality

- Prompt changes: role, few-shot examples, CoT-style structure
- Retrieval changes: hybrid strategy, HyDE, re-ranking
- Model changes

---

## 9) File Reference

- Prompt implementation: [backend/app/rag/generation.py](backend/app/rag/generation.py)
- SSE streaming endpoint: [backend/app/main.py](backend/app/main.py) (`POST /api/v1/query/stream`)
- Streaming client helper: [frontend/src/utils/api.js](frontend/src/utils/api.js) (`queryRAGStream`)
- Live thinking component: [frontend/src/components/ThinkingPanel.jsx](frontend/src/components/ThinkingPanel.jsx)
- Response schema: [backend/app/models.py](backend/app/models.py)

---

**Last Updated:** March 13, 2026
