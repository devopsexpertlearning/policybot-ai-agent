"""
Integration tests for end-to-end workflows.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, Mock
from app.main import app
from tests.factories import QueryFactory


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def client(self):
        """Test client."""
        return TestClient(app)
    
    @pytest.fixture
    def mock_all_llm(self):
        """Mock all LLM interactions."""
        with patch('app.llm.llm_client.LLMClient') as mock_class:
            instance = Mock()
            instance.generate = AsyncMock(return_value="GENERAL")
            instance.generate_with_history = AsyncMock(
                return_value="This is a test response to your query."
            )
            instance.generate_embedding = AsyncMock(return_value=[0.1] * 1536)
            instance.generate_embeddings_batch = AsyncMock(
                return_value=[[0.1] * 1536 for _ in range(5)]
            )
            instance.count_tokens = Mock(return_value=100)
            instance.environment = "local"
            mock_class.return_value = instance
            
            # Also mock retriever for RAG integration availability
            with patch('app.agents.agent.retriever') as mock_retriever:
                mock_retriever.retrieve = AsyncMock(return_value=[
                    {"content": "Policy content", "metadata": {"source": "policy.txt"}}
                ])
                mock_retriever.format_sources = Mock(return_value=["policy.txt"])
                yield mock_class
    
    def test_complete_query_workflow(self, client, mock_all_llm):
        """Test complete query from API to response."""
        response = client.post(
            "/ask",
            json={"query": "What is the capital of France?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "session_id" in data
        assert "source" in data
        assert "metadata" in data
    
    def test_session_continuity(self, client, mock_all_llm):
        """Test session continuity across multiple requests."""
        # First request
        response1 = client.post(
            "/ask",
            json={"query": "Hello, I need help"}
        )
        assert response1.status_code == 200
        session_id = response1.json()["session_id"]
        
        # Second request with same session
        response2 = client.post(
            "/ask",
            json={
                "query": "What did I just say?",
                "session_id": session_id
            }
        )
        
        assert response2.status_code == 200
        assert response2.json()["session_id"] == session_id
        
        # Verify session info
        session_response = client.get(f"/session/{session_id}")
        assert session_response.status_code == 200
        session_data = session_response.json()
        assert session_data["message_count"] >= 2
    
    def test_policy_query_workflow(self, client, mock_all_llm):
        """Test policy query workflow with RAG."""
        # Mock policy classification
        mock_all_llm.return_value.generate = AsyncMock(return_value="POLICY")
        
        response = client.post(
            "/ask",
            json={"query": "What is the leave policy?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        # Policy queries should have document sources
        assert len(data["source"]) > 0
    
    def test_general_query_workflow(self, client, mock_all_llm):
        """Test general query workflow without RAG."""
        mock_all_llm.return_value.generate = AsyncMock(return_value="GENERAL")
        
        response = client.post(
            "/ask",
            json={"query": "What is 2+2?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        # General queries use direct LLM
        assert data["source"] == ["direct_llm"]
    
    def test_error_handling_invalid_input(self, client):
        """Test error handling for invalid input."""
        # Missing query
        response = client.post("/ask", json={})
        assert response.status_code == 422
        
        # Empty query
        response = client.post("/ask", json={"query": ""})
        assert response.status_code == 422
    
    def test_health_and_stats_integration(self, client, mock_all_llm):
        """Test health check and stats reflect system state."""
        # Make some queries
        client.post("/ask", json={"query": "Test 1"})
        client.post("/ask", json={"query": "Test 2"})
        
        # Check health
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"
        
        # Check stats
        stats_response = client.get("/stats")
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert "memory" in stats
        assert "total_queries" in stats
    
    def test_concurrent_sessions(self, client, mock_all_llm):
        """Test multiple concurrent sessions."""
        # Create multiple sessions
        sessions = []
        for i in range(3):
            response = client.post(
                "/ask",
                json={"query": f"Query {i}"}
            )
            assert response.status_code == 200
            sessions.append(response.json()["session_id"])
        
        # Verify all sessions are different
        assert len(set(sessions)) == 3
        
        # Verify each session exists
        for session_id in sessions:
            response = client.get(f"/session/{session_id}")
            assert response.status_code == 200
    
    def test_detailed_endpoint_integration(self, client, mock_all_llm):
        """Test detailed endpoint provides comprehensive response."""
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
        assert "metadata" in data
    
    def test_full_conversation_flow(self, client, mock_all_llm):
        """Test a full multi-turn conversation."""
        # Start conversation
        response1 = client.post(
            "/ask",
            json={"query": "Hello"}
        )
        session_id = response1.json()["session_id"]
        
        # Continue conversation
        queries = [
            "What is the leave policy?",
            "How many days?",
            "Can I take them all at once?"
        ]
        
        for query in queries:
            response = client.post(
                "/ask",
                json={"query": query, "session_id": session_id}
            )
            assert response.status_code == 200
            assert response.json()["session_id"] == session_id
        
        # Verify session has all messages
        session_response = client.get(f"/session/{session_id}")
        session_data = session_response.json()
        # Should have initial + 3 follow-ups = 4 user messages + 4 assistant responses
        assert session_data["message_count"] >= 6
