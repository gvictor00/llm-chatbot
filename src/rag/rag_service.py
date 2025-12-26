import logging
from typing import List, Dict, Any
from src.rag.embedder import RagEmbedder
from src.rag.vector_store import SimpleVectorStore, SimilarityResult
from src.rag.models import EmbeddedDocument, DocumentMetadata

logger = logging.getLogger(__name__)

class RAGService:
    """
    Service class that orchestrates the RAG (Retrieval-Augmented Generation) process.
    """
    
    def __init__(self):
        self.embedder = RagEmbedder()
        self.vector_store = SimpleVectorStore()
        self.is_initialized = False
    
    def initialize_with_documents(self, documents: List[DocumentMetadata]) -> bool:
        """
        Initialize the RAG service with a list of documents.
        This embeds the documents and adds them to the vector store.
        """
        try:
            logger.info(f"Initializing RAG service with {len(documents)} documents")
            
            # Embed all documents
            embedded_docs = self.embedder.embed_documents(documents)
            
            # Add to vector store
            self.vector_store.add_documents(embedded_docs)
            
            self.is_initialized = True
            logger.info("RAG service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            return False
    
    def retrieve_relevant_context(self, query: str, top_k: int = 3) -> List[SimilarityResult]:
        """
        Retrieve relevant document chunks for a given query.
        """
        if not self.is_initialized:
            logger.warning("RAG service not initialized")
            return []
        
        try:
            # Generate embedding for the query
            query_embedding = self.embedder._mock_embed(query)
            
            # Search for similar documents
            results = self.vector_store.similarity_search(query_embedding, top_k)
            
            logger.info(f"Retrieved {len(results)} relevant documents for query")
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant context: {e}")
            return []
    
    def format_context_for_llm(self, similarity_results: List[SimilarityResult]) -> str:
        """
        Format the retrieved documents into a context string for the LLM.
        """
        if not similarity_results:
            return "No relevant context found."
        
        context_parts = []
        for i, result in enumerate(similarity_results, 1):
            doc = result.document
            score = result.similarity_score
            
            context_parts.append(
                f"Document {i} (similarity: {score:.3f}):\n"
                f"Source: {doc.metadata.file_name}\n"
                f"Content: {doc.content[:500]}{'...' if len(doc.content) > 500 else ''}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG service."""
        return {
            "is_initialized": self.is_initialized,
            "total_documents": len(self.vector_store.documents),
            "embedding_dimension": len(self.vector_store.embeddings[0]) if self.vector_store.embeddings else 0
        }
