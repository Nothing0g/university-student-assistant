from datetime import date
import json
import uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile, status
from app.config import get_settings
from app.database.db import get_audit, init_db, save_audit, connect
from app.schemas.api import AskRequest, AskResponse, IngestResponse, SourceResponse, validate_student_header

app = FastAPI(title="University Student Services Assistant", version="0.1.0")

@app.on_event("startup")
def startup() -> None:
    init_db()

@app.get("/health")
def health() -> dict:
    settings = get_settings()
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
        sqlite_status = "ok"
    except Exception as exc:
        sqlite_status = f"error: {exc.__class__.__name__}"
    chroma_status = "configured" if Path(settings.chroma_path).exists() else "not_initialized"
    llm_status = "mock" if settings.mock_llm else "not_checked"
    return {"status": "ok" if sqlite_status == "ok" else "degraded", "api": "ok", "sqlite": sqlite_status, "chromadb": chroma_status, "llm": llm_status}

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, x_student_id: str | None = Header(default=None)) -> AskResponse:
    try:
        student_id = validate_student_header(x_student_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    trace_id = str(uuid.uuid4())
    as_of = request.as_of_date or date.today()
    answer = "The Stage 1 foundation is running. Policy retrieval and deterministic student tools are added in later stages."
    response = AskResponse(trace_id=trace_id, answer=answer, answer_type="clarification_needed", explanation="No policy or student-data workflow is enabled in the foundation stage.", as_of_date=as_of)
    save_audit(trace_id, {**response.model_dump(mode="json"), "student_reference": student_id, "stage": 1})
    return response

@app.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_501_NOT_IMPLEMENTED)
def ingest(file: UploadFile = File(...), metadata: str = Form(...)) -> IngestResponse:
    try:
        parsed = json.loads(metadata)
        if not isinstance(parsed, dict) or "doc_id" not in parsed:
            raise ValueError("metadata must be an Annex B object containing doc_id")
    except (json.JSONDecodeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    raise HTTPException(status_code=501, detail="Document ingestion is scheduled for Stage 3")

@app.get("/sources", response_model=SourceResponse)
def sources() -> SourceResponse:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM source_register ORDER BY doc_id").fetchall()
    return SourceResponse(sources=[dict(row) for row in rows])

@app.get("/audit/{trace_id}")
def audit(trace_id: str) -> dict:
    payload = get_audit(trace_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Audit record not found")
    return payload
