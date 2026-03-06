# 🔧 Troubleshooting Guide

## Common Issues

### 1. "OpenAI API key not found" Error
**Symptom:** Backend returns 500 error with "OpenAI API key not found"

```bash
cd backend
cp .env.example .env          # if .env is missing
echo "OPENAI_API_KEY=sk-..." >> .env

# Restart: docker compose restart backend
```

---

### 2. ChromaDB Collection Not Found
**Symptom:** `Collection not found` error on query

Documents may not have been ingested yet. Restart the dev stack — it auto-ingests on startup:
```bash
docker compose -f docker-compose-dev.yml up
```

Or manually trigger ingestion:
```bash
docker compose exec backend python ingest_visa_docs.py
docker compose exec backend python ingest_fastapi_docs.py
```

---

### 3. Frontend Can't Connect to Backend
**Symptom:** "Failed to fetch" in browser console

```bash
curl http://localhost:8000/health   # check if backend is up

# Check logs
docker compose logs backend
```

---

### 4. Port Already in Use
**Symptom:** "Address already in use" on startup

```bash
lsof -ti :8000 | xargs kill -9   # free backend port
lsof -ti :5173 | xargs kill -9   # free frontend port
```

---

### 5. Docker Build Fails / Container Exits

```bash
docker compose logs backend
docker compose logs frontend

# Clean rebuild
docker compose -f docker-compose-dev.yml down -v
docker compose -f docker-compose-dev.yml up --build --no-cache
```

---

### 6. Slow Query Response (>60s)
- Ensure `LLM_PROVIDER=openai` in `backend/.env` (GPT4All local LLM is much slower)
- Reduce `TOP_K=3` in `.env` to retrieve fewer chunks

---

### 7. Low Confidence Scores (<0.65)
- Re-ingest documents if collection is empty or stale
- Rephrase queries: `"What is VCC?"` → `"What is Visa Chart Components?"`
- The frontend toggle must match the ingested collection (`VCC Docs` vs `FastAPI Docs`)

---

### 8. RAGAS Evaluation Fails

```bash
export OPENAI_API_KEY="sk-..."

# Debug with minimal dataset first
cd evaluation
python run_ragas_stage1_query.py --input ../data/test_queries/baseline_3.json
```

---

## Checking Logs

```bash
docker compose logs -f backend     # backend logs
docker compose logs -f frontend    # frontend logs
# or open browser DevTools (F12) → Console
```

## Full Reset

```bash
docker compose -f docker-compose-dev.yml down -v
rm -rf data/chroma_db              # wipe ChromaDB
docker compose -f docker-compose-dev.yml up --build
# collections will be re-ingested automatically on startup
```

---

*See also: [DOCKER.md](../DOCKER.md) | [DOCKER-GPU.md](DOCKER-GPU.md) | [backend/README.md](../backend/README.md)*
