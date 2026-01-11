"""
Unit tests for LLM client with mocked responses.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.llm.llm_client import LLMClient
from app.config import Settings


@pytest.mark.unit
class TestLLMClient:
    """Test LLM client functionality with mocks."""
    
    @pytest.fixture
    def gemini_settings(self):
        """Settings for Gemini environment."""
        return Settings(
            environment="local",
            google_gemini_api_key="test_gemini_key"
        )
    
    @pytest.fixture
    def azure_settings(self):
        """Settings for Azure environment."""
        return Settings(
            environment="production",
            azure_openai_api_key="test_azure_key",
            azure_openai_endpoint="https://test.openai.azure.com",
            azure_search_api_key="test_search_key",
            azure_search_endpoint="https://test.search.windows.net"
        )
    
    @pytest.fixture
    def mock_gemini_model(self):
        """Mock Google Gemini model."""
        model = Mock()
        
        # Mock successful response
        mock_response = Mock()
        mock_candidate = Mock()
        mock_part = Mock()
        mock_part.text = "Mocked Gemini response"
        mock_candidate.content.parts = [mock_part]
        mock_response.candidates = [mock_candidate]
        
        # Make sure generate_content can be called in thread
        model.generate_content = Mock(return_value=mock_response)
        
        return model
    
    @pytest.fixture
    def mock_azure_client(self):
        """Mock Azure OpenAI client."""
        client = Mock()
        response = Mock()
        response.choices = [Mock(message=Mock(content="Mocked Azure response"))]
        client.chat.completions.create = AsyncMock(return_value=response)
        return client
    
    def test_client_initialization_gemini(self, gemini_settings):
        """Test client initializes with Gemini."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.GenerativeModel'):
                client = LLMClient()
                assert client.environment == "local"
    
    def test_client_initialization_azure(self, azure_settings):
        """Test client initializes with Azure."""
        with patch('app.llm.llm_client.settings', azure_settings):
            with patch('openai.AsyncAzureOpenAI'):
                client = LLMClient()
                assert client.environment == "production"
    
    @pytest.mark.asyncio
    async def test_generate_with_gemini(self, gemini_settings, mock_gemini_model):
        """Test text generation with Gemini."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                client = LLMClient()
                response = await client.generate("Test prompt")
                assert response == "Mocked Gemini response"
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, gemini_settings, mock_gemini_model):
        """Test generation with system prompt."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                client = LLMClient()
                response = await client.generate(
                    "Test prompt",
                    system_prompt="You are a helpful assistant"
                )
                assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_generate_with_history(self, gemini_settings, mock_gemini_model):
        """Test generation with conversation history."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                client = LLMClient()
                messages = [
                    {"role": "user", "content": "Hello"},
                    {"role": "assistant", "content": "Hi!"},
                    {"role": "user", "content": "How are you?"}
                ]
                response = await client.generate_with_history(messages)
                assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_generate_embedding_gemini(self, gemini_settings):
        """Test embedding generation with Gemini."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            # Mock genai.embed_content directly (not async)
            with patch('google.generativeai.embed_content', return_value={"embedding": [0.1] * 3072}) as mock_embed:
                client = LLMClient()
                embedding = await client.generate_embedding("Test text")
                assert len(embedding) == 3072
                assert all(isinstance(x, float) for x in embedding)
    
    @pytest.mark.asyncio
    async def test_generate_embeddings_batch(self, gemini_settings):
        """Test batch embedding generation."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.embed_content', return_value={"embedding": [0.1] * 3072}) as mock_embed:
                client = LLMClient()
                texts = ["text1", "text2", "text3"]
                embeddings = await client.generate_embeddings_batch(texts)
                assert len(embeddings) == 3
                assert all(len(emb) == 3072 for emb in embeddings)
    
    def test_token_counting(self, gemini_settings):
        """Test token counting."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('tiktoken.encoding_for_model') as mock_encoding:
                mock_enc = Mock()
                mock_enc.encode = Mock(return_value=[1, 2, 3, 4])
                mock_encoding.return_value = mock_enc
                
                client = LLMClient()
                count = client.count_tokens("This is a test")
                assert count == 4
    
    @pytest.mark.asyncio
    async def test_generate_with_temperature(self, gemini_settings, mock_gemini_model):
        """Test generation with custom temperature."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                client = LLMClient()
                response = await client.generate("Test", temperature=0.3)
                assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_generate_with_max_tokens(self, gemini_settings, mock_gemini_model):
        """Test generation with max tokens limit."""
        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.GenerativeModel', return_value=mock_gemini_model):
                client = LLMClient()
                response = await client.generate("Test", max_tokens=500)
                assert isinstance(response, str)
