# University Student Services Assistant

Stage 2 foundation for the HCLTech AI Engineer Hackathon build prompt. The repository is intentionally not claiming full specification compliance because only two real DTU source documents are currently available; the prompt requires at least three.

## Current stage

Implemented: project skeleton, environment configuration, SQLite schema matching the Annex C core tables, Pydantic v2 request/response models, FastAPI foundation endpoints, audit persistence, Docker Compose, Streamlit foundation UI, pytest tests, Stage 2 Source Register, page-aware coverage matrix, and proposed fictional synthetic-policy parameters.

The two source files are in `data/documents/`. The scanned examination notice has a user-supplied companion transcription at `data/documents/Notice_Studnt_O26_240826.transcript.txt`; this is not treated as a third document.

Not yet implemented: synthetic policy PDFs, RAG/ChromaDB indexing, AI-generated synthetic student data, deterministic tools, LangGraph workflow, live ingestion, full evaluation, and production-grade UI. Synthetic documents and student data are blocked until the proposed parameters in `docs/COVERAGE_MATRIX.md` are explicitly approved.

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

## Stage 2 status

Read `docs/COVERAGE_MATRIX.md` for verified source references, unsupported topics, proposed synthetic values, and the approval gate. The synthetic policy layer is fictional by design and must never be described as official DTU policy.

## Required next input

Approve or revise the proposed synthetic parameters and amendment effective date. A third verified DTU document is still needed to satisfy the original real-corpus minimum.
