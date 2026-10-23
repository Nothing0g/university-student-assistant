from datetime import date
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

AnswerType = Literal["retrieved_fact", "calculated", "not_found", "clarification_needed", "refused", "conflict_flagged"]

class AskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=1, max_length=4000)
    as_of_date: date | None = None

class Citation(BaseModel):
    doc_id: str
    title: str
    section: str | None = None
    page: int | None = None
    version: str | None = None
    effective_from: date | None = None
    synthetic: bool = False

class AskResponse(BaseModel):
    trace_id: str
    answer: str
    answer_type: AnswerType
    citations: list[Citation] = []
    tools_invoked: list[dict[str, Any]] = []
    applied_rules: list[dict[str, Any]] = []
    conflicts_detected: list[dict[str, Any]] = []
    explanation: str
    as_of_date: date

class SourceResponse(BaseModel):
    sources: list[dict[str, Any]]

class IngestResponse(BaseModel):
    doc_id: str
    chunks_indexed: int
    status: Literal["accepted", "failed"]


def validate_student_header(value: str | None) -> str | None:
    if value is None:
        return None
    if not re.fullmatch(r"S\d{4}", value):
        raise ValueError("X-Student-Id must match S followed by four digits")
    return value
