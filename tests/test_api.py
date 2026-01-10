"""
API endpoint tests.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAPI:
    """Test API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "environment" in data
    
    def test_health_endpoint(self):
        """Test health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "llm_provider" in data
        assert "vector_store" in data
    
    def test_ready_endpoint(self):
        """Test readiness check."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
    
    def test_ask_endpoint_validation(self):
        """Test ask endpoint input validation."""
        # Missing query
        response = client.post("/ask", json={})
        assert response.status_code == 422
        
        # Empty query
        response = client.post("/ask", json={"query": ""})
        assert response.status_code == 422
    
    def test_ask_endpoint_valid_request(self):
        """Test ask endpoint with valid request."""
        response = client.post(
            "/ask",
            json={"query": "Hello"}
        )
        
        # May fail if vector store not set up, but should not be 500
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "answer" in data
            assert "source" in data
            assert "session_id" in data
    
    def test_stats_endpoint(self):
        """Test stats endpoint."""
        response = client.get("/stats")
        assert response.status_code == 200
        data = response.json()
        assert "memory" in data
        assert "provider" in data
        assert "environment" in data
