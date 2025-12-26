from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChatMessage(BaseModel):
    """Model for incoming chat messages."""
    message: str
    model: Optional[str] = None  # Allow model selection
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7
    top_k_documents: Optional[int] = 3

class ChatResponse(BaseModel):
    """Model for chat responses."""
    response: str
    success: bool
    context_used: List[Dict[str, Any]]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class RAGStats(BaseModel):
    """Model for RAG service statistics."""
    is_initialized: bool
    total_documents: int
    embedding_dimension: int
    last_updated: Optional[str] = None
