"""Weaviate vector store implementation for cloud/self-hosted use."""

from typing import List, Optional, Tuple

from rag_app.config import get_settings
from rag_app.exceptions import VectorStoreError
from rag_app.logger import get_logger

from .abstract_store import VectorStoreBase

logger = get_logger(__name__)


class WeaviateVectorStore(VectorStoreBase):
    """Weaviate vector store implementation.

    Supports both cloud-hosted and self-hosted Weaviate instances.
    Great for scalable, cloud-native deployments.
    """

    def __init__(self):
        """Initialize Weaviate vector store."""
        super().__init__("weaviate")
        self.client = None
        self.collection_name = None

    def initialize(self, persist_dir: str, collection_name: str) -> None:
        """Initialize Weaviate client and collection.

        Args:
            persist_dir: Base URL or connection string for Weaviate
            collection_name: Name of the collection

        Raises:
            VectorStoreError: If initialization fails
        """
        try:
            import weaviate

            settings = get_settings()

            # Get Weaviate config from settings or use persist_dir as URL
            weaviate_url = getattr(settings, "WEAVIATE_URL", persist_dir)
            api_key = getattr(settings, "WEAVIATE_API_KEY", None)

            logger.info(f"Connecting to Weaviate at {weaviate_url}")

            # Connect to Weaviate
            if api_key:
                auth = weaviate.AuthApiKey(api_key=api_key)
                self.client = weaviate.Client(weaviate_url, auth_client_secret=auth)
            else:
                self.client = weaviate.Client(weaviate_url)

            self.collection_name = collection_name

            # Check if schema exists, create if not
            try:
                self.client.schema.get(collection_name)
                logger.info(f"Collection {collection_name} already exists")
            except weaviate.exceptions.WeaviateException:
                # Create new class/collection
                class_obj = {
                    "class": collection_name,
                    "description": "RAG document collection",
                    "vectorizer": "text2vec-openai",  # or other vectorizer
                    "properties": [
                        {
                            "name": "text",
                            "dataType": ["text"],
                            "description": "Document text",
                        },
                        {
                            "name": "source",
                            "dataType": ["text"],
                            "description": "Document source",
                        },
                        {
                            "name": "page",
                            "dataType": ["int"],
                            "description": "Page number",
                        },
                    ],
                }
                self.client.schema.create_class(class_obj)
                logger.info(f"Created collection {collection_name}")

            logger.info("Weaviate vector store initialized")

        except ImportError:
            raise VectorStoreError(
                "Weaviate client is not installed. Install with: pip install weaviate-client"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Weaviate: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Weaviate initialization failed: {str(e)}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> int:
        """Add documents to Weaviate.

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
            added_count = 0

            for doc_id, text, embedding, metadata in zip(
                ids, documents, embeddings, metadatas
            ):
                # Combine text with metadata
                obj = {
                    "text": text,
                    "source": metadata.get("source", "unknown"),
                    "page": metadata.get("page", 0),
                }

                # Add to Weaviate
                self.client.data_object.create(
                    obj,
                    self.collection_name,
                    uuid=doc_id,
                    vector=embedding,
                )
                added_count += 1

            logger.info(f"Added {added_count} documents to Weaviate")
            return added_count

        except Exception as e:
            logger.error(f"Failed to add documents to Weaviate: {str(e)}", exc_info=True)
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
            # Use vector search in Weaviate
            result = (
                self.client.query.get(self.collection_name, ["text", "source", "page"])
                .with_near_vector({"vector": query_embedding})
                .with_limit(top_k)
                .do()
            )

            documents = []
            metadatas = []
            scores = []

            if "data" in result and "Get" in result["data"]:
                items = result["data"]["Get"].get(self.collection_name, [])
                for i, item in enumerate(items):
                    documents.append(item.get("text", ""))
                    metadatas.append(
                        {
                            "source": item.get("source", ""),
                            "page": item.get("page", 0),
                        }
                    )
                    scores.append(1.0 - (i * 0.1))  # Approximate scores

            logger.debug(f"Found {len(documents)} documents in Weaviate")
            return documents, metadatas, scores

        except Exception as e:
            logger.error(f"Weaviate search failed: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Search failed: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the current collection.

        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            if self.client and self.collection_name:
                self.client.schema.delete_class(self.collection_name)
                logger.info(f"Deleted Weaviate collection: {self.collection_name}")

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
            result = (
                self.client.query.aggregate(self.collection_name)
                .with_meta_count()
                .do()
            )

            count = result["data"]["Aggregate"][self.collection_name][0]["meta"]["count"]
            return count

        except Exception as e:
            logger.error(f"Failed to get collection count: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to get count: {str(e)}")

    def persist(self) -> None:
        """Persist the vector store (Weaviate handles this automatically)."""
        logger.debug("Weaviate persistence handled automatically")

    def close(self) -> None:
        """Close Weaviate connection."""
        if self.client:
            self.client.close()
            logger.debug("Weaviate connection closed")
