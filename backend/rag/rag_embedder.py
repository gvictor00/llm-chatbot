import logging
from typing import List
from rag.models import DocumentMetadata, EmbeddedDocument
from langchain.schema import Document

logger = logging.getLogger(__name__)

class RagEmbedder:

    def __init__(self):
        # Initialize any embedding model or parameters here
        pass

    def embed_documents(self, documents: List[DocumentMetadata]) -> List[EmbeddedDocument]:
        """
        Embeds the given documents and returns a list of Document objects with embeddings.
        """
        embedded_documents = []
        for doc in documents:
            # Here we would normally call an embedding model to get the embedding vector
            embedding_vector = self._mock_embed(doc.content)

            embedded_doc = EmbeddedDocument(
                content=doc.content,
                metadata=doc.metadata,
                embedding=embedding_vector
            )
            embedded_documents.append(embedded_doc)
            logger.info(f"Embedded document: {doc.metadata.get('filename', 'unknown')}")

        return embedded_documents