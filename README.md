# University Student Services Assistant

Stage 1 foundation for the HCLTech AI Engineer Hackathon build prompt. This repository is intentionally incomplete until the required official DTU PDFs are supplied. It does not invent official documents, clauses, or policy values.

## Current stage

Implemented and tested: project skeleton, environment configuration, SQLite schema matching the Annex C core tables, Pydantic v2 request/response models, FastAPI foundation endpoints, audit persistence, Docker Compose, Streamlit foundation UI, and pytest tests.

Not yet implemented: official DTU corpus, coverage matrix, synthetic policy PDFs, RAG/ChromaDB indexing, AI-generated synthetic student data, deterministic tools, LangGraph workflow, live ingestion, full evaluation, and production-grade UI. These are deliberately deferred to later stages because the supplied specification requires real DTU documents before synthetic parameters are chosen.

## Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
cp .env.example .env
pytest -q
uvicorn app.main:app --reload
```

In a second terminal:

```bash
streamlit run frontend/app.py
```

API: http://localhost:8000, Swagger: http://localhost:8000/docs, UI: http://localhost:8501.

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

Ollama is not silently replaced by a cloud model. The foundation defaults to `MOCK_LLM=true`; later stages will document host-to-container Ollama connectivity and pre-flight the configured model.

## Foundation API examples

```bash
curl http://localhost:8000/health
curl http://localhost:8000/sources
curl -X POST http://localhost:8000/ask \\
  -H 'Content-Type: application/json' \\
  -d '{"question":"What is the policy?"}'
```

`/ingest` returns a deliberate Stage 1 response until the real-corpus and ingestion stages are implemented.

## Required next input

Place at least three verified official DTU PDFs in `data/documents/` and provide their genuine metadata. The build must stop for coverage-matrix and synthetic-parameter approval before creating the synthetic policy layer or student dataset.
