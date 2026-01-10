"""
Pydantic models for API requests and responses.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request model for /ask endpoint."""
    
    query: str = Field(
        ...,
        description="User query",
        min_length=1,
        max_length=1000,
        examples=["What is the company leave policy?"]
    )
    session_id: Optional[str] = Field(
        default=None,
        description="Session ID for conversation continuity",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )


class Source(BaseModel):
    """Source document information."""
    
    document: str = Field(..., description="Document name")
    page: Optional[int] = Field(None, description="Page number")
    chunk_id: Optional[str] = Field(None, description="Chunk identifier")
    relevance_score: Optional[float] = Field(None, description="Relevance score")


class AskResponse(BaseModel):
    """Response model for /ask endpoint."""
    
    answer: str = Field(..., description="Generated answer")
    source: List[str] = Field(
        default_factory=list,
        description="Source documents used"
    )
    session_id: str = Field(..., description="Session ID")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )
    

class DetailedAskResponse(BaseModel):
    """Detailed response model with sources."""
    
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(
        default_factory=list,
        description="Detailed source information"
    )
    session_id: str = Field(..., description="Session ID")
    method: str = Field(..., description="Method used: direct or rag")
    processing_time: float = Field(..., description="Processing time in seconds")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata"
    )


class HealthResponse(BaseModel):
    """Health check response."""
    
    status: str = Field(..., description="Health status")
    environment: str = Field(..., description="Current environment")
    llm_provider: str = Field(..., description="LLM provider (groq or azure)")
    vector_store: str = Field(..., description="Vector store (faiss or azure_search)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SessionInfo(BaseModel):
    """Session information."""
    
    session_id: str
    created_at: datetime
    last_activity: datetime
    message_count: int
    

class ConversationMessage(BaseModel):
    """Conversation message."""
    
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sources: Optional[List[str]] = Field(default=None, description="Sources used")
