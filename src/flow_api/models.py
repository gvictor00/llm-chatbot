from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

@dataclass
class FlowAccessToken:
    access_token: str
    expires_in: int
    expiration_timestamp: float = 0  # Optional field for token expiration time

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            access_token=data.get("access_token", ""),
            expires_in=data.get("expires_in", 0),
            expiration_timestamp=datetime.now().timestamp() + data.get("expires_in", 0)
        )
    
    @classmethod
    def empty(cls):
        return cls(access_token="", expires_in=0)
    
@dataclass
class HealthStatus:
    result: str
    timestamp: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            result=data.get("result", ""),
            timestamp=data.get("timestamp", "")
        )
    
    @classmethod
    def empty(cls):
        return cls(result="", timestamp="")

@dataclass
class FlowAPIError:
    """Represents an error response from Flow API."""
    timestamp: str
    path: str
    message: str
    error: str
    status_code: int

    @classmethod
    def from_response(cls, response_data: Dict[str, Any], status_code: int) -> 'FlowAPIError':
        """Create FlowAPIError from API response."""
        return cls(
            timestamp=response_data.get("timestamp", datetime.now().isoformat()),
            path=response_data.get("path", "unknown"),
            message=response_data.get("message", "Unknown error"),
            error=response_data.get("error", "API Error"),
            status_code=status_code
        )

    def __str__(self) -> str:
        return f"FlowAPIError({self.status_code}): {self.message} at {self.path}"

@dataclass
class SupportedModel:
    """Represents a supported LLM model."""
    name: str
    display_name: str
    max_tokens: int
    supports_streaming: bool = False

@dataclass
class LLMCapabilities:
    """Represents the capabilities of the LLM service."""
    supported_models: List[SupportedModel]
    default_model: str
    max_context_length: int

    @classmethod
    def get_default_capabilities(cls) -> 'LLMCapabilities':
        """Get default capabilities when API discovery fails."""
        return cls(
            supported_models=[
                SupportedModel("llama-2", "Llama 2", 4096),
                SupportedModel("claude", "Claude", 8192),
                SupportedModel("gemini", "Gemini", 4096),
            ],
            default_model="llama-2",
            max_context_length=4096
        )
