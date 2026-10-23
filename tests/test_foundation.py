from fastapi.testclient import TestClient
from app.api.main import app
from app.database.db import init_db

init_db()
client = TestClient(app)

def test_health_contract():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["api"] == "ok"
    assert "sqlite" in response.json()

def test_ask_contract_and_audit():
    response = client.post("/ask", json={"question": "What is the policy?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer_type"] in {"retrieved_fact", "calculated", "not_found", "clarification_needed", "refused", "conflict_flagged"}
    audit = client.get(f"/audit/{body['trace_id']}")
    assert audit.status_code == 200

def test_invalid_student_header():
    response = client.post("/ask", headers={"X-Student-Id": "not-a-student"}, json={"question": "x"})
    assert response.status_code == 422

def test_invalid_request_does_not_run_model():
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422
