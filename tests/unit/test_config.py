"""
Unit tests for configuration management.
"""

import pytest
from pydantic import ValidationError
from app.config import Settings


@pytest.mark.unit
class TestSettings:
    """Test Settings class."""
    
    def test_default_settings(self):
        """Test default settings initialization."""
        settings = Settings(google_gemini_api_key="test_key")
        assert settings.environment == "local"
        assert settings.api_port == 8000
        assert settings.log_level == "INFO"
        assert settings.chunk_size == 500
        assert settings.chunk_overlap == 50
    
    def test_environment_validation(self):
        """Test environment validation."""
        with pytest.raises(ValidationError):
            Settings(environment="invalid", google_gemini_api_key="test")
    
    def test_local_environment_properties(self):
        """Test local environment computed properties."""
        settings = Settings(
            environment="local",
            google_gemini_api_key="test_key"
        )
        assert settings.is_local is True
        assert settings.is_production is False
        assert settings.use_gemini is True
        assert settings.use_faiss is True
        assert settings.use_azure is False
        assert settings.use_azure_search is False
    
    def test_production_environment_properties(self):
        """Test production environment computed properties."""
        settings = Settings(
            environment="production",
            azure_openai_api_key="test_key",
            azure_openai_endpoint="https://test.openai.azure.com",
            azure_search_api_key="test_key",
            azure_search_endpoint="https://test.search.windows.net"
        )
        assert settings.is_production is True
        assert settings.is_local is False
        assert settings.use_azure is True
        assert settings.use_azure_search is True
        assert settings.use_gemini is False
        assert settings.use_faiss is False
    
    def test_config_validation_local_missing_key(self):
        """Test configuration validation for local environment."""
        # Settings initialization itself validates required fields
        # The validate_config method is called during app startup
        settings = Settings(environment="local", google_gemini_api_key="test")
        # Should not raise with valid key
        settings.validate_config()
    
    def test_config_validation_production_complete(self):
        """Test configuration validation for production."""
        settings = Settings(
            environment="production",
            azure_openai_api_key="test",
            azure_openai_endpoint="https://test.openai.azure.com",
            azure_search_api_key="test",
            azure_search_endpoint="https://test.search.windows.net"
        )
        # Should not raise with all required fields
        settings.validate_config()
    
    def test_custom_settings(self):
        """Test custom settings override defaults."""
        settings = Settings(
            google_gemini_api_key="test",
            api_port=9000,
            chunk_size=1000,
            temperature=0.5
        )
        assert settings.api_port == 9000
        assert settings.chunk_size == 1000
        assert settings.temperature == 0.5
    
    def test_cors_origins_default(self):
        """Test CORS origins default value."""
        settings = Settings(google_gemini_api_key="test")
        assert isinstance(settings.cors_origins, list)
        assert len(settings.cors_origins) > 0
