# Deliverables Checklist

**Project:** AI Engineer Coding Exercise - RAG System  
**Due Date:** March 5, 2026  
**Status:** 🟡 In Progress

---

## 📦 Required Deliverables

### 1. GitHub Repository ✅
- [x] Public/accessible repository
- [x] Source code committed
- [x] Repository: `git@github.com:kefeimo/ai-engineer-coding-exercise.git`
- [ ] All code pushed (in progress)

### 2. README with Setup Instructions ⏳
- [x] Initial skeleton created
- [ ] Complete installation instructions
- [ ] Prerequisites documented
- [ ] Quick start guide
- [ ] Usage examples
- [ ] Troubleshooting section

### 3. Technical Report (2-3 pages) OR Video ⏳
**Choosing:** Written report (2-3 pages)

**Required Sections:**
- [ ] **Approach** (Page 1)
  - [ ] Dataset choice rationale (FastAPI docs)
  - [ ] Architecture decisions
  - [ ] Technology stack justification
  - [ ] Evaluation strategy

- [ ] **Implementation** (Page 2)
  - [ ] Technical highlights
  - [ ] Production patterns used
  - [ ] Key challenges & solutions
  - [ ] Code structure overview

- [ ] **Evaluation Results** (Page 3)
  - [ ] RAGAS metrics (baseline + improved)
  - [ ] Analysis by query category
  - [ ] Improvement iteration
  - [ ] Key findings and insights

**File:** `docs/EVALUATION-REPORT.md`

### 4. Working Demo ⏳
**Deployment Strategy:** Local demo (Docker Compose)

- [ ] Backend runs successfully
- [ ] Frontend accessible
- [ ] RAG pipeline functional
- [ ] Can demonstrate live queries
- [ ] Docker Compose setup documented

---

## 💻 Code Deliverables

### Data Preparation ⏳
- [x] FastAPI documentation downloaded (12 files, ~500KB)
  - [x] Tutorial section (7 files)
  - [x] Advanced guide
  - [x] Deployment guide
  - [x] Features documentation
- [ ] Data ingested into ChromaDB
- [ ] Verify embeddings generated

### Backend Service ⏳
- [x] Project structure created
- [x] Requirements.txt defined
- [x] Environment configuration ready
- [ ] FastAPI application implemented
- [ ] RAG pipeline functional
- [ ] API endpoints working
- [ ] Error handling complete
- [ ] Logging configured

### RAG System Implementation ⏳
**Components:**
- [ ] **Document Ingestion**
  - [ ] Markdown parsing
  - [ ] Text chunking (500 chars, 50 overlap)
  - [ ] Metadata extraction
  - [ ] ChromaDB storage

- [ ] **Retrieval**
  - [ ] Vector similarity search
  - [ ] Top-k retrieval (k=5)
  - [ ] Confidence scoring
  - [ ] Context formatting

- [ ] **Generation**
  - [ ] GPT4All integration
  - [ ] OpenAI fallback config
  - [ ] Prompt construction
  - [ ] Source attribution
  - [ ] "Unknown" handling

### Evaluation Framework ⏳
- [ ] **RAGAS Integration**
  - [ ] 3 baseline metrics (context_precision, faithfulness, answer_relevancy)
  - [ ] 5 total metrics (+ context_recall, answer_correctness)
  - [ ] Custom metrics (response_time, token_cost, source_coverage)

- [ ] **Test Dataset**
  - [ ] 20 queries for baseline (easy, medium, hard)
  - [ ] 50 queries for full evaluation
  - [ ] Categorized by topic and difficulty
  - [ ] Realistic FastAPI use cases

- [ ] **Results Documentation**
  - [ ] Baseline scores recorded
  - [ ] Improvement iteration documented
  - [ ] Comparison tables created

### Frontend (Optional, but included) ⏳
- [ ] React + Vite setup
- [ ] Tailwind CSS configured
- [ ] Query interface implemented
- [ ] Results display with sources
- [ ] Confidence score visualization
- [ ] Error handling
- [ ] Loading states

### Infrastructure ⏳
- [ ] Docker Compose configuration
- [ ] Backend Dockerfile
- [ ] Frontend Dockerfile
- [ ] Volume mounts for development
- [ ] Environment variable management

---

## ✅ Code Quality Deliverables

### Code Standards ⏳
- [ ] Type hints throughout Python code
- [ ] Docstrings for all functions (Google style)
- [ ] Clean module structure
- [ ] Consistent naming conventions
- [ ] Error handling implemented
- [ ] Logging configured

### Testing ⏳
- [ ] 5 unit tests written
  - [ ] test_document_ingestion()
  - [ ] test_retrieval_returns_results()
  - [ ] test_prompt_construction()
  - [ ] test_unknown_handling()
  - [ ] test_source_attribution()
