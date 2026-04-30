"""Qdrant vector store implementation for open-source deployments."""

from typing import List, Optional, Tuple

from rag_app.config import get_settings
from rag_app.exceptions import VectorStoreError
from rag_app.logger import get_logger

from .abstract_store import VectorStoreBase

logger = get_logger(__name__)


class QdrantVectorStore(VectorStoreBase):
    """Qdrant vector store implementation.

    Open-source vector similarity search engine. Supports both in-memory and persistent storage.
    Great for self-hosted or containerized deployments.
    """

    def __init__(self):
        """Initialize Qdrant vector store."""
        super().__init__("qdrant")
        self.client = None
        self.collection_name = None

    def initialize(self, persist_dir: str, collection_name: str) -> None:
        """Initialize Qdrant client and collection.

        Args:
            persist_dir: Path for local storage or URL for remote Qdrant
            collection_name: Name of the collection

        Raises:
            VectorStoreError: If initialization fails
        """
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            settings = get_settings()

            # Get Qdrant configuration
            qdrant_url = getattr(settings, "QDRANT_URL", None)
            qdrant_api_key = getattr(settings, "QDRANT_API_KEY", None)

            logger.info(f"Initializing Qdrant collection: {collection_name}")

            # Connect to Qdrant
            if qdrant_url:
                # Remote Qdrant instance
                self.client = QdrantClient(
                    url=qdrant_url,
                    api_key=qdrant_api_key,
                )
                logger.info(f"Connected to remote Qdrant at {qdrant_url}")
            else:
                # Local Qdrant instance
                self.client = QdrantClient(path=persist_dir)
                logger.info(f"Using local Qdrant at {persist_dir}")

            self.collection_name = collection_name
            self.vector_size = None

            # Check if collection exists
            try:
                self.client.get_collection(collection_name)
                logger.info(f"Collection {collection_name} already exists")
            except Exception:
                # Collection doesn't exist yet, will create on first add
                logger.debug(f"Collection {collection_name} will be created on first add")

            logger.info("Qdrant vector store initialized")

        except ImportError:
            raise VectorStoreError(
                "Qdrant client is not installed. Install with: pip install qdrant-client"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Qdrant initialization failed: {str(e)}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> int:
        """Add documents to Qdrant collection.

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
            from qdrant_client.models import Distance, PointStruct, VectorParams

            # Create collection if it doesn't exist
            if self.vector_size is None and len(embeddings) > 0:
                self.vector_size = len(embeddings[0])
                try:
                    self.client.get_collection(self.collection_name)
                except Exception:
                    # Create collection
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=VectorParams(
                            size=self.vector_size, distance=Distance.COSINE
                        ),
                    )
                    logger.info(f"Created Qdrant collection: {self.collection_name}")

            # Prepare points
            points = []
            for i, (doc_id, text, embedding, metadata) in enumerate(
                zip(ids, documents, embeddings, metadatas)
            ):
                points.append(
                    PointStruct(
                        id=hash(doc_id) % (10**9),  # Convert string ID to number
                        vector=embedding,
                        payload={
                            "text": text,
                            "doc_id": doc_id,
                            "source": metadata.get("source", "unknown"),
                            "page": metadata.get("page", 0),
                        },
                    )
                )

            # Upsert points
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            logger.info(f"Added {len(ids)} documents to Qdrant")
            return len(ids)

        except Exception as e:
            logger.error(f"Failed to add documents to Qdrant: {str(e)}", exc_info=True)
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
            # Search in Qdrant
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=top_k,
            )

            documents = []
            metadatas = []
            scores = []

            for result in results:
                payload = result.payload
                documents.append(payload.get("text", ""))
                metadatas.append(
                    {
                        "source": payload.get("source", ""),
                        "page": payload.get("page", 0),
                    }
                )
                scores.append(result.score)

            logger.debug(f"Found {len(documents)} documents in Qdrant")
            return documents, metadatas, scores

        except Exception as e:
            logger.error(f"Qdrant search failed: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Search failed: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the current collection.

        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            if self.client and self.collection_name:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Deleted Qdrant collection: {self.collection_name}")

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
            collection_info = self.client.get_collection(self.collection_name)
            count = collection_info.points_count
            return count

        except Exception as e:
            logger.error(f"Failed to get collection count: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to get count: {str(e)}")

    def persist(self) -> None:
        """Persist the vector store (Qdrant handles this automatically)."""
        logger.debug("Qdrant persistence handled automatically")

    def close(self) -> None:
        """Close Qdrant connections."""
        if self.client:
            self.client.close()
            logger.debug("Qdrant connection closed")
