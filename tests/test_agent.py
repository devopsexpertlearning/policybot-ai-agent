"""
Basic tests for the AI agent.
"""

import pytest
import asyncio
from app.agents.agent import AIAgent, QueryType
from app.agents.memory import ConversationMemory
from app.config import settings


class TestAIAgent:
    """Test the AI agent functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return AIAgent()
    
    @pytest.fixture
    def memory(self):
        """Create memory instance."""
        return ConversationMemory()
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.llm_client is not None
        assert agent.memory is not None
    
    @pytest.mark.asyncio
    async def test_query_classification(self, agent):
        """Test query classification."""
        # Test general query
        result = await agent.classify_query("What is the capital of France?")
        assert result in [QueryType.GENERAL, QueryType.POLICY, QueryType.CLARIFICATION]
    
    @pytest.mark.asyncio
    async def test_process_query(self, agent):
        """Test basic query processing."""
        response = await agent.process_query("Hello, how are you?")
        
        assert response is not None
        assert "answer" in response
        assert "source" in response
        assert "session_id" in response
        assert "metadata" in response
    
    def test_memory_session_creation(self, memory):
        """Test session creation."""
        session_id = memory.create_session()
        assert session_id is not None
        assert memory.session_exists(session_id)
    
    def test_memory_add_message(self, memory):
        """Test adding messages to session."""
        session_id = memory.create_session()
        memory.add_message(session_id, "user", "test message")
        
        history = memory.get_history(session_id)
        assert len(history) == 1
        assert history[0]["content"] == "test message"
    
    def test_memory_get_stats(self, memory):
        """Test memory statistics."""
        session_id = memory.create_session()
        memory.add_message(session_id, "user", "test")
        
        stats = memory.get_stats()
        assert stats["total_sessions"] >= 1
        assert stats["total_messages"] >= 1
