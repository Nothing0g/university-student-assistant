from datetime import date
import json, uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from app.database.db import connect, get_audit, init_db, save_audit
from app.schemas.api import AskRequest, AskResponse, SourceResponse, IngestResponse, validate_student_header
from app.services.core import answer_question, ensure_demo_state

app = FastAPI(title="University Student Services Assistant", version="1.0.0")

@app.on_event("startup")
def startup() -> None:
    init_db()
    ensure_demo_state()

@app.get("/health")
def health() -> dict:
    try:
        with connect() as conn: conn.execute("SELECT 1")
        db="ok"
    except Exception as exc: db=f"error: {type(exc).__name__}"
    return {"status":"ok" if db=="ok" else "degraded", "api":"ok", "sqlite":db, "chromadb":"lexical-demo-index", "llm":"mock-explanation; Ollama optional"}

@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, x_student_id: str | None = Header(default=None)) -> AskResponse:
    try: student_id=validate_student_header(x_student_id)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    response=answer_question(request.question, student_id, request.as_of_date or date.today())
    save_audit(response["trace_id"], {**response, "student_reference":student_id})
    return response

@app.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...), metadata: str = Form(...)) -> IngestResponse:
    try: meta=json.loads(metadata)
    except json.JSONDecodeError as exc: raise HTTPException(status_code=422, detail="metadata must be valid JSON") from exc
    required={"doc_id","title","issuer","authority_level","doc_type","version","effective_from","effective_to","supersedes","scope_programmes","scope_batches","provenance","retrieved_on","synthetic"}
    missing=required-set(meta)
    if missing: raise HTTPException(status_code=422, detail=f"missing metadata fields: {sorted(missing)}")
    if file.content_type not in {"text/plain","application/pdf","text/markdown"}:
        raise HTTPException(status_code=415, detail="only PDF, text, and Markdown files are allowed")
    root=Path(__file__).resolve().parents[2]; target=root/"data/documents"/Path(file.filename or "upload.txt").name
    payload=await file.read() if hasattr(file,"read") else b""
    if len(payload)>10*1024*1024: raise HTTPException(status_code=413, detail="file exceeds 10 MB limit")
    target.write_bytes(payload)
    with connect() as conn:
        conn.execute("INSERT OR REPLACE INTO source_register VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", tuple(meta[k] for k in ["doc_id","title","issuer","authority_level","doc_type","version","effective_from","effective_to","supersedes","scope_programmes","scope_batches","provenance","retrieved_on","synthetic"]))
    return IngestResponse(doc_id=meta["doc_id"], chunks_indexed=1, status="accepted")

@app.get("/sources", response_model=SourceResponse)
def sources() -> SourceResponse:
    with connect() as conn: rows=conn.execute("SELECT * FROM source_register ORDER BY doc_id").fetchall()
    return SourceResponse(sources=[dict(r) for r in rows])

@app.get("/students")
def students() -> dict:
    with connect() as conn: rows=conn.execute("SELECT student_id, programme, batch_year, current_semester, cgpa, active_backlogs FROM students ORDER BY student_id").fetchall()
    return {"students":[dict(r) for r in rows]}

@app.get("/audit/{trace_id}")
def audit(trace_id: str) -> dict:
    record=get_audit(trace_id)
    if record is None: raise HTTPException(status_code=404, detail="Audit record not found")
    return record
