import logging
from typing import List
from langchain_core.documents import Document
from backend.rag.models import DocumentMetadata, EmbeddedDocument

logger = logging.getLogger(__name__)

class RagEmbedder:
    """
    RAG Embedder for converting documents to embeddings.
    Currently implements placeholder logic for future embedding model integration.
    """

    def __init__(self, embedding_model: str = "placeholder"):
        """
        Initialize the embedder with a specific model.
        
        Args:
            embedding_model: Name of the embedding model to use
        """
        self.embedding_model = embedding_model
        logger.info(f"Initialized RagEmbedder with model: {embedding_model}")

    def _mock_embed(self, text: str) -> List[float]:
        """
        Mock embedding function that returns a simple hash-based vector.
        This is a placeholder for actual embedding model integration.
        """
        import hashlib
        hash_obj = hashlib.md5(text.encode())
        hash_hex = hash_obj.hexdigest()
        
        embedding = []
        for i in range(0, len(hash_hex), 2):
            hex_pair = hash_hex[i:i+2]
            value = int(hex_pair, 16) / 255.0 * 2 - 1
            embedding.append(value)
        
        while len(embedding) < 384:
            embedding.extend(embedding[:min(384-len(embedding), len(embedding))])
        
        return embedding[:384]

    def embed_documents(self, documents: List[DocumentMetadata]) -> List[EmbeddedDocument]:
        """
        Embeds the given documents and returns a list of EmbeddedDocument objects.
        
        Args:
            documents: List of DocumentMetadata objects to embed
            
        Returns:
            List of EmbeddedDocument objects with embeddings
        """
        embedded_documents = []
        
        for doc in documents:
            try:
                content_to_embed = doc.content if doc.content else doc.file_name
                
                embedding_vector = self._mock_embed(content_to_embed)

                embedded_doc = EmbeddedDocument(
                    content=content_to_embed,
                    metadata=doc,
                    embedding=embedding_vector
                )
                embedded_documents.append(embedded_doc)
                logger.info(f"Embedded document: {doc.file_name}")
                
            except Exception as e:
                logger.error(f"Error embedding document {doc.file_name}: {e}")

        logger.info(f"Successfully embedded {len(embedded_documents)} documents")
        return embedded_documents

def embed_documents(documents: List[DocumentMetadata]) -> List[EmbeddedDocument]:
    """
    Convenience function for embedding documents using default embedder.
    """
    embedder = RagEmbedder()
    return embedder.embed_documents(documents)
