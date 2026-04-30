"""Custom exceptions for RAG system."""


class RAGException(Exception):
    """Base exception for RAG system."""

    def __init__(self, message: str, code: str = "RAG_ERROR"):
        """Initialize exception.

        Args:
            message: Error message
            code: Error code for logging and tracking
        """
        self.message = message
        self.code = code
        super().__init__(self.message)


class ConfigurationError(RAGException):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "CONFIG_ERROR")


class DocumentLoadError(RAGException):
    """Raised when document loading fails."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "DOCUMENT_LOAD_ERROR")


class EmbeddingError(RAGException):
    """Raised when embedding generation fails."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "EMBEDDING_ERROR")


class VectorStoreError(RAGException):
    """Raised when vector store operations fail."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "VECTOR_STORE_ERROR")


class RetrievalError(RAGException):
    """Raised when document retrieval fails."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "RETRIEVAL_ERROR")


class GenerationError(RAGException):
    """Raised when LLM generation fails."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "GENERATION_ERROR")


class ValidationError(RAGException):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "VALIDATION_ERROR")


class PipelineError(RAGException):
    """Raised when pipeline operations fail."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "PIPELINE_ERROR")


class APIError(RAGException):
    """Raised when API operations fail."""

    def __init__(self, message: str):
        """Initialize exception."""
        super().__init__(message, "API_ERROR")
