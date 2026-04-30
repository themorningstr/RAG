"""Astra DB vector store implementation for managed deployments."""

from typing import List, Optional, Tuple

from rag_app.config import get_settings
from rag_app.exceptions import VectorStoreError
from rag_app.logger import get_logger

from .abstract_store import VectorStoreBase

logger = get_logger(__name__)


class AstraDBVectorStore(VectorStoreBase):
    """Astra DB vector store implementation.

    DataStax Astra DB - Managed Apache Cassandra with vector search.
    Requires API key and database credentials. Enterprise-grade vector database.
    """

    def __init__(self):
        """Initialize Astra DB vector store."""
        super().__init__("astradb")
        self.client = None
        self.collection_name = None

    def initialize(self, persist_dir: str, collection_name: str) -> None:
        """Initialize Astra DB client and collection.

        Args:
            persist_dir: Not used for Astra (cloud-hosted)
            collection_name: Name of the collection/table

        Raises:
            VectorStoreError: If initialization fails
        """
        try:
            from astrapy.db import AstraDB

            settings = get_settings()

            # Get Astra DB credentials from settings
            astra_db_id = getattr(settings, "ASTRA_DB_ID", None)
            astra_db_region = getattr(settings, "ASTRA_DB_REGION", "us-east1")
            astra_db_token = getattr(settings, "ASTRA_DB_TOKEN", None)

            if not astra_db_id or not astra_db_token:
                raise VectorStoreError(
                    "Astra DB credentials not found in settings. "
                    "Set ASTRA_DB_ID, ASTRA_DB_REGION, and ASTRA_DB_TOKEN in .env file"
                )

            logger.info(f"Initializing Astra DB collection: {collection_name}")

            # Initialize Astra DB client
            self.client = AstraDB(
                token=astra_db_token,
                api_endpoint=f"https://{astra_db_id}-{astra_db_region}.apps.astra.datastax.com",
            )

            self.collection_name = collection_name
            self.db = self.client.collection(collection_name)

            logger.info("Astra DB vector store initialized")

        except ImportError:
            raise VectorStoreError(
                "Astra DB client is not installed. Install with: pip install astrapy"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Astra DB: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Astra DB initialization failed: {str(e)}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> int:
        """Add documents to Astra DB collection.

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
            inserted_ids = []

            for doc_id, text, embedding, metadata in zip(
                ids, documents, embeddings, metadatas
            ):
                # Prepare document
                document = {
                    "_id": doc_id,
                    "text": text,
                    "source": metadata.get("source", "unknown"),
                    "page": metadata.get("page", 0),
                    "$vector": embedding,
                }

                # Insert into Astra DB
                try:
                    self.db.insert_one(document)
                    inserted_ids.append(doc_id)
                except Exception as e:
                    logger.warning(
                        f"Failed to insert document {doc_id}: {str(e)}"
                    )

            logger.info(f"Added {len(inserted_ids)} documents to Astra DB")
            return len(inserted_ids)

        except Exception as e:
            logger.error(
                f"Failed to add documents to Astra DB: {str(e)}", exc_info=True
            )
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
            # Search in Astra DB
            results = self.db.find(
                filter={},
                sort={"$vector": query_embedding},
                limit=top_k,
            )

            documents = []
            metadatas = []
            scores = []

            for i, result in enumerate(results):
                documents.append(result.get("text", ""))
                metadatas.append(
                    {
                        "source": result.get("source", ""),
                        "page": result.get("page", 0),
                    }
                )
                # Approximate score based on position (1.0 for top result, decreasing)
                scores.append(1.0 - (i * 0.1))

            logger.debug(f"Found {len(documents)} documents in Astra DB")
            return documents, metadatas, scores

        except Exception as e:
            logger.error(f"Astra DB search failed: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Search failed: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the current collection.

        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            if self.db:
                self.db.delete_many(filter={})
                logger.info(f"Deleted all documents from Astra DB collection: {self.collection_name}")

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
            # Use estimated_document_count if available
            count = self.db.count_documents(filter={})
            return count

        except Exception as e:
            logger.error(f"Failed to get collection count: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to get count: {str(e)}")

    def persist(self) -> None:
        """Persist the vector store (Astra DB handles this automatically)."""
        logger.debug("Astra DB persistence handled automatically")

    def close(self) -> None:
        """Close Astra DB connections."""
        logger.debug("Astra DB connection closed")
