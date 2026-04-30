"""Abstract base class for vector stores."""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

import numpy as np


class VectorStoreBase(ABC):
    """Abstract base class for vector store implementations.

    This allows easy switching between different vector database backends
    (Chroma, Weaviate, Pinecone, Milvus, etc.) by just changing the name.
    """

    def __init__(self, name: str):
        """Initialize vector store.

        Args:
            name: Vector store name/backend
        """
        self.name = name
        self.collection = None

    @abstractmethod
    def initialize(self, persist_dir: str, collection_name: str) -> None:
        """Initialize the vector store.

        Args:
            persist_dir: Directory for persistence
            collection_name: Name of the collection
        """
        pass

    @abstractmethod
    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> int:
        """Add documents to the vector store.

        Args:
            ids: List of document IDs
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries

        Returns:
            Number of documents added
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> Tuple[List[str], List[dict], List[float]]:
        """Search for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            Tuple of (documents, metadatas, scores)
        """
        pass

    @abstractmethod
    def delete_collection(self) -> None:
        """Delete the current collection."""
        pass

    @abstractmethod
    def get_collection_count(self) -> int:
        """Get number of documents in collection.

        Returns:
            Number of documents
        """
        pass

    @abstractmethod
    def persist(self) -> None:
        """Persist the vector store."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close connections."""
        pass
