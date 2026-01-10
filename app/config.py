"""
Configuration management with environment-based settings.
Supports both local (Groq + FAISS) and production (Azure OpenAI + Azure AI Search) environments.
"""

import os
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment-based configuration."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ========================
    # ENVIRONMENT
    # ========================
    environment: str = Field(default="local", description="Environment: local or production")
    
    # ========================
    # LOCAL ENVIRONMENT (Google Gemini)
    # ========================
    google_gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key")
    google_gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini chat model")
    google_gemini_embedding_model: str = Field(default="models/embedding-001", description="Gemini embedding model")
    
    # ========================
    # PRODUCTION ENVIRONMENT (Azure OpenAI)
    # ========================
    azure_openai_endpoint: Optional[str] = Field(default=None, description="Azure OpenAI endpoint")
    azure_openai_api_key: Optional[str] = Field(default=None, description="Azure OpenAI API key")
    azure_openai_deployment_name: str = Field(default="gpt-4", description="Azure OpenAI deployment")
    azure_openai_embedding_deployment: str = Field(default="text-embedding-ada-002", description="Azure embedding deployment")
    azure_openai_api_version: str = Field(default="2024-02-01", description="Azure OpenAI API version")
    
    # Azure AI Search
    azure_search_endpoint: Optional[str] = Field(default=None, description="Azure AI Search endpoint")
    azure_search_api_key: Optional[str] = Field(default=None, description="Azure AI Search API key")
    azure_search_index_name: str = Field(default="company-policies", description="Azure Search index name")
    
    # ========================
    # API SETTINGS
    # ========================
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8000, description="API port")
    api_reload: bool = Field(default=False, description="Auto-reload on code changes")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )
    
    # ========================
    # LOGGING
    # ========================
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format: json or text")
    
    # ========================
    # SESSION MANAGEMENT
    # ========================
    session_timeout: int = Field(default=3600, description="Session timeout in seconds")
    max_conversation_history: int = Field(default=10, description="Max messages in conversation history")
    cleanup_interval: int = Field(default=300, description="Session cleanup interval in seconds")
    
    # ========================
    # RAG CONFIGURATION
    # ========================
    chunk_size: int = Field(default=500, description="Text chunk size in tokens")
    chunk_overlap: int = Field(default=50, description="Chunk overlap in tokens")
    top_k_results: int = Field(default=5, description="Number of top results to retrieve")
    similarity_threshold: float = Field(default=0.7, description="Similarity threshold for retrieval")
    
    # ========================
    # LLM CONFIGURATION
    # ========================
    max_tokens: int = Field(default=1000, description="Max tokens in response")
    temperature: float = Field(default=0.7, description="LLM temperature")
    top_p: float = Field(default=0.9, description="LLM top_p")
    
    # ========================
    # VECTOR STORE
    # ========================
    vector_store_path: str = Field(default="./data/vector_stores/faiss_index", description="FAISS index path")
    faiss_index_type: str = Field(default="IndexFlatL2", description="FAISS index type")
    
    # ========================
    # AZURE MONITORING (Production)
    # ========================
    applicationinsights_connection_string: Optional[str] = Field(
        default=None,
        description="Application Insights connection string"
    )
    
    # ========================
    # SECURITY
    # ========================
    api_key_enabled: bool = Field(default=False, description="Enable API key authentication")
    api_key: Optional[str] = Field(default=None, description="API key for authentication")
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_per_minute: int = Field(default=60, description="Rate limit per minute")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment setting."""
        if v not in ["local", "production"]:
            raise ValueError("Environment must be 'local' or 'production'")
        return v
    
    @property
    def is_local(self) -> bool:
        """Check if running in local environment."""
        return self.environment == "local"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def use_gemini(self) -> bool:
        """Check if using Google Gemini."""
        return self.is_local and self.google_gemini_api_key is not None
    
    @property
    def use_azure(self) -> bool:
        """Check if using Azure OpenAI."""
        return self.is_production and self.azure_openai_api_key is not None
    
    @property
    def use_faiss(self) -> bool:
        """Check if using FAISS vector store."""
        return self.is_local
    
    @property
    def use_azure_search(self) -> bool:
        """Check if using Azure AI Search."""
        return self.is_production and self.azure_search_api_key is not None
    
    def validate_config(self) -> None:
        """Validate configuration based on environment."""
        if self.is_local:
            if not self.google_gemini_api_key:
                raise ValueError("GOOGLE_GEMINI_API_KEY is required for local environment")
        
        if self.is_production:
            if not self.azure_openai_api_key:
                raise ValueError("AZURE_OPENAI_API_KEY is required for production environment")
            if not self.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT is required for production environment")
            if not self.azure_search_api_key:
                raise ValueError("AZURE_SEARCH_API_KEY is required for production environment")
            if not self.azure_search_endpoint:
                raise ValueError("AZURE_SEARCH_ENDPOINT is required for production environment")


# Global settings instance
settings = Settings()

# Validate on import
try:
    settings.validate_config()
except ValueError as e:
    print(f"⚠️  Configuration warning: {e}")
    print(f"   Current environment: {settings.environment}")
    print(f"   Please check your .env file")
