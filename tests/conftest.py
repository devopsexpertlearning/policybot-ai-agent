"""
Shared test fixtures and configuration.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any
import numpy as np

from app.config import Settings
from app.agents.agent import AIAgent
from app.agents.memory import ConversationMemory
from app.llm.llm_client import LLMClient
from app.rag.document_processor import DocumentProcessor
from app.rag.vector_store import FAISSVectorStore


# Configuration Fixtures
@pytest.fixture
def test_settings():
    """Test settings with safe defaults."""
    return Settings(
        environment="local",
        google_gemini_api_key="test_key_12345",
        api_host="127.0.0.1",
        api_port=8000,
        log_level="DEBUG",
    )


# Mock LLM Responses
@pytest.fixture
def mock_llm_response():
    """Mock LLM text response."""
    return "This is a mock LLM response for testing purposes."


@pytest.fixture
def mock_embedding():
    """Mock embedding vector (1536 dimensions for Azure, 3072 for Gemini)."""
    return np.random.rand(1536).tolist()


@pytest.fixture
def mock_embeddings_batch():
    """Mock batch of embeddings."""
    return [np.random.rand(1536).tolist() for _ in range(5)]


# Mock LLM Client
@pytest.fixture
def mock_llm_client(mock_llm_response, mock_embedding):
    """Mock LLM client with predefined responses."""
    client = Mock(spec=LLMClient)
    client.generate = AsyncMock(return_value=mock_llm_response)
    client.generate_with_history = AsyncMock(return_value=mock_llm_response)
    client.generate_embedding = AsyncMock(return_value=mock_embedding)
    client.generate_embeddings_batch = AsyncMock(return_value=[mock_embedding] * 5)
    client.count_tokens = Mock(return_value=100)
    client.environment = "local"
    return client


# Memory Fixtures
@pytest.fixture
def memory():
    """Fresh conversation memory instance."""
    return ConversationMemory()


@pytest.fixture
def memory_with_session(memory):
    """Memory with a pre-created session."""
    session_id = memory.create_session()
    memory.add_message(session_id, "user", "Hello")
    memory.add_message(session_id, "assistant", "Hi there!")
    return memory, session_id


# Agent Fixtures
@pytest.fixture
def agent_with_mocks(mock_llm_client):
    """Agent instance with mocked LLM client."""
    with patch('app.agents.agent.llm_client', mock_llm_client):
        return AIAgent()


# Document Processing Fixtures
@pytest.fixture
def sample_text():
    """Sample text for document processing."""
    return """
    This is a sample company policy document.
    Employees are entitled to 15 days of paid vacation per year.
    Remote work is allowed up to 3 days per week.
    All employees must complete annual security training.
    """ * 10


@pytest.fixture
def sample_chunks():
    """Sample document chunks."""
    return [
        {
            "content": f"This is chunk {i} with policy information about benefits and leave.",
            "metadata": {
                "source": f"policy_doc_{i % 3}.txt",
                "chunk_id": i,
                "page": (i // 5) + 1
            }
        }
        for i in range(10)
    ]


# Vector Store Fixtures
@pytest.fixture
def mock_vector_store(mock_embeddings_batch, sample_chunks):
    """Mock vector store with sample data."""
    store = Mock(spec=FAISSVectorStore)
    store.add_documents = Mock()
    store.search = Mock(return_value=[
        {
            **chunk,
            "similarity_score": 0.95 - (i * 0.05)
        }
        for i, chunk in enumerate(sample_chunks[:5])
    ])
    store.get_stats = Mock(return_value={
        "total_documents": len(sample_chunks),
        "dimension": 1536
    })
    store.save = Mock()
    store.load = Mock()
    return store


# API Test Fixtures
@pytest.fixture
def api_client():
    """FastAPI test client."""
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app)


# Async Event Loop
@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock Retriever
@pytest.fixture
def mock_retriever(sample_chunks):
    """Mock retriever with sample results."""
    retriever = Mock()
    retriever.retrieve = AsyncMock(return_value=sample_chunks[:3])
    return retriever
