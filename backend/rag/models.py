from dataclasses import dataclass
from typing import Optional, List

@dataclass
class DocumentMetadata:
    """Metadata for a document used in RAG models."""
    file_path: str
    file_name: str
    file_size: int
    file_extension: str
    file_last_modified: str
    file_relative_path: str
    sha256_hash: str
    content: Optional[str] = None  # Add content field

@dataclass
class RAGModelConfig:
    """Configuration for RAG models."""
    model_name: str
    embedding_model: str
    retrieval_method: str
    top_k: int
    chunk_size: int
    chunk_overlap: int

@dataclass
class EmbeddedDocument:
    """Represents an embedded document."""
    content: str
    embedding: List[float]
    metadata: DocumentMetadata

@dataclass
class RetrievalResult:
    """Result from a retrieval operation."""
    document: EmbeddedDocument
    score: float