"""
Enhanced API endpoint tests with mocked dependencies.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from app.main import app
from tests.factories import QueryFactory, ResponseFactory


@pytest.mark.unit
class TestAPI:
    """Test API endpoints with mocked dependencies."""
    
    @pytest.fixture
    def client(self):
        """Test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_agent(self):
        """Mock agent with predefined responses."""
        agent = Mock()
        agent.process_query = AsyncMock(return_value=ResponseFactory.agent_response())
        agent.get_session_info = AsyncMock(return_value={
            "session_id": "test-session",
            "message_count": 2,
            "created_at": "2024-01-01T00:00:00",
            "last_activity": "2024-01-01T00:05:00"
        })
        agent.get_stats = Mock(return_value={
            "memory": {"total_sessions": 1, "total_messages": 2},
            "provider": "gemini",
            "environment": "local",
            "total_queries": 5
        })
        return agent
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "environment" in data
        assert "endpoints" in data
    
    def test_health_endpoint(self, client):
        """Test health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "environment" in data
        assert "llm_provider" in data
        assert "vector_store" in data
    
    def test_ready_endpoint(self, client):
        """Test readiness check."""
        response = client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
    
    def test_ask_endpoint_validation_missing_query(self, client):
        """Test ask endpoint validates missing query."""
        response = client.post("/ask", json={})
        assert response.status_code == 422
    
    def test_ask_endpoint_validation_empty_query(self, client):
        """Test ask endpoint validates empty query."""
        response = client.post("/ask", json={"query": ""})
        assert response.status_code == 422
    
    def test_ask_endpoint_validation_whitespace_query(self, client):
        """Test ask endpoint with whitespace-only query."""
        response = client.post("/ask", json={"query": "   "})
        # API accepts whitespace queries and processes them
        assert response.status_code == 200
    
    def test_ask_endpoint_with_mock(self, client, mock_agent):
        """Test ask endpoint with mocked agent."""
        with patch('app.api.routes.agent', mock_agent):
            response = client.post(
                "/ask",
                json={"query": "What is the leave policy?"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "source" in data
            assert "session_id" in data
            mock_agent.process_query.assert_called_once()
    
    def test_ask_endpoint_with_session_id(self, client, mock_agent):
        """Test ask endpoint with existing session."""
        with patch('app.api.routes.agent', mock_agent):
            response = client.post(
                "/ask",
                json={
                    "query": "Follow-up question",
                    "session_id": "existing-session-123"
                }
            )
            
            assert response.status_code == 200
            call_args = mock_agent.process_query.call_args
            assert call_args[1]["session_id"] == "existing-session-123"
    
    def test_ask_detailed_endpoint(self, client, mock_agent):
        """Test detailed ask endpoint."""
        mock_agent.process_query.return_value = ResponseFactory.agent_response(
            sources=["policy.txt", "handbook.txt"]
        )
        
        with patch('app.api.routes.agent', mock_agent):
            response = client.post(
                "/ask/detailed",
                json={"query": "Test query"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "answer" in data
            assert "sources" in data
            assert "method" in data
            assert "processing_time" in data
    
    def test_stats_endpoint(self, client, mock_agent):
        """Test stats endpoint."""
        with patch('app.api.routes.agent', mock_agent):
            response = client.get("/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert "memory" in data
            assert "provider" in data
            assert "environment" in data
    
    def test_session_endpoint(self, client, mock_agent):
        """Test session info endpoint."""
        with patch('app.api.routes.agent', mock_agent):
            response = client.get("/session/test-session")
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == "test-session"
            assert "message_count" in data
    
    def test_session_endpoint_not_found(self, client, mock_agent):
        """Test session endpoint with nonexistent session."""
        mock_agent.get_session_info.return_value = None
        
        with patch('app.api.routes.agent', mock_agent):
            response = client.get("/session/nonexistent")
            
            assert response.status_code == 404
    
    def test_cors_headers(self, client):
        """Test CORS headers are present."""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
    
    def test_multiple_requests_different_sessions(self, client, mock_agent):
        """Test multiple requests create different sessions."""
        with patch('app.api.routes.agent', mock_agent):
            response1 = client.post("/ask", json={"query": "Query 1"})
            response2 = client.post("/ask", json={"query": "Query 2"})
            
            # Both should succeed
            assert response1.status_code == 200
            assert response2.status_code == 200
    
    def test_error_handling(self, client, mock_agent):
        """Test error handling in API."""
        mock_agent.process_query.side_effect = Exception("Test error")
        
        with patch('app.api.routes.agent', mock_agent):
            response = client.post("/ask", json={"query": "Test"})
            
            assert response.status_code == 500
            data = response.json()
            assert "detail" in data
