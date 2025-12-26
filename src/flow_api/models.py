from dataclasses import dataclass
from datetime import datetime

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