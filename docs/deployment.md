# Deployment Guide

FinSQL Agent is structured for zero-friction local development and production cloud deployment.

## 1. Local Development (Zero-Dependency SQLite)

```bash
# 1. Activate environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt

# 2. Initialize and seed DB
python scripts/init_db.py
python scripts/seed_data.py
python scripts/build_schema_embeddings.py

# 3. Start Backend
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 4. Start Frontend
cd frontend
npm install
npm run dev
```

---

## 2. Docker Compose (PostgreSQL + pgvector)

```bash
docker compose up -d
```

Update `.env`:
```env
DATABASE_URL=postgresql://finsql:finsqlpass@localhost:5432/finsqldb
```

Run initialization:
```bash
python scripts/init_db.py
python scripts/seed_data.py
python scripts/build_schema_embeddings.py
```

---

## 3. Production Cloud Run & Cloud SQL Deployment

```text
┌───────────────────────────────────────┐
│           Vercel / Cloudflare         │
│             (React Frontend)          │
└───────────────────┬───────────────────┘
                    │ HTTPS
                    ▼
┌───────────────────────────────────────┐
│           Google Cloud Run            │
│            (FastAPI Backend)          │
└───────────┬───────────────────┬───────┘
            │                   │
            ▼                   ▼
┌───────────────────────┐ ┌─────────────┐
│  Cloud SQL PostgreSQL │ │ Google GenAI│
│      + pgvector       │ │ Gemini 2.5  │
└───────────────────────┘ └─────────────┘
```

### Dockerfile for Backend (Cloud Run)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```
