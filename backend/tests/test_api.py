import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_api_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "FinSQL Agent API"


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"]["companies_count"] >= 7
    assert data["database"]["financial_facts_count"] >= 300


def test_api_schema():
    response = client.get("/api/schema")
    assert response.status_code == 200
    data = response.json()
    assert len(data["tables"]) == 3
    assert len(data["companies"]) >= 7
    assert len(data["concepts"]) >= 10


def test_api_examples():
    response = client.get("/api/examples")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 15


def test_api_metrics():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "finsql_agent" in data or "status" in data


def test_api_query_finsql():
    response = client.post("/api/query", json={"question": "What was Apple's revenue in 2023?"})
    assert response.status_code == 200
    data = response.json()
    assert "Apple" in data["answer"]
    assert "383" in data["answer"]
    assert data["execution"]["success"] is True
    assert data["validation"]["valid"] is True
    assert len(data["trace"]) >= 4


def test_api_query_baseline():
    response = client.post("/api/query", json={"question": "What was Apple's revenue in 2023?", "mode": "baseline"})
    assert response.status_code == 200
    data = response.json()
    assert data["mode"] == "Baseline Text-to-SQL"
    assert data["execution"]["success"] is True
