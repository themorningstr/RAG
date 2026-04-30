"""Vector store factory for switching between backends."""

from typing import Optional

from rag_app.exceptions import VectorStoreError
from rag_app.logger import get_logger

from .abstract_store import VectorStoreBase
from .chroma_store import ChromaVectorStore
from .faiss_store import FAISSVectorStore
from .weaviate_store import WeaviateVectorStore
from .pinecone_store import PineconeVectorStore
from .qdrant_store import QdrantVectorStore
from .astra_store import AstraDBVectorStore

logger = get_logger(__name__)


class VectorStoreFactory:
    """Factory for creating vector store instances."""

    # Mapping of backend names to implementations
    BACKENDS = {
        "chroma": ChromaVectorStore,
        "faiss": FAISSVectorStore,
        "weaviate": WeaviateVectorStore,
        "pinecone": PineconeVectorStore,
        "qdrant": QdrantVectorStore,
        "astradb": AstraDBVectorStore,
    }

    @classmethod
    def create(
        cls,
        backend: str = "chroma",
        persist_dir: str = "./data/vector_store",
        collection_name: str = "documents",
    ) -> VectorStoreBase:
        """Create a vector store instance.

        Args:
            backend: Backend name (e.g., 'chroma', 'weaviate')
            persist_dir: Directory for persistence
            collection_name: Name of the collection

        Returns:
            Vector store instance

        Raises:
            VectorStoreError: If backend is not supported

        Example:
            >>> # Use Chroma
            >>> store = VectorStoreFactory.create("chroma")
            >>> 
            >>> # Switch to Weaviate (when implemented)
            >>> store = VectorStoreFactory.create("weaviate")
        """
        backend = backend.lower()

        if backend not in cls.BACKENDS:
            available = ", ".join(cls.BACKENDS.keys())
            raise VectorStoreError(
                f"Unsupported vector store backend: {backend}. "
                f"Available backends: {available}"
            )

        try:
            logger.info(f"Creating {backend} vector store")
            store_class = cls.BACKENDS[backend]
            store = store_class()
            store.initialize(persist_dir, collection_name)
            return store

        except VectorStoreError:
            raise
        except Exception as e:
            logger.error(f"Failed to create vector store: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to create {backend} vector store: {str(e)}")

    @classmethod
    def list_backends(cls) -> list:
        """List available backends.

        Returns:
            List of available backend names
        """
        return list(cls.BACKENDS.keys())

    @classmethod
    def register_backend(cls, name: str, store_class: type) -> None:
        """Register a new backend.

        Args:
            name: Backend name
            store_class: Vector store class

        Raises:
            TypeError: If class doesn't implement VectorStoreBase
        """
        if not issubclass(store_class, VectorStoreBase):
            raise TypeError(f"{store_class} must inherit from VectorStoreBase")

        cls.BACKENDS[name] = store_class
        logger.info(f"Registered vector store backend: {name}")
