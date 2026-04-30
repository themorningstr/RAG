"""RAG Application Package - Production Grade."""

# Setup logging at package load time
from rag_app.logger import setup_root_logger, disable_external_logging

setup_root_logger()
disable_external_logging()

# Import core components
from rag_app.api import create_app
from rag_app.config import get_settings
from rag_app.embeddings import EmbeddingModel
from rag_app.exceptions import RAGException
from rag_app.generation import OllamaLLM
from rag_app.ingestion import (
    Document,
    TextChunker,
    UnifiedDocumentLoader,
)
from rag_app.logger import get_logger
from rag_app.pipeline import RAGPipeline
from rag_app.retrieval import Retriever
from rag_app.vectorstore import VectorStoreFactory

__version__ = "2.0.0"
__all__ = [
    "RAGPipeline",
    "EmbeddingModel",
    "OllamaLLM",
    "VectorStoreFactory",
    "Retriever",
    "UnifiedDocumentLoader",
    "TextChunker",
    "Document",
    "create_app",
    "get_settings",
    "get_logger",
    "RAGException",
]
