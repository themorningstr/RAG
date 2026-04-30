"""Chroma vector store implementation."""

import logging
from typing import List, Tuple

from chromadb.config import Settings as ChromaSettings
import chromadb

from rag_app.exceptions import VectorStoreError
from rag_app.logger import get_logger

from .abstract_store import VectorStoreBase

logger = get_logger(__name__)


class ChromaVectorStore(VectorStoreBase):
    """Chroma-based vector store implementation."""

    def __init__(self):
        """Initialize Chroma vector store."""
        super().__init__("chroma")
        self.client = None
        self.collection = None

    def initialize(self, persist_dir: str, collection_name: str) -> None:
        """Initialize Chroma vector store.

        Args:
            persist_dir: Directory for persistence
            collection_name: Name of the collection

        Raises:
            VectorStoreError: If initialization fails
        """
        try:
            logger.info(f"Initializing Chroma vector store in {persist_dir}")

            # Initialize Chroma client with persistence
            self.client = chromadb.Client(
                ChromaSettings(
                    chroma_db_impl="duckdb+parquet",
                    persist_directory=persist_dir,
                    anonymized_telemetry=False,
                )
            )

            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )

            logger.info(f"Chroma vector store initialized: {collection_name}")

        except Exception as e:
            logger.error(f"Failed to initialize Chroma: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Chroma initialization failed: {str(e)}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> int:
        """Add documents to Chroma.

        Args:
            ids: List of document IDs
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries

        Returns:
            Number of documents added

        Raises:
            VectorStoreError: If addition fails
        """
        try:
            if not self.collection:
                raise VectorStoreError("Vector store not initialized")

            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
            )

            logger.info(f"Added {len(documents)} documents to Chroma")
            return len(documents)

        except Exception as e:
            logger.error(f"Failed to add documents to Chroma: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to add documents: {str(e)}")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
    ) -> Tuple[List[str], List[dict], List[float]]:
        """Search Chroma for similar documents.

        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return

        Returns:
            Tuple of (documents, metadatas, scores)

        Raises:
            VectorStoreError: If search fails
        """
        try:
            if not self.collection:
                raise VectorStoreError("Vector store not initialized")

            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )

            documents = results["documents"][0] if results["documents"] else []
            metadatas = results["metadatas"][0] if results["metadatas"] else []
            scores = results["distances"][0] if results["distances"] else []

            # Convert distances to similarity scores
            similarity_scores = [1 - s for s in scores]

            logger.debug(f"Found {len(documents)} similar documents")
            return documents, metadatas, similarity_scores

        except Exception as e:
            logger.error(f"Failed to search Chroma: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Search failed: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the Chroma collection.

        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            if self.client and self.collection:
                self.client.delete_collection(name=self.collection.name)
                logger.info(f"Deleted collection: {self.collection.name}")
                self.collection = None

        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to delete collection: {str(e)}")

    def get_collection_count(self) -> int:
        """Get number of documents in Chroma collection.

        Returns:
            Number of documents

        Raises:
            VectorStoreError: If query fails
        """
        try:
            if not self.collection:
                raise VectorStoreError("Vector store not initialized")

            count = self.collection.count()
            logger.debug(f"Collection count: {count}")
            return count

        except Exception as e:
            logger.error(f"Failed to get collection count: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to get count: {str(e)}")

    def persist(self) -> None:
        """Persist Chroma to disk.

        Raises:
            VectorStoreError: If persistence fails
        """
        try:
            if self.client:
                self.client.persist()
                logger.info("Chroma vector store persisted")

        except Exception as e:
            logger.error(f"Failed to persist Chroma: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to persist: {str(e)}")

    def close(self) -> None:
        """Close Chroma connections."""
        try:
            if self.collection:
                self.collection = None
            if self.client:
                self.client = None
            logger.info("Chroma vector store closed")

        except Exception as e:
            logger.warning(f"Error closing Chroma: {str(e)}")
