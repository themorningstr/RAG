"""Production-grade configuration settings for RAG application."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings

from rag_app.logger import get_logger

logger = get_logger(__name__)


class Settings(BaseSettings):
    """Production-grade application settings with validation."""

    # ==================== Paths ====================
    DATA_FOLDER: str = "./data"
    SOURCE_FOLDER: str = "./data/source"
    LOGS_FOLDER: str = "./logs"

    # Vector Store
    VECTOR_STORE_TYPE: str = "chroma"  # "chroma", "faiss", "weaviate", "pinecone", "qdrant", "astradb"
    VECTOR_STORE_PATH: str = "./data/vector_store"

    # ==================== Vector Store Specific Settings ====================
    # Chroma
    CHROMA_COLLECTION_NAME: str = "documents"

    # FAISS
    FAISS_COLLECTION_NAME: str = "documents"

    # Weaviate
    WEAVIATE_URL: str = "http://localhost:8080"
    WEAVIATE_API_KEY: Optional[str] = None

    # Pinecone
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-west1-gcp"
    PINECONE_INDEX_NAME: str = "documents"

    # Qdrant
    QDRANT_URL: Optional[str] = None  # Remote Qdrant URL (optional, defaults to local)
    QDRANT_API_KEY: Optional[str] = None

    # Astra DB (DataStax Astra)
    ASTRA_DB_ID: Optional[str] = None
    ASTRA_DB_REGION: str = "us-east1"
    ASTRA_DB_TOKEN: Optional[str] = None

    # ==================== Embeddings ====================
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DEVICE: str = "cpu"  # "cpu" or "cuda" for GPU
    EMBEDDING_BATCH_SIZE: int = 32
    EMBEDDING_DIMENSION: int = 384  # Default for all-MiniLM-L6-v2

    # ==================== LLM Configuration ====================
    LLM_PROVIDER: str = "ollama"  # "ollama", "huggingface", etc.
    LLM_MODEL: str = "mistral"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 512
    LLM_TIMEOUT: int = 120  # Timeout in seconds

    # ==================== Text Processing ====================
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    MIN_CHUNK_SIZE: int = 50
    MAX_CHUNK_SIZE: int = 2000

    # ==================== Retrieval ====================
    TOP_K: int = 3
    MIN_TOP_K: int = 1
    MAX_TOP_K: int = 20

    # ==================== API ====================
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    API_WORKERS: int = 4
    API_LOG_LEVEL: str = "info"

    # ==================== Processing ====================
    BATCH_SIZE: int = 32
    MAX_FILE_SIZE_MB: int = 100
    MAX_WORKERS: int = 4

    # ==================== Logging ====================
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    LOG_FILE_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_FILE_BACKUP_COUNT: int = 5

    class Config:
        """Pydantic configuration."""

        env_file = ".env"
        case_sensitive = True
        validate_assignment = True


def get_settings() -> Settings:
    """Get application settings with validation.

    Returns:
        Settings instance

    Raises:
        Exception: If settings are invalid
    """
    try:
        settings = Settings()
        logger.debug("Settings loaded successfully")
        return settings
    except Exception as e:
        logger.error(f"Failed to load settings: {str(e)}", exc_info=True)
        raise


def initialize_directories() -> None:
    """Initialize required directories.

    Raises:
        Exception: If directory creation fails
    """
    try:
        settings = get_settings()

        directories = [
            settings.DATA_FOLDER,
            settings.SOURCE_FOLDER,
            settings.LOGS_FOLDER,
            settings.VECTOR_STORE_PATH,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

        logger.info("All required directories initialized")

    except Exception as e:
        logger.error(f"Failed to initialize directories: {str(e)}", exc_info=True)
        raise


# Initialize settings and directories on module load
try:
    settings = get_settings()
    initialize_directories()
except Exception as e:
    logger.critical(f"Failed to initialize RAG application: {str(e)}")
    raise
