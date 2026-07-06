import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add the parent directory to Python path to allow app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app

client = TestClient(app)

# 1. Test the root endpoint
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "FlowForge AI Service"
    assert data["status"] == "running"

# 2. Test the health endpoint
def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "model" in data

# 3. Test the telemetry endpoint (Endpoint removed by user)
# def test_read_telemetry():
#     response = client.get("/telemetry")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["status"] == "healthy"
#     assert data["database"] == "chromadb"

# 4. Test validation error on the architecture generation endpoint
def test_generate_architecture_validation_error():
    # Sending an empty JSON should result in a 422 Unprocessable Entity
    # because 'payload' and 'source' are required in WorkflowRequest
    response = client.post("/api/v1/workflow/generate", json={})
    assert response.status_code == 422
    assert "detail" in response.json()

# 5. Test knowledge ingestion with non-existent file
def test_knowledge_ingest_file_not_found():
    payload = {
        "file_path": "non_existent_file.pdf",
        "doc_type": "knowledge_book"
    }
    response = client.post("/knowledge/ingest", json=payload)
    # The endpoint should raise a 404 because the file doesn't exist
    assert response.status_code == 404
    assert response.json()["detail"] == "File not found"
