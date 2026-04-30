"""FAISS vector store implementation for local/embedded use."""

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np

from rag_app.exceptions import VectorStoreError
from rag_app.logger import get_logger

from .abstract_store import VectorStoreBase

logger = get_logger(__name__)


class FAISSVectorStore(VectorStoreBase):
    """FAISS (Facebook AI Similarity Search) vector store implementation.

    Lightweight, fast, local vector search without external dependencies.
    Great for development and small-to-medium datasets.
    """

    def __init__(self):
        """Initialize FAISS vector store."""
        super().__init__("faiss")
        self.index = None
        self.documents = []
        self.metadatas = []
        self.ids = []
        self.persist_path = None

    def initialize(self, persist_dir: str, collection_name: str) -> None:
        """Initialize FAISS index.

        Args:
            persist_dir: Directory for persistence
            collection_name: Name of the collection

        Raises:
            VectorStoreError: If initialization fails
        """
        try:
            import faiss

            self.collection_name = collection_name
            self.persist_path = Path(persist_dir) / f"{collection_name}_faiss"
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)

            # Try to load existing index
            index_path = self.persist_path / "index.faiss"
            ids_path = self.persist_path / "ids.npy"
            docs_path = self.persist_path / "docs.npy"
            metas_path = self.persist_path / "metas.npy"

            if index_path.exists() and ids_path.exists():
                try:
                    self.index = faiss.read_index(str(index_path))
                    self.ids = list(np.load(ids_path, allow_pickle=True))
                    self.documents = list(np.load(docs_path, allow_pickle=True))
                    self.metadatas = list(np.load(metas_path, allow_pickle=True))
                    logger.info(
                        f"Loaded existing FAISS index with {len(self.ids)} documents"
                    )
                except Exception as e:
                    logger.warning(f"Failed to load existing index: {str(e)}")
                    self.index = None
            else:
                self.index = None

            logger.info(
                f"FAISS vector store initialized: {collection_name} at {persist_dir}"
            )

        except ImportError:
            raise VectorStoreError(
                "FAISS is not installed. Install with: pip install faiss-cpu"
            )
        except Exception as e:
            logger.error(f"Failed to initialize FAISS: {str(e)}", exc_info=True)
            raise VectorStoreError(f"FAISS initialization failed: {str(e)}")

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[dict],
    ) -> int:
        """Add documents to FAISS index.

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
            import faiss

            embeddings_array = np.array(embeddings, dtype=np.float32)

            # Initialize index if not exists
            if self.index is None:
                dimension = embeddings_array.shape[1]
                self.index = faiss.IndexFlatL2(dimension)  # L2 distance
                logger.debug(f"Created FAISS index with dimension {dimension}")

            # Add to index
            self.index.add(embeddings_array)

            # Store metadata
            self.ids.extend(ids)
            self.documents.extend(documents)
            self.metadatas.extend(metadatas)

            logger.info(f"Added {len(ids)} documents to FAISS index")
            self.persist()

            return len(ids)

        except Exception as e:
            logger.error(f"Failed to add documents to FAISS: {str(e)}", exc_info=True)
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
            Tuple of (documents, metadatas, distances)

        Raises:
            VectorStoreError: If search fails
        """
        try:
            if self.index is None or len(self.ids) == 0:
                return [], [], []

            query_array = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.index.search(query_array, min(top_k, len(self.ids)))

            results = []
            for idx in indices[0]:
                if idx < len(self.ids):
                    results.append(
                        (
                            self.documents[idx],
                            self.metadatas[idx],
                            1.0 / (1.0 + distances[0][len(results)]),
                        )  # Convert distance to similarity
                    )

            return (
                [r[0] for r in results],
                [r[1] for r in results],
                [r[2] for r in results],
            )

        except Exception as e:
            logger.error(f"FAISS search failed: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Search failed: {str(e)}")

    def delete_collection(self) -> None:
        """Delete the current collection.

        Raises:
            VectorStoreError: If deletion fails
        """
        try:
            self.index = None
            self.documents = []
            self.metadatas = []
            self.ids = []

            if self.persist_path and self.persist_path.exists():
                import shutil

                shutil.rmtree(self.persist_path)
                logger.info(f"Deleted FAISS collection: {self.collection_name}")

        except Exception as e:
            logger.error(f"Failed to delete collection: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Failed to delete collection: {str(e)}")

    def get_collection_count(self) -> int:
        """Get number of documents in collection.

        Returns:
            Number of documents
        """
        return len(self.ids)

    def persist(self) -> None:
        """Persist the FAISS index to disk.

        Raises:
            VectorStoreError: If persistence fails
        """
        try:
            if self.index is None or self.persist_path is None:
                return

            import faiss

            self.persist_path.mkdir(parents=True, exist_ok=True)

            # Save index
            faiss.write_index(self.index, str(self.persist_path / "index.faiss"))

            # Save metadata
            np.save(self.persist_path / "ids.npy", np.array(self.ids, dtype=object))
            np.save(
                self.persist_path / "docs.npy",
                np.array(self.documents, dtype=object),
            )
            np.save(
                self.persist_path / "metas.npy",
                np.array(self.metadatas, dtype=object),
            )

            logger.debug("FAISS index persisted")

        except Exception as e:
            logger.error(f"Failed to persist FAISS: {str(e)}", exc_info=True)
            raise VectorStoreError(f"Persistence failed: {str(e)}")

    def close(self) -> None:
        """Close FAISS connections."""
        self.persist()
        logger.debug("FAISS store closed")