- [ ] pytest configuration
- [ ] All tests passing

### Configuration Management ⏳
- [x] .env.example created
- [x] .env file created
- [ ] Config validation implemented
- [ ] Defaults for all settings
- [ ] Sensitive data excluded from repo

---

## 📚 Documentation Deliverables

### Core Documentation ⏳
- [x] **README.md** (skeleton)
  - [x] Project overview
  - [ ] Complete setup instructions
  - [ ] Usage examples
  - [ ] API documentation
  - [ ] Troubleshooting

- [ ] **ARCHITECTURE.md**
  - [ ] System architecture diagram
  - [ ] Component descriptions
  - [ ] Data flow explanation
  - [ ] Key technical decisions
  - [ ] Technology stack rationale

- [ ] **EVALUATION-REPORT.md** (2-3 pages)
  - [ ] Approach section
  - [ ] Implementation section
  - [ ] Results section
  - [ ] Key findings

- [ ] **FUTURE-IMPROVEMENTS.md**
  - [ ] Scaling strategy
  - [ ] CI/CD pipeline
  - [ ] Kubernetes deployment
  - [ ] Security hardening
  - [ ] UX improvements

### Code Documentation ⏳
- [ ] Inline comments for complex logic
- [ ] API endpoint documentation
- [ ] Environment variable documentation
- [ ] Deployment instructions

---

## 🎯 Feature Deliverables

### Core Features (Required) ⏳
- [ ] Data ingestion from FastAPI docs
- [ ] Vector database (ChromaDB) integration
- [ ] LLM integration (GPT4All + OpenAI option)
- [ ] RAG query pipeline (retrieve + generate)
- [ ] Source attribution in responses
- [ ] Evaluation framework (RAGAS)

### Differentiation Features (Value-Add) ⏳
- [ ] **Unknown/TBD Handling**
  - [ ] Confidence threshold (0.65)
  - [ ] Out-of-scope detection
  - [ ] Helpful error messages

- [ ] **Hallucination Detection**
  - [ ] Post-generation faithfulness check
  - [ ] Low-confidence flagging
  - [ ] Optional answer suppression

- [ ] **Agent-Style Pipeline**
  - [ ] Retrieval validation step
  - [ ] Conditional logic by confidence
  - [ ] Multi-step: Query → Retrieval → Validation → Generation

- [ ] **Production Patterns**
  - [ ] Logging (request/response/errors)
  - [ ] Error handling (graceful degradation)
  - [ ] Config management
  - [ ] API versioning (/api/v1/)
  - [ ] Health check endpoint
  - [ ] Metrics endpoint

### UI Features (Optional) ⏳
- [ ] Clean, professional interface
- [ ] Query input with validation
- [ ] Loading states
- [ ] Response display with formatting
- [ ] Source list with confidence scores
- [ ] Error display
- [ ] Responsive design (Tailwind)

---

## 🚀 Submission Checklist

### Pre-Submission Verification
- [ ] All code committed and pushed
- [ ] README instructions tested (fresh install)
- [ ] Docker Compose builds successfully
- [ ] Demo runs without errors
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Report finalized (2-3 pages)
- [ ] Code cleaned (no debug prints, TODOs resolved)
- [ ] .env file excluded from repo
- [ ] Sensitive data removed

### Final Review
- [ ] Code quality review
- [ ] Documentation review
- [ ] Demo rehearsal
- [ ] Repository clean
- [ ] README clarity check
- [ ] Report proofread

### Submission Package
- [ ] GitHub repository URL ready
- [ ] README accessible on GitHub
- [ ] Report in docs/ folder
- [ ] All deliverables present
- [ ] Repository made public/accessible

---

## 📊 Progress Summary

**Overall Status:** 0/4 required deliverables complete (0%)

| Deliverable | Status | Progress |
|-------------|--------|----------|
| GitHub Repository | ✅ Created | 70% (in progress) |
| README | ⏳ In Progress | 30% |
| Technical Report | ⏳ Not Started | 0% |
| Working Demo | ⏳ In Progress | 15% |

**Code Deliverables:** 2/8 complete (25%)  
**Documentation Deliverables:** 1/4 complete (25%)  
**Feature Deliverables:** 0/10 complete (0%)

---

## 🎯 Critical Path

**Must Complete for Submission:**
1. ✅ GitHub repository
2. ⏳ Working RAG system (backend + frontend)
3. ⏳ Docker Compose setup
4. ⏳ Basic evaluation results
5. ⏳ README with setup instructions
6. ⏳ 2-3 page report

**Nice to Have:**
- 50 test queries (vs 20 minimum)
- 5 RAGAS metrics (vs 3 minimum)
- Agent-style features
- Comprehensive documentation

---

*Deliverables Checklist Version: 1.0*  
*Created: March 4, 2026*  
*Last Updated: March 4, 2026*
