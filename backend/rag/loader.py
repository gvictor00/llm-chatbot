import os
import hashlib
import logging
from typing import List
from pathlib import Path
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_core.documents import Document
from backend.rag.models import DocumentMetadata

logger = logging.getLogger(__name__)

class RagLoader:
    """
    RAG Document Loader for loading and processing documents from a folder.
    Supports text and PDF files with metadata extraction.
    """

    def __init__(self, folder_path: str, supported_file_types: List[str] = None, recurse: bool = False):
        """
        Initialize the RAG loader.
        
        Args:
            folder_path: Path to the folder containing documents
            supported_file_types: List of supported file extensions
            recurse: Whether to recursively search subfolders
        """
        self.folder_path = folder_path
        self.supported_file_types = supported_file_types if supported_file_types is not None else [".txt", ".pdf"]
        self.recurse = recurse

        if not self._validate_folder():
            raise ValueError(f"Invalid folder path: {self.folder_path}")

    def _validate_folder(self) -> bool:
        """
        Validates if the folder path exists and is a directory.
        """
        if not os.path.exists(self.folder_path):
            logger.error(f"Folder path {self.folder_path} does not exist.")
            return False
        if not os.path.isdir(self.folder_path):
            logger.error(f"Path {self.folder_path} is not a directory.")
            return False
        return True

    def _compute_sha256(self, file_path: str) -> str:
        """
        Computes SHA256 hash of a file for integrity checking.
        """
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Error computing SHA256 for {file_path}: {e}")
            return ""
    
    def _validate_file_type(self, file_name: str) -> bool:
        """
        Validates if the file type is supported.
        """
        file_extension = os.path.splitext(file_name)[1].lower()
        return file_extension in self.supported_file_types

    def _load_document_content(self, file_path: str) -> List[Document]:
        """
        Load document content using appropriate LangChain loader.
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_extension == ".txt":
                loader = TextLoader(file_path, encoding='utf-8')
                return loader.load()
            elif file_extension == ".pdf":
                try:
                    loader = PyPDFLoader(file_path)
                    return loader.load()
                except ImportError as e:
                    logger.error(f"PDF processing requires 'pypdf' package. Install with: pip install pypdf")
                    raise e
                except Exception as e:
                    logger.error(f"Error processing PDF {file_path}: {e}")
                    # Return empty document with error message as content
                    return [Document(
                        page_content=f"Error processing PDF: {str(e)}",
                        metadata={"source": file_path, "error": True}
                    )]
            else:
                logger.warning(f"Unsupported file type: {file_extension}")
                return []
        except Exception as e:
            logger.error(f"Error loading content from {file_path}: {e}")
            return []

    def load_documents_from_folder(self) -> List[DocumentMetadata]:
        """
        Loads documents from the specified folder and returns their metadata with content.
        """
        documents = []
        
        # Use os.walk for recursive search or os.listdir for non-recursive
        if self.recurse:
            file_iterator = os.walk(self.folder_path)
        else:
            # For non-recursive, create a single iteration
            try:
                files = os.listdir(self.folder_path)
                file_iterator = [(self.folder_path, [], files)]
            except OSError as e:
                logger.error(f"Error accessing folder {self.folder_path}: {e}")
                return documents

        for root, _, files in file_iterator:
            for file_name in files:
                file_path = os.path.join(root, file_name)

                if not os.path.isfile(file_path):
                    continue
                
                if not self._validate_file_type(file_name):
                    logger.debug(f"Unsupported file type for file {file_name}. Skipping.")
                    continue

                try:
                    # Get file statistics
                    stat = os.stat(file_path)
                    
                    # Load document content
                    langchain_docs = self._load_document_content(file_path)
                    content = ""
                    if langchain_docs:
                        content = "\n".join([doc.page_content for doc in langchain_docs])

                    # Create metadata object
                    metadata = DocumentMetadata(
                        file_path=file_path,
                        file_name=file_name,
                        file_size=stat.st_size,
                        file_extension=os.path.splitext(file_name)[1],
                        file_last_modified=str(stat.st_mtime),
                        file_relative_path=os.path.relpath(file_path, self.folder_path),
                        sha256_hash=self._compute_sha256(file_path),
                        content=content  # Add content to metadata
                    )
                    documents.append(metadata)
                    logger.info(f"Successfully loaded document: {file_name}")
                    
                except Exception as e:
                    logger.error(f"Error loading document {file_path}: {e}")

        logger.info(f"Loaded {len(documents)} documents from {self.folder_path}")
        return documents
