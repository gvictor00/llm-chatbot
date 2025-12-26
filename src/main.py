from fastapi import FastAPI, HTTPException
import logging
import os
from datetime import datetime
from src.rag.loader import RagLoader
from src.rag.rag_service import RAGService
from src.flow_api.llm_client import llm_client, LLMRequest
from src.config.config import config
from src.flow_api.flow_client import flow_client
from src.api.chat_models import ChatMessage, ChatResponse, RAGStats

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="CI&T Flow API Integration with RAG")

rag_service = RAGService()

@app.get("/", summary="Health Check Endpoint")
def read_root():
    return {"message": "CI&T Flow API Integration with RAG is running."}

@app.get("/health", summary="Check CI&T Flow API connection")
def health():
    try:
        if flow_client.health_check():
            return {"status": "ok", "message": "Connected to CI&T Flow API"}
        return {"status": "error", "message": "Failed to connect to CI&T Flow API"}
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "message": "Health check failed"}

@app.get("/models", summary="Get available LLM models")
def get_available_models():
    try:
        models_details = llm_client.get_models_details()
        model_names = llm_client.get_available_models()
        default_model = llm_client.get_default_model()

        return {
            "available_models": model_names,
            "default_model": default_model,
            "total_models": len(model_names),
            "models_details": models_details,
            "success": True,
            "message": "Models retrieved successfully" if models_details else "Using fallback models (API may not be accessible)"
        }
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        return {
            "available_models": ["llama-2-7b"],
            "default_model": "llama-2-7b",
            "total_models": 1,
            "models_details": [],
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve models, using fallback"
        }

@app.get("/models/refresh", summary="Refresh available models cache")
def refresh_models():
    try:
        llm_client._models_cache = None
        models_data = llm_client.fetch_available_models()
        model_names = llm_client.get_available_models()

        return {
            "message": "Models cache refreshed successfully",
            "available_models": model_names,
            "total_models": len(model_names),
            "success": True,
            "models_fetched": len(models_data) if models_data else 0
        }
    except Exception as e:
        logger.error(f"Error refreshing models: {e}")
        return {
            "message": "Failed to refresh models cache",
            "success": False,
            "error": str(e)
        }

@app.get("/load_documents", summary="Load RAG Documents from Folder")
def load_documents_endpoint():
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
                "folder_path": folder_path,
                "rag_initialized": False
            }

        rag_initialized = rag_service.initialize_with_documents(documents)

        document_summaries = [
            {
                "file_name": doc.file_name,
                "file_size": doc.file_size,
                "file_extension": doc.file_extension,
                "content_length": len(doc.content) if doc.content else 0
            }
            for doc in documents
        ]

        logger.info(f"Successfully loaded {len(documents)} documents and initialized RAG service")
        return {
            "document_count": len(documents),
            "documents": document_summaries,
            "folder_path": folder_path,
            "rag_initialized": rag_initialized,
            "message": "Documents loaded and RAG service initialized successfully"
        }

    except Exception as e:
        logger.error(f"Error loading documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load documents: {str(e)}")

@app.post("/chat", summary="Send message to RAG-enabled chatbot")
def chat_endpoint(chat_message: ChatMessage) -> ChatResponse:
    try:
        if not rag_service.is_initialized:
            return ChatResponse(
                response="RAG service is not initialized. Please load documents first using /load_documents endpoint.",
                success=False,
                context_used=[],
                error_message="RAG service not initialized"
            )

        logger.info(f"Processing chat message: {chat_message.message[:100]}...")

        similarity_results = rag_service.retrieve_relevant_context(
            chat_message.message,
            top_k=chat_message.top_k_documents
        )

        context = rag_service.format_context_for_llm(similarity_results)

        llm_request = LLMRequest(
            message=chat_message.message,
            context=context,
            model=chat_message.model,
            max_tokens=chat_message.max_tokens,
            temperature=chat_message.temperature
        )

        llm_response = llm_client.generate_response(llm_request)

        context_used = [
            {
                "file_name": result.document.metadata.file_name,
                "similarity_score": result.similarity_score,
                "content_preview": result.document.content[:200] + "..." if len(result.document.content) > 200 else result.document.content
            }
            for result in similarity_results
        ]

        if not llm_response.success:
            error_details = llm_response.error_message
            if llm_response.flow_error:
                error_details = f"Flow API Error: {llm_response.flow_error}"

            logger.error(f"LLM request failed: {error_details}")

            fallback_response = _generate_fallback_response(context, chat_message.message)

            return ChatResponse(
                response=fallback_response,
                success=False,
                context_used=context_used,
                error_message=error_details,
                metadata={
                    "documents_retrieved": len(similarity_results),
                    "query_length": len(chat_message.message),
                    "timestamp": datetime.now().isoformat(),
                    "model_requested": chat_message.model,
                    "model_used": llm_response.model_used,
                    "fallback_used": True
                }
            )

        return ChatResponse(
            response=llm_response.response,
            success=True,
            context_used=context_used,
            error_message=None,
            metadata={
                "documents_retrieved": len(similarity_results),
                "query_length": len(chat_message.message),
                "timestamp": datetime.now().isoformat(),
                "model_requested": chat_message.model,
                "model_used": llm_response.model_used
            }
        )

    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            response="I apologize, but an error occurred while processing your message.",
            success=False,
            context_used=[],
            error_message=str(e)
        )

def _generate_fallback_response(context: str, user_message: str) -> str:
    if context and context.strip() != "No relevant context found.":
        return f"""I found some relevant information in the documents, but I'm currently unable to process it through the AI service.

Here's what I found related to your question "{user_message}":

{context[:1000]}{'...' if len(context) > 1000 else ''}

Please try again later or contact support if the issue persists."""
    else:
        return f"""I apologize, but I'm currently unable to process your question "{user_message}" due to a service issue. Please try again later or contact support if the issue persists."""

@app.get("/rag/stats", summary="Get RAG service statistics", response_model=RAGStats)
def get_rag_stats():
    try:
        stats = rag_service.get_stats()
        return RAGStats(
            is_initialized=stats["is_initialized"],
            total_documents=stats["total_documents"],
            embedding_dimension=stats["embedding_dimension"],
            last_updated=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Error getting RAG stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get RAG statistics")

@app.get("/documents/stats", summary="Get document loading statistics")
def get_document_stats():
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
