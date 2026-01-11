"""
Unit tests for Azure AI Search vector store.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.rag.vector_store import AzureAISearchVectorStore, get_vector_store
from app.config import Settings


@pytest.mark.unit
class TestAzureVectorStore:
    """Test Azure AI Search vector store."""
    
    @pytest.fixture
    def azure_settings(self):
        """Settings for Azure environment."""
        return Settings(
            environment="production",
            azure_search_api_key="test_key",
            azure_search_endpoint="https://test.search.windows.net",
            azure_search_index_name="test-index",
            use_azure_search=True,
            use_faiss=False
        )
    
    @pytest.fixture
    def mock_search_client(self):
        """Mock Azure Search client."""
        client = Mock()
        client.upload_documents = Mock()
        client.search = Mock(return_value=[])
        return client
        
    @pytest.fixture
    def mock_index_client(self):
        """Mock Azure Search Index client."""
        client = Mock()
        client.create_or_update_index = Mock()
        return client

    def test_initialization(self, azure_settings, mock_search_client, mock_index_client):
        """Test initialization with Azure settings."""
        with patch('app.rag.vector_store.settings', azure_settings):
            with patch('app.rag.vector_store.AZURE_SEARCH_AVAILABLE', True):
                with patch('app.rag.vector_store.SearchClient', return_value=mock_search_client):
                    with patch('app.rag.vector_store.SearchIndexClient', return_value=mock_index_client):
                        store = AzureAISearchVectorStore()
                        assert store.endpoint == "https://test.search.windows.net"
                        assert store.index_name == "test-index"

    def test_create_index(self, azure_settings, mock_search_client, mock_index_client):
        """Test index creation."""
        with patch('app.rag.vector_store.settings', azure_settings):
            with patch('app.rag.vector_store.AZURE_SEARCH_AVAILABLE', True):
                with patch('app.rag.vector_store.SearchClient', return_value=mock_search_client):
                    with patch('app.rag.vector_store.SearchIndexClient', return_value=mock_index_client):
                        store = AzureAISearchVectorStore()
                        store.create_index()
                        mock_index_client.create_or_update_index.assert_called_once()

    def test_add_documents(self, azure_settings, mock_search_client, mock_index_client):
        """Test adding documents."""
        with patch('app.rag.vector_store.settings', azure_settings):
            with patch('app.rag.vector_store.AZURE_SEARCH_AVAILABLE', True):
                with patch('app.rag.vector_store.SearchClient', return_value=mock_search_client):
                    with patch('app.rag.vector_store.SearchIndexClient', return_value=mock_index_client):
                        store = AzureAISearchVectorStore()
                        
                        embeddings = [[0.1, 0.2]]
                        documents = [{"content": "test", "metadata": {"source": "test.txt"}}]
                        
                        store.add_documents(embeddings, documents)
                        mock_search_client.upload_documents.assert_called_once()
                        
    def test_search(self, azure_settings, mock_search_client, mock_index_client):
        """Test searching documents."""
        mock_result = {
            "@search.score": 0.9,
            "content": "test content",
            "source": "test.txt",
            "page": 1,
            "chunk_id": "1"
        }
        mock_search_client.search.return_value = [mock_result]
        
        with patch('app.rag.vector_store.settings', azure_settings):
            with patch('app.rag.vector_store.AZURE_SEARCH_AVAILABLE', True):
                with patch('app.rag.vector_store.SearchClient', return_value=mock_search_client):
                    with patch('app.rag.vector_store.SearchIndexClient', return_value=mock_index_client):
                        store = AzureAISearchVectorStore()
                        
                        results = store.search(query_embedding=[0.1, 0.2])
                        
                        assert len(results) == 1
                        assert results[0]["content"] == "test content"
                        assert results[0]["similarity_score"] == 0.9

    def test_factory_azure(self, azure_settings, mock_search_client, mock_index_client):
        """Test getting Azure store from factory."""
        with patch('app.rag.vector_store.settings', azure_settings):
            with patch('app.rag.vector_store.AZURE_SEARCH_AVAILABLE', True):
                with patch('app.rag.vector_store.SearchClient', return_value=mock_search_client):
                    with patch('app.rag.vector_store.SearchIndexClient', return_value=mock_index_client):
                        store = get_vector_store()
                        assert isinstance(store, AzureAISearchVectorStore)
