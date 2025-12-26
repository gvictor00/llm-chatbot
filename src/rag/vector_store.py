import logging
from typing import List, Tuple
import numpy as np
from dataclasses import dataclass
from src.rag.models import EmbeddedDocument, DocumentMetadata

logger = logging.getLogger(__name__)

@dataclass
class SimilarityResult:
    """Result from similarity search."""
    document: EmbeddedDocument
    similarity_score: float

class SimpleVectorStore:
    """
    Simple in-memory vector store for document retrieval.
    In production, consider using Chroma, Pinecone, or FAISS.
    """
    
    def __init__(self):
        self.documents: List[EmbeddedDocument] = []
        self.embeddings: List[List[float]] = []
        
    def add_documents(self, documents: List[EmbeddedDocument]):
        """Add embedded documents to the vector store."""
        for doc in documents:
            self.documents.append(doc)
            self.embeddings.append(doc.embedding)
        logger.info(f"Added {len(documents)} documents to vector store. Total: {len(self.documents)}")
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 3) -> List[SimilarityResult]:
        """
        Find the most similar documents to the query embedding.
        Uses cosine similarity for comparison.
        """
        if not self.embeddings:
            logger.warning("No documents in vector store for similarity search")
            return []
        
        similarities = []
        query_array = np.array(query_embedding)
        
        for i, doc_embedding in enumerate(self.embeddings):
            doc_array = np.array(doc_embedding)
            
            # Cosine similarity calculation
            dot_product = np.dot(query_array, doc_array)
            norm_query = np.linalg.norm(query_array)
            norm_doc = np.linalg.norm(doc_array)
            
            if norm_query == 0 or norm_doc == 0:
                similarity = 0.0
            else:
                similarity = dot_product / (norm_query * norm_doc)
            
            similarities.append(SimilarityResult(
                document=self.documents[i],
                similarity_score=float(similarity)
            ))
        
        # Sort by similarity score (descending) and return top_k
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)
        return similarities[:top_k]
    
    def clear(self):
        """Clear all documents from the vector store."""
        self.documents.clear()
        self.embeddings.clear()
        logger.info("Vector store cleared")
