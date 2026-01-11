"""
Unit tests for LLM client streaming.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.llm.llm_client import LLMClient
from app.config import Settings


@pytest.mark.unit
class TestLLMClientStreaming:
    """Test LLM client streaming."""
    
    @pytest.fixture
    def gemini_settings(self):
        """Settings for Gemini environment."""
        return Settings(
            environment="local",
            google_gemini_api_key="test_gemini_key",
            llm_provider="gemini"
        )

    @pytest.mark.asyncio
    async def test_generate_stream_gemini(self, gemini_settings):
        """Test streaming with Gemini."""
        mock_chunk1 = Mock()
        mock_chunk1.text = "Hello"
        mock_chunk2 = Mock()
        mock_chunk2.text = " World"
        
        mock_response = [mock_chunk1, mock_chunk2]
        
        mock_model = Mock()
        # Mock generate_content (called in thread)
        mock_model.generate_content = Mock(return_value=mock_response)

        with patch('app.llm.llm_client.settings', gemini_settings):
            with patch('google.generativeai.GenerativeModel', return_value=mock_model):
                client = LLMClient()
                
                chunks = []
                async for chunk in client.stream_generate("Test"):
                    chunks.append(chunk)
                
                assert len(chunks) == 2
                assert chunks[0] == "Hello"
                assert chunks[1] == " World"
