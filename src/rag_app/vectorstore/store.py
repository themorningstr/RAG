"""Vector store using Chroma."""

from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from rag_app.config import get_settings
from rag_app.ingestion import Document


class VectorStore:
    """Vector store for storing and retrieving embeddings using Chroma."""

    def __init__(self, persist_directory: str = None, collection_name: str = "documents"):
        """Initialize vector store.
        
        Args:
            persist_directory: Directory to persist the vector store
            collection_name: Name of the collection
        """
        settings = get_settings()
        self.persist_directory = persist_directory or settings.CHROMA_DB_PATH
        self.collection_name = collection_name

        # Initialize Chroma client with persistence
        self.client = chromadb.Client(
            ChromaSettings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.persist_directory,
                anonymized_telemetry=False,
            )
        )

        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]],
    ) -> None:
        """Add documents with embeddings to vector store.
        
        Args:
            documents: List of documents
            embeddings: List of embeddings (vectors)
        """
        ids = []
        texts = []
        metadatas = []

        for idx, doc in enumerate(documents):
            doc_id = f"{doc.source}_{idx}"
            ids.append(doc_id)
            texts.append(doc.content)
            metadatas.append({**doc.metadata, "source": doc.source})

        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        print(f"Added {len(documents)} documents to vector store")

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 3,
    ) -> tuple[List[str], List[dict], List[float]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Embedding vector of query
            top_k: Number of results to return
            
        Returns:
            Tuple of (texts, metadatas, distances)
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        texts = results["documents"][0] if results["documents"] else []
        metadatas = results["metadatas"][0] if results["metadatas"] else []
        distances = results["distances"][0] if results["distances"] else []

        return texts, metadatas, distances

    def delete_collection(self) -> None:
        """Delete the current collection."""
        self.client.delete_collection(name=self.collection_name)
        print(f"Deleted collection: {self.collection_name}")

    def get_collection_stats(self) -> dict:
        """Get statistics about the collection."""
        return {
            "name": self.collection_name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata,
        }

    def persist(self) -> None:
        """Persist the vector store to disk."""
        self.client.persist()
        print(f"Vector store persisted to {self.persist_directory}")
