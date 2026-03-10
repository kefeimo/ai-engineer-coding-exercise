# Tech Stack Selection Rationale

**Project:** AI Engineer Coding Exercise - RAG System  
**Date:** March 2026

---

## Overview

This document explains the technical decisions behind the RAG system architecture, prioritizing **proven technologies**, **cost efficiency**, and **production patterns**.

---

## Core Principles

1. **Battle-Tested Stack:** Leverage familiar, reliable technologies
2. **Free & Offline:** Zero API costs during development
3. **Production-Ready:** Easy upgrade path to cloud/paid services
4. **Demonstrable Skills:** Show full-stack GenAI capabilities

---

## Technology Decisions

### **Backend: FastAPI**
**Rationale:**
- ✅ Modern Python web framework built for ML/AI services
- ✅ Auto-generated OpenAPI docs (`/docs`)
- ✅ Native async support for streaming responses
- ✅ Pydantic validation (type safety)
- ✅ Industry standard for ML/AI APIs
- ✅ Excellent performance and developer experience

**Alternatives Considered:**
- Flask: Simpler but lacks async and auto-docs
- Django: Overkill for API-only service

---

### **Vector Database: ChromaDB**
**Rationale:**
- ✅ Python-native (no separate server required)
- ✅ Persistent local storage with minimal setup
- ✅ Simple, intuitive API (5 lines to set up)
- ✅ Perfect for prototype-to-production scale (252 chunks)
- ✅ Active development and strong community support
- ✅ Built-in embedding support

**Alternatives Considered:**
- Pinecone: Better for massive scale but requires API key/cloud
- Weaviate: More features but complex setup
- FAISS: Fast but requires more manual management

---

### **LLM: GPT4All (Mistral-7B-Instruct)**
**Rationale:**
- ✅ **Cost:** 100% free, offline operation
- ✅ **Quality:** 7B parameters = excellent instruction-following
- ✅ **Integration:** Direct Python import (no server required)
- ✅ **Quantization:** Q4_0 format optimized for CPU inference
- ✅ **Deployment:** Easy to containerize and distribute
- ✅ **Privacy:** No data sent to external APIs

**Why Mistral-7B Specifically:**
- Superior instruction compliance (critical for RAG grounding)
- Fine-tuned for following system prompts and constraints
- Balanced quality/performance tradeoff (80-99s on CPU)
- Strong performance on technical documentation tasks
- Actively maintained with good community support

**Why GPT4All over Ollama:**
- **Python-native:** Direct library import vs HTTP client overhead
- **Simpler deployment:** No separate server process to manage
- **Docker-friendly:** Easier containerization
- **Proven reliability:** Mature library with stable API

**Production Alternative:**
- OpenAI GPT-4 via abstracted `LLMClient` interface
- Same code, just environment variable change
- Demonstrates production engineering thinking

---

### **Embeddings: sentence-transformers/all-MiniLM-L6-v2**
**Rationale:**
- ✅ **Performance:** Excellent retrieval scores (0.80-0.93 similarity)
- ✅ **Efficiency:** Compact 384-dimensional vectors
- ✅ **Size:** Small model (~90MB) loads quickly
- ✅ **Speed:** Fast inference on CPU
- ✅ **Quality:** Semantic understanding sufficient for technical docs
- ✅ **Adoption:** Widely used in production RAG systems

**Why This Model:**
- Optimized for semantic similarity tasks
- Strong performance on question-answer retrieval
- Good balance of speed and accuracy
- CPU-friendly (no GPU required)

---

### **Frontend: React 19 + Vite 7 + Tailwind CSS 4**
**Rationale:**
- ✅ **React 19:** Modern component architecture, hooks ecosystem
- ✅ **Vite 7:** Lightning-fast dev server and HMR
- ✅ **Tailwind CSS 4:** Rapid UI development with utility classes
- ✅ **Modern Stack:** Latest stable versions, production-ready
- ✅ **Developer Experience:** Fast iteration and debugging

**Why This Combo:**
- Vite significantly faster than Webpack
- Tailwind eliminates CSS boilerplate
- React provides component reusability
- All three are industry standards

**Alternative Considered:**
- Plain HTML/JS: Simpler but less maintainable
- Next.js: Overkill for SPA without SSR needs

---

