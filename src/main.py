from fastapi import FastAPI, HTTPException
import logging
import os
from src.rag.loader import RagLoader
from src.rag.embedder import embed_documents
from src.config.config import config
from src.flow_api.flow_client import flow_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CI&T Flow API Integration")

@app.get("/", summary="Health Check Endpoint")
def read_root():
    return {"message": "CI&T Flow API Integration is running."}

@app.get("/health", summary="Check CI&T Flow API connection")
def health():
    try:
        if flow_client.health_check():
            return {"status": "ok", "message": "Connected to CI&T Flow API"}
        return {"status": "error", "message": "Failed to connect to CI&T Flow API"}
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "message": "Health check failed"}

@app.get("/load_documents", summary="Load RAG Documents from Folder")
def load_documents_endpoint():
    """
    Load documents from the configured folder path and return metadata.
    Supports text and PDF files with optional embedding processing.
    """
    folder_path = config.rag.documents_path
    logger.info(f"Loading documents from: {folder_path}")
    if not folder_path or not os.path.isdir(folder_path):
        error_msg = f"Invalid document folder path in config: {folder_path}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

    try:
        rag_loader = RagLoader(
            folder_path=folder_path,
            recurse=config.rag.recurse_folders,
            supported_file_types=config.rag.supported_file_types
        )

        documents = rag_loader.load_documents_from_folder()
        if not documents:
            logger.warning("No documents found in the specified folder")
            return {
                "document_count": 0,
                "message": "No supported documents found in folder",
                "folder_path": folder_path
            }

        try:
            embedded_documents = embed_documents(documents)
            logger.info(f"Successfully processed embeddings for {len(embedded_documents)} documents")
        except Exception as e:
            logger.warning(f"Embedding processing failed: {e}")
            embedded_documents = []

        document_summaries = [
            {
                "file_name": doc.file_name,
                "file_size": doc.file_size,
                "file_extension": doc.file_extension,
                "file_relative_path": doc.file_relative_path,
                "content_length": len(doc.content) if doc.content else 0,
                "sha256_hash": doc.sha256_hash[:16] + "..."
            }
            for doc in documents
        ]

        logger.info(f"Successfully loaded {len(documents)} documents")
        return {
            "document_count": len(documents),
            "embedded_count": len(embedded_documents),
            "documents": document_summaries,
            "folder_path": folder_path,
            "supported_types": config.rag.supported_file_types
        }

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to load documents")

@app.get("/documents/stats", summary="Get document loading statistics")
def get_document_stats():
    """
    Get statistics about the document folder without loading all documents.
    """
    folder_path = config.rag.documents_path

    if not folder_path or not os.path.isdir(folder_path):
        raise HTTPException(status_code=400, detail="Invalid document folder path")

    try:
        stats = {
            "folder_path": folder_path,
            "supported_types": config.rag.supported_file_types,
            "recurse_enabled": config.rag.recurse_folders,
            "total_files": 0,
            "supported_files": 0,
            "file_type_breakdown": {}
        }

        for root, _, files in os.walk(folder_path):
            for file_name in files:
                stats["total_files"] += 1
                ext = os.path.splitext(file_name)[1].lower()

                if ext in config.rag.supported_file_types:
                    stats["supported_files"] += 1

                stats["file_type_breakdown"][ext] = stats["file_type_breakdown"].get(ext, 0) + 1

            if not config.rag.recurse_folders:
                break

        return stats

    except Exception as e:
        logger.error(f"Error getting document stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get document statistics")
