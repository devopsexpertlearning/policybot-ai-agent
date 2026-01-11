"""
Unit tests for LLM client with Azure OpenAI.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.llm.llm_client import LLMClient
from app.config import Settings


@pytest.mark.unit
class TestLLMClientAzure:
    """Test LLM client with Azure OpenAI."""
    
    @pytest.fixture
    def azure_settings(self):
        """Settings for Azure environment."""
        return Settings(
            environment="production",
            azure_openai_api_key="test_azure_key",
            azure_openai_endpoint="https://test.openai.azure.com",
            azure_search_api_key="test_search_key",
            azure_search_endpoint="https://test.search.windows.net",
            llm_provider="azure"
        )
    
    @pytest.fixture
    def mock_azure_client(self):
        """Mock Azure OpenAI client."""
        client = Mock()
        
        # Mock chat completion
        mock_message = Mock()
        mock_message.content = "Mocked Azure response"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        
        client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        # Mock embeddings
        mock_embedding = Mock()
        mock_embedding.embedding = [0.1] * 1536
        mock_emb_response = Mock()
        mock_emb_response.data = [mock_embedding]
        
        client.embeddings.create = AsyncMock(return_value=mock_emb_response)
        
        return client

    @pytest.mark.asyncio
    async def test_generate_azure(self, azure_settings, mock_azure_client):
        """Test text generation with Azure."""
        with patch('app.llm.llm_client.settings', azure_settings):
            # Patch the imported class in the module
            with patch('app.llm.llm_client.AsyncAzureOpenAI', return_value=mock_azure_client):
                client = LLMClient()
                assert client.environment == "production"
                assert client.provider == "azure"
                
                response = await client.generate("Test prompt")
                assert response == "Mocked Azure response"
                
                mock_azure_client.chat.completions.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_with_history_azure(self, azure_settings, mock_azure_client):
        """Test generation with history on Azure."""
        with patch('app.llm.llm_client.settings', azure_settings):
            with patch('app.llm.llm_client.AsyncAzureOpenAI', return_value=mock_azure_client):
                client = LLMClient()
                messages = [{"role": "user", "content": "Hi"}]
                
                response = await client.generate_with_history(messages)
                assert response == "Mocked Azure response"
                
                mock_azure_client.chat.completions.create.assert_called_once()
                
    @pytest.mark.asyncio
    async def test_generate_embedding_azure(self, azure_settings, mock_azure_client):
        """Test embedding generation with Azure."""
        with patch('app.llm.llm_client.settings', azure_settings):
            with patch('app.llm.llm_client.AsyncAzureOpenAI', return_value=mock_azure_client):
                client = LLMClient()
                
                embedding = await client.generate_embedding("Test text")
                assert len(embedding) == 1536
                assert embedding[0] == 0.1
                
                mock_azure_client.embeddings.create.assert_called_once()
