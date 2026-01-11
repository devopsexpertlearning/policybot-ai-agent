"""
Comprehensive tests for the AI agent with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.agents.agent import AIAgent, QueryType, ResponseMethod
from tests.factories import QueryFactory, ResponseFactory


@pytest.mark.unit
class TestAIAgent:
    """Test AI agent functionality with mocks."""
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client."""
        client = Mock()
        client.generate = AsyncMock(return_value="POLICY")
        client.generate_with_history = AsyncMock(return_value="Mocked answer to your query.")
        client.generate_embedding = AsyncMock(return_value=[0.1] * 1536)
        client.environment = "local"
        return client
    
    @pytest.fixture
    def mock_retriever(self):
        """Mock retriever."""
        retriever = Mock()
        retriever.retrieve = AsyncMock(return_value=[
            {
                "content": "Employees are entitled to 15 days of paid vacation per year.",
                "metadata": {"source": "leave_policy.txt", "page": 1},
                "similarity_score": 0.92
            },
            {
                "content": "Remote work is allowed up to 3 days per week.",
                "metadata": {"source": "remote_work_policy.txt", "page": 2},
                "similarity_score": 0.85
            }
        ])
        retriever.format_sources = Mock(return_value=["leave_policy.txt", "remote_work_policy.txt"])
        return retriever
    
    @pytest.fixture
    def agent(self, mock_llm_client, mock_retriever):
        """Create agent with mocked dependencies."""
        with patch('app.agents.agent.llm_client', mock_llm_client):
            with patch('app.agents.agent.retriever', mock_retriever):
                return AIAgent()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.memory is not None
        assert hasattr(agent, 'stats')
        assert agent.stats['total_queries'] == 0
    
    @pytest.mark.asyncio
    async def test_classify_query_policy(self, agent, mock_llm_client):
        """Test policy query classification."""
        mock_llm_client.generate.return_value = "POLICY"
        result = await agent.classify_query("What is the leave policy?")
        assert result == QueryType.POLICY
    
    @pytest.mark.asyncio
    async def test_classify_query_general(self, agent, mock_llm_client):
        """Test general query classification."""
        mock_llm_client.generate.return_value = "GENERAL"
        result = await agent.classify_query("What is the capital of France?")
        assert result == QueryType.GENERAL
    
    @pytest.mark.asyncio
    async def test_classify_query_clarification(self, agent, mock_llm_client):
        """Test clarification query classification."""
        mock_llm_client.generate.return_value = "CLARIFICATION"
        result = await agent.classify_query("huh?")
        assert result == QueryType.CLARIFICATION
    
    @pytest.mark.asyncio
    async def test_classify_query_with_fallback(self, agent, mock_llm_client):
        """Test classification falls back to keyword matching on error."""
        mock_llm_client.generate.side_effect = Exception("LLM error")
        
        # Should fall back to keyword matching
        result = await agent.classify_query("What is the vacation policy?")
        assert result in [QueryType.POLICY, QueryType.GENERAL, QueryType.CLARIFICATION]
    
    @pytest.mark.asyncio
    async def test_direct_response_generation(self, agent, mock_llm_client):
        """Test direct LLM response generation."""
        session_id = agent.memory.create_session()
        response = await agent.generate_direct_response(
            "What is 2+2?",
            session_id
        )
        
        assert response["answer"] is not None
        assert response["source"] == ["direct_llm"]
        assert response["method"] == ResponseMethod.DIRECT
        # Metadata is added by process_query, not generate_direct_response
    
    @pytest.mark.asyncio
    async def test_rag_response_generation(self, agent, mock_llm_client, mock_retriever):
        """Test RAG-based response generation."""
        session_id = agent.memory.create_session()
        response = await agent.generate_rag_response(
            "What is the leave policy?",
            session_id
        )
        
        assert response["answer"] is not None
        assert len(response["source"]) > 0
        assert response["method"] == ResponseMethod.RAG
        mock_retriever.retrieve.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_process_query_general(self, agent, mock_llm_client):
        """Test processing general query."""
        mock_llm_client.generate.return_value = "GENERAL"
        
        response = await agent.process_query("Hello, how are you?")
        
        assert "answer" in response
        assert "source" in response
        assert "session_id" in response
        assert "metadata" in response
        assert response["metadata"]["processing_time"] >= 0
        assert response["metadata"]["query_type"] == "GENERAL"
    
    @pytest.mark.asyncio
    async def test_process_query_policy(self, agent, mock_llm_client):
        """Test processing policy query."""
        mock_llm_client.generate.return_value = "POLICY"
        
        response = await agent.process_query("What is the leave policy?")
        
        assert "answer" in response
        assert len(response["source"]) > 0
        assert response["metadata"]["query_type"] == "POLICY"
    
    @pytest.mark.asyncio
    async def test_process_query_clarification(self, agent, mock_llm_client):
        """Test processing clarification query."""
        mock_llm_client.generate.return_value = "CLARIFICATION"
        
        response = await agent.process_query("huh?")
        
        assert "answer" in response
        assert "not quite sure" in response["answer"].lower()
    
    @pytest.mark.asyncio
    async def test_session_persistence(self, agent, mock_llm_client):
        """Test session persistence across queries."""
        mock_llm_client.generate.return_value = "GENERAL"
        session_id = agent.memory.create_session()
        
        await agent.process_query("First query", session_id)
        await agent.process_query("Second query", session_id)
        
        history = agent.memory.get_history(session_id)
        assert len(history) >= 4  # 2 user messages + 2 assistant messages
    
    @pytest.mark.asyncio
    async def test_new_session_creation(self, agent, mock_llm_client):
        """Test automatic session creation."""
        mock_llm_client.generate.return_value = "GENERAL"
        
        response = await agent.process_query("Test query")
        
        assert response["session_id"] is not None
        assert agent.memory.session_exists(response["session_id"])
    
    def test_get_stats(self, agent):
        """Test agent statistics."""
        stats = agent.get_stats()
        
        assert "memory" in stats
        assert "provider" in stats
        assert "environment" in stats
        assert "total_queries" in stats
    
    @pytest.mark.asyncio
    async def test_get_session_info(self, agent, mock_llm_client):
        """Test getting session information."""
        mock_llm_client.generate.return_value = "GENERAL"
        session_id = agent.memory.create_session()
        
        await agent.process_query("Test", session_id)
        
        info = await agent.get_session_info(session_id)
        assert info is not None
        assert info["session_id"] == session_id
        assert "message_count" in info
    
    @pytest.mark.asyncio
    async def test_stats_increment(self, agent, mock_llm_client):
        """Test stats increment after queries."""
        mock_llm_client.generate.return_value = "GENERAL"
        initial_count = agent.stats['total_queries']
        
        await agent.process_query("Test query 1")
        await agent.process_query("Test query 2")
        
        assert agent.stats['total_queries'] == initial_count + 2
