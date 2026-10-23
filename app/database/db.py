import json
import sqlite3
from pathlib import Path
from app.config import get_settings


def connect() -> sqlite3.Connection:
    path = Path(get_settings().sqlite_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema = Path(__file__).with_name("schema.sql").read_text()
    with connect() as conn:
        conn.executescript(schema)


def save_audit(trace_id: str, payload: dict) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO audit_records(trace_id, created_at, payload_json) VALUES (?, datetime('now'), ?)",
            (trace_id, json.dumps(payload)),
        )


def get_audit(trace_id: str) -> dict | None:
    with connect() as conn:
        row = conn.execute("SELECT payload_json FROM audit_records WHERE trace_id = ?", (trace_id,)).fetchone()
    return json.loads(row["payload_json"]) if row else None