### **Evaluation: RAGAS**
**Rationale:**
- ✅ **Industry Standard:** Widely adopted RAG evaluation framework
- ✅ **Comprehensive Metrics:** Multiple quality dimensions
- ✅ **LangChain Integration:** Works seamlessly with our stack
- ✅ **Flexible Backends:** Supports both local and API-based LLMs
- ✅ **Research-Backed:** Based on academic RAG evaluation research

**Metrics Chosen:**
- `faithfulness`: Ensures answer grounded in retrieved context
- `answer_relevancy`: Measures if answer addresses the question
- `context_precision`: Validates retrieval quality

**Why RAGAS over Custom Metrics:**
- Standardized benchmarking (comparable results)
- Proven methodology
- Active development and community

---

## Architecture Patterns

### **Abstraction Strategy**
```python
# LLM Client abstraction for flexibility
class LLMClient(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

# Easy switching: GPT4All ↔ OpenAI
def get_llm_client() -> LLMClient:
    if settings.llm_provider == "gpt4all":
        return GPT4AllClient()
    return OpenAIClient()
```

**Benefits:**
- Switch LLMs without code changes
- Free dev → Paid production
- A/B testing different models

---

### **Configuration-Driven Design**
```bash
# All key parameters in .env
LLM_PROVIDER=gpt4all          # or openai
CHUNK_SIZE=500
CHUNK_OVERLAP=50
TOP_K_RESULTS=5
RELEVANCE_THRESHOLD=0.65
```

**Benefits:**
- Experiment without code changes
- Environment-specific configs
- Production-ready pattern

---

## RAG Pipeline Decisions

### **Chunk Size: 500 chars, 50 overlap**
**Rationale:**
- Balances context preservation vs retrieval granularity
- Small enough for precise matching
- Large enough to maintain semantic coherence
- Sentence-boundary awareness prevents mid-sentence breaks
- 50-char overlap ensures no information loss at boundaries

### **Confidence Threshold: 0.65**
**Rationale:**
- Empirical testing: All valid queries scored 0.80+
- Prevents false positives ("unknown" for low-confidence results)
- Tunable via configuration for different use cases
- Conservative enough to avoid hallucinations

### **Top-K: 5 documents**
**Rationale:**
- Standard RAG practice across industry
- Provides sufficient context (~2500 chars total)
- Doesn't overwhelm LLM context window
- Balances diversity vs focus of retrieved information

---

## Cost-Quality Tradeoffs

| Component | Dev Choice | Tradeoff | Production Upgrade |
|-----------|------------|----------|-------------------|
| **LLM** | GPT4All (free) | 80-99s latency | OpenAI GPT-4 (2-5s) |
| **Vector DB** | ChromaDB (local) | Single-machine | Pinecone (cloud scale) |
| **Embeddings** | sentence-transformers | CPU-only | GPU acceleration |

**Philosophy:**
> "Nail retrieval first (free), upgrade generation later (same pipeline)"

---

## Key Insights & Design Philosophy

### **RAG Quality Hierarchy**
**Critical Discovery:**
> "RAG quality = Retrieval (70%) + Generation (30%)"

**Implications:**
- Prioritize embedding model selection and chunk strategy
- LLM quality is important but secondary
- Focus optimization effort on retrieval pipeline first
- Can upgrade generation layer later without changing retrieval

**Strategy:**
1. ✅ Optimize retrieval first (achieved 0.80-0.93 similarity)
2. ✅ Use cost-effective LLM for development
3. ✅ Build abstraction for easy LLM upgrades
4. ✅ Prove system works end-to-end
5. → Swap in premium LLM for production (same pipeline)

### **Architecture Flexibility**
**Abstraction Benefits:**
- Development: GPT4All (free, offline)
- Production: OpenAI GPT-4 (premium quality)
- Same code, just configuration change
- Easy A/B testing of different models

---

## Summary

This tech stack demonstrates:
1. ✅ **Full-stack GenAI capabilities** (embedding → retrieval → generation)
2. ✅ **Production engineering patterns** (abstraction, config-driven, error handling)
3. ✅ **Cost-conscious development** ($0 API costs during build)
4. ✅ **Pragmatic technology choices** (proven, reliable, maintainable)
5. ✅ **Scalability thinking** (clear upgrade path to enterprise)

**Result:** Production-ready RAG system demonstrating both technical depth and strategic thinking.
