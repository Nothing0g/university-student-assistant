# Requirements traceability — Stage 1 and Stage 2

| Requirement | Status | Implementation / evidence |
|---|---|---|
| Python project skeleton | PASS | Repository folders and `pyproject.toml` |
| FastAPI + Uvicorn | PASS | `app/api/main.py`; `tests/test_foundation.py::test_health_contract` |
| Pydantic v2 request/response validation | PASS | `app/schemas/api.py`; invalid request/header tests |
| SQLite foundation | PASS | `app/database/schema.sql`, `app/database/db.py` |
| Audit endpoint foundation | PASS | `GET /audit/{trace_id}`; `test_ask_contract_and_audit` |
| Docker + Compose | PASS | `Dockerfile`, `docker-compose.yml` |
| Ollama JSON pre-flight | BLOCKED | Ollama/model not supplied in this environment; see `reports/stage1_preflight.md` |
| Real DTU source corpus minimum of three documents | BLOCKED / PARTIAL | Two user-supplied PDFs are present; `docs/COVERAGE_MATRIX.md` records the limitation |
| Source Register | PARTIAL | `data/source_register.csv`; two sources only and provenance is user-provided GitHub, not independently verified |
| Coverage matrix | PASS WITH LIMITATION | `docs/COVERAGE_MATRIX.md`; verified page/section references and unsupported topics recorded |
| Synthetic parameters | PROPOSED — APPROVAL REQUIRED | Values and supersession references are in `docs/COVERAGE_MATRIX.md`; no synthetic rules/docs created yet |
| Synthetic policy and data | NOT STARTED | Must follow explicit approval gate |
| RAG, tools, LangGraph, UI completion, evaluation | NOT STARTED | Later stages |
