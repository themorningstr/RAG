"""Pinecone vector store implementation for managed cloud use."""

from typing import List, Optional, Tuple

from rag_app.config import get_settings
from rag_app.exceptions import VectorStoreError
from rag_app.logger import get_logger

from .abstract_store import VectorStoreBase

logger = get_logger(__name__)


class PineconeVectorStore(VectorStoreBase):
    """Pinecone vector store implementation.

    Fully managed vector database service. Requires Pinecone API key.
    Great for production, scalable deployments without infrastructure.
    """

    def __init__(self):
        """Initialize Pinecone vector store."""
        super().__init__("pinecone")
        self.client = None
        self.index = None
        self.collection_name = None

    def initialize(self, persist_dir: str, collection_name: str) -> None:
        """Initialize Pinecone client and index.

        Args:
            persist_dir: Not used for Pinecone (cloud-hosted)
            collection_name: Name of the Pinecone index

        Raises:
            VectorStoreError: If initialization fails
        """
        try:
            from pinecone import Pinecone

            settings = get_settings()

            # Get Pinecone API key from settings
            api_key = getattr(settings, "PINECONE_API_KEY", None)
            environment = getattr(settings, "PINECONE_ENVIRONMENT", "us-west1-gcp")

            if not api_key:
                raise VectorStoreError(
                    "PINECONE_API_KEY not found in settings. "
                    "Set PINECONE_API_KEY in .env file"
                )

            logger.info(f"Initializing Pinecone with index: {collection_name}")

            # Initialize Pinecone client
            self.client = Pinecone(api_key=api_key)

            # Connect to index
            self.index = self.client.Index(collection_name)
            self.collection_name = collection_name

            logger.info("Pinecone vector store initialized")

        except ImportError:
            raise VectorStoreError(
                "Pinecone client is not installed. Install with: pip install pinecone-client"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Pinecone: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Pinecone initialization failed: {str(e)}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> int:
        """Add documents to Pinecone index.

        Args:
            ids: List of document IDs
            documents: List of document texts
            embeddings: List of embedding vectors
            metadatas: List of metadata dictionaries

        Returns:
            Number of documents added

        Raises:
            VectorStoreError: If adding documents fails
        """
        try:
            vectors = []

            for doc_id, text, embedding, metadata in zip(
                ids, documents, embeddings, metadatas
            ):
                # Prepare vector with metadata
                vectors.append(
                    (
                        doc_id,
                        embedding,
                        {
                            "text": text,
                            "source": metadata.get("source", "unknown"),
                            "page": metadata.get("page", 0),
                        },
                    )
                )

            # Upsert in batches (Pinecone has batch limits)
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i : i + batch_size]
                self.index.upsert(vectors=batch)

            logger.info(f"Added {len(vectors)} documents to Pinecone")
            return len(vectors)

        except Exception as e:
            logger.error(f"Failed to add documents to Pinecone: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to add documents: {str(e)}")

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

        Raises:
            VectorStoreError: If search fails
        """
        try:
            # Query Pinecone index
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True,
            )

            documents = []
            metadatas = []
            scores = []

            for match in results.get("matches", []):
                metadata = match.get("metadata", {})
                documents.append(metadata.get("text", ""))
                metadatas.append(
                    {
                        "source": metadata.get("source", ""),
                        "page": metadata.get("page", 0),
                    }
                )
                scores.append(match.get("score", 0.0))

            logger.debug(f"Found {len(documents)} documents in Pinecone")
            return documents, metadatas, scores

        except Exception as e:
            logger.error(f"Pinecone search failed: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Search failed: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the current collection.

        Note: This deletes all vectors from the index.

        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            if self.index:
                # Delete all vectors from index
                self.index.delete(delete_all=True)
                logger.info(f"Deleted all vectors from Pinecone index: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to delete collection: {str(e)}")

    def get_collection_count(self) -> int:
        """Get number of documents in collection.

        Returns:
            Number of documents

        Raises:
            VectorStoreError: If query fails
        """
        try:
            stats = self.index.describe_index_stats()
            count = stats.total_vector_count
            return count

        except Exception as e:
            logger.error(f"Failed to get collection count: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to get count: {str(e)}")

    def persist(self) -> None:
        """Persist the vector store (Pinecone handles this automatically)."""
        logger.debug("Pinecone persistence handled automatically")

    def close(self) -> None:
        """Close Pinecone connections."""
        logger.debug("Pinecone connection closed")
