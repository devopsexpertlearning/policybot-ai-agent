"""
Unit tests for FAISS vector store.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from app.rag.vector_store import FAISSVectorStore, get_vector_store
from app.config import Settings


@pytest.mark.unit
class TestFAISSVectorStore:
    """Test FAISS vector store."""
    
    @pytest.fixture
    def faiss_settings(self):
        """Settings for FAISS environment."""
        return Settings(
            environment="local",
            use_gemini=True,
            vector_store_path="test_index",
            use_faiss=True,
            use_azure_search=False
        )
    
    @pytest.fixture
    def mock_faiss(self):
        """Mock faiss module."""
        mock = MagicMock()
        mock.IndexFlatL2.return_value = Mock(ntotal=0)
        return mock

    def test_initialization(self, faiss_settings, mock_faiss):
        """Test initialization."""
        with patch('app.rag.vector_store.settings', faiss_settings):
            with patch('app.rag.vector_store.faiss', mock_faiss):
                with patch('app.rag.vector_store.FAISS_AVAILABLE', True):
                    with patch('os.path.exists', return_value=False):
                        store = FAISSVectorStore(dimension=128)
                        assert store.dimension == 128
                        mock_faiss.IndexFlatL2.assert_called_with(128)

    def test_add_documents(self, faiss_settings, mock_faiss):
        """Test adding documents."""
        with patch('app.rag.vector_store.settings', faiss_settings):
            with patch('app.rag.vector_store.faiss', mock_faiss):
                with patch('app.rag.vector_store.FAISS_AVAILABLE', True):
                    with patch('os.path.exists', return_value=False):
                        store = FAISSVectorStore()
                        index_mock = store.index
                        
                        embeddings = [[0.1, 0.2]]
                        documents = [{"content": "test"}]
                        
                        store.add_documents(embeddings, documents)
                        
                        assert index_mock.add.called
                        assert len(store.metadata_store) == 1

    def test_add_documents_mismatch(self, faiss_settings, mock_faiss):
        """Test error when embeddings count mismatches documents."""
        with patch('app.rag.vector_store.settings', faiss_settings):
            with patch('app.rag.vector_store.faiss', mock_faiss):
                with patch('app.rag.vector_store.FAISS_AVAILABLE', True):
                    with patch('os.path.exists', return_value=False):
                        store = FAISSVectorStore()
                        
                        embeddings = [[0.1, 0.2]]
                        documents = []
                        
                        with pytest.raises(ValueError, match="match"):
                            store.add_documents(embeddings, documents)

    def test_search(self, faiss_settings, mock_faiss):
        """Test searching."""
        with patch('app.rag.vector_store.settings', faiss_settings):
            with patch('app.rag.vector_store.faiss', mock_faiss):
                with patch('app.rag.vector_store.FAISS_AVAILABLE', True):
                    store = FAISSVectorStore()
                    store.index.ntotal = 1
                    store.metadata_store = [{"content": "test"}]
                    
                    # Mock search result: distances, indices
                    store.index.search.return_value = (
                        np.array([[0.1]], dtype=np.float32), 
                        np.array([[0]], dtype=np.int64)
                    )
                    
                    results = store.search([0.1, 0.2])
                    
                    assert len(results) == 1
                    assert results[0]["content"] == "test"
                    assert "similarity_score" in results[0]

    def test_search_empty(self, faiss_settings, mock_faiss):
        """Test search on empty index."""
        with patch('app.rag.vector_store.settings', faiss_settings):
            with patch('app.rag.vector_store.faiss', mock_faiss):
                with patch('app.rag.vector_store.FAISS_AVAILABLE', True):
                    store = FAISSVectorStore()
                    store.index.ntotal = 0
                    
                    results = store.search([0.1, 0.2])
                    assert len(results) == 0

    def test_factory_faiss(self, faiss_settings, mock_faiss):
        """Test factory returns FAISS store."""
        with patch('app.rag.vector_store.settings', faiss_settings):
            with patch('app.rag.vector_store.faiss', mock_faiss):
                with patch('app.rag.vector_store.FAISS_AVAILABLE', True):
                    store = get_vector_store()
                    assert isinstance(store, FAISSVectorStore)
