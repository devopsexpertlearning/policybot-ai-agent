"""
Vector store implementation with support for FAISS (local) and Azure AI Search (production).
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

# FAISS for local development
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    logging.warning("FAISS not available")

# Azure AI Search for production
try:
    from azure.search.documents import SearchClient
    from azure.search.documents.indexes import SearchIndexClient
    from azure.search.documents.indexes.models import (
        SearchIndex,
        SearchField,
        SearchFieldDataType,
        VectorSearch,
        VectorSearchProfile,
        HnswAlgorithmConfiguration,
    )
    from azure.core.credentials import AzureKeyCredential
    AZURE_SEARCH_AVAILABLE = True
except ImportError:
    AZURE_SEARCH_AVAILABLE = False
    logging.warning("Azure Search SDK not available")

from app.config import settings

logger = logging.getLogger(__name__)


class FAISSVectorStore:
    """FAISS vector store for local development."""
    
    def __init__(self, index_path: str = None, dimension: int = 1536):
        """
        Initialize FAISS vector store.
        
        Args:
            index_path: Path to save/load index
            dimension: Embedding dimension
        """
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS is not installed. Install with: pip install faiss-cpu")
        
        self.index_path = index_path or settings.vector_store_path
        self.dimension = dimension
        self.index = None
        self.metadata_store = []
        
        # Create directory if needed
        Path(self.index_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Try to load existing index
        if os.path.exists(self.index_path):
            self.load()
        else:
            # Create new index
            self.index = faiss.IndexFlatL2(dimension)
            logger.info(f"Created new FAISS index with dimension {dimension}")
    
    def add_documents(
        self,
        embeddings: List[List[float]],
        documents: List[Dict[str, Any]]
    ) -> None:
        """
        Add documents to vector store.
        
        Args:
            embeddings: Document embeddings
            documents: Document metadata
        """
        if len(embeddings) != len(documents):
            raise ValueError("Number of embeddings must match number of documents")
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings, dtype=np.float32)
        
        # Add to index
        self.index.add(embeddings_array)
        
        # Store metadata
        self.metadata_store.extend(documents)
        
        logger.info(f"Added {len(embeddings)} documents to FAISS index")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query_embedding: Query embedding
            top_k: Number of results to return
            threshold: Similarity threshold (optional)
            
        Returns:
            List of documents with similarity scores
        """
        if self.index.ntotal == 0:
            logger.warning("Index is empty")
            return []
        
        # Convert to numpy array
        query_array = np.array([query_embedding], dtype=np.float32)
        
        # Search
        distances, indices = self.index.search(query_array, top_k)
        
        # Prepare results
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(self.metadata_store):
                # Convert L2 distance to similarity score (0-1)
                similarity = 1 / (1 + distance)
                
                if threshold is None or similarity >= threshold:
                    result = self.metadata_store[idx].copy()
                    result["similarity_score"] = float(similarity)
                    results.append(result)
        
        return results
    
    def save(self) -> None:
        """Save index and metadata to disk."""
        # Save FAISS index
        faiss.write_index(self.index, f"{self.index_path}.faiss")
        
        # Save metadata
        with open(f"{self.index_path}.metadata", 'wb') as f:
            pickle.dump(self.metadata_store, f)
        
        logger.info(f"Saved FAISS index to {self.index_path}")
    
    def load(self) -> None:
        """Load index and metadata from disk."""
        try:
            # Load FAISS index
            self.index = faiss.read_index(f"{self.index_path}.faiss")
            
            # Load metadata
            with open(f"{self.index_path}.metadata", 'rb') as f:
                self.metadata_store = pickle.load(f)
            
            logger.info(f"Loaded FAISS index from {self.index_path}")
            logger.info(f"Index contains {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Error loading FAISS index: {e}")
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata_store = []
    
    def clear(self) -> None:
        """Clear the index."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata_store = []
        logger.info("Cleared FAISS index")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "total_documents": len(self.metadata_store)
        }


class AzureAISearchVectorStore:
    """Azure AI Search vector store for production."""
    
    def __init__(self):
        """Initialize Azure AI Search client."""
        if not AZURE_SEARCH_AVAILABLE:
            raise ImportError("Azure Search SDK not installed")
        
        if not settings.use_azure_search:
            raise ValueError("Azure Search configuration missing")
        
        self.endpoint = settings.azure_search_endpoint
        self.index_name = settings.azure_search_index_name
        self.credential = AzureKeyCredential(settings.azure_search_api_key)
        
        # Initialize clients
        self.index_client = SearchIndexClient(self.endpoint, self.credential)
        self.search_client = SearchClient(
            self.endpoint,
            self.index_name,
            self.credential
        )
        
        logger.info(f"Initialized Azure AI Search client for index: {self.index_name}")
    
    def create_index(self, dimension: int = 1536) -> None:
        """Create search index if it doesn't exist."""
        # Define index schema
        fields = [
            SearchField(
                name="id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True
            ),
            SearchField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True
            ),
            SearchField(
                name="embedding",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=dimension,
                vector_search_profile_name="default-profile"
            ),
            SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
            SearchField(name="page", type=SearchFieldDataType.Int32, filterable=True),
            SearchField(name="chunk_id", type=SearchFieldDataType.String, filterable=True),
        ]
        
        # Configure vector search
        vector_search = VectorSearch(
            algorithms=[
                HnswAlgorithmConfiguration(name="default-algorithm")
            ],
            profiles=[
                VectorSearchProfile(
                    name="default-profile",
                    algorithm_configuration_name="default-algorithm"
                )
            ]
        )
        
        # Create index
        index = SearchIndex(
            name=self.index_name,
            fields=fields,
            vector_search=vector_search
        )
        
        self.index_client.create_or_update_index(index)
        logger.info(f"Created/updated index: {self.index_name}")
    
    def add_documents(
        self,
        embeddings: List[List[float]],
        documents: List[Dict[str, Any]]
    ) -> None:
        """Add documents to Azure Search."""
        if len(embeddings) != len(documents):
            raise ValueError("Embeddings and documents count mismatch")
        
        # Prepare documents for upload
        search_documents = []
        for i, (embedding, doc) in enumerate(zip(embeddings, documents)):
            search_doc = {
                "id": f"{doc['metadata'].get('source', 'unknown')}_{i}",
                "content": doc["content"],
                "embedding": embedding,
                **doc["metadata"]
            }
            search_documents.append(search_doc)
        
        # Upload in batches
        batch_size = 100
        for i in range(0, len(search_documents), batch_size):
            batch = search_documents[i:i + batch_size]
            self.search_client.upload_documents(documents=batch)
        
        logger.info(f"Added {len(documents)} documents to Azure Search")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Search using vector similarity."""
        results = self.search_client.search(
            search_text=None,
            vector_queries=[{
                "vector": query_embedding,
                "k_nearest_neighbors": top_k,
                "fields": "embedding"
            }],
            select=["content", "source", "page", "chunk_id"]
        )
        
        documents = []
        for result in results:
            score = result.get("@search.score", 0)
            
            if threshold is None or score >= threshold:
                documents.append({
                    "content": result.get("content"),
                    "metadata": {
                        "source": result.get("source"),
                        "page": result.get("page"),
                        "chunk_id": result.get("chunk_id")
                    },
                    "similarity_score": score
                })
        
        return documents


# Factory function to get appropriate vector store
def get_vector_store():
    """Get vector store based on environment."""
    if settings.use_faiss:
        logger.info("Using FAISS vector store (local)")
        return FAISSVectorStore()
    elif settings.use_azure_search:
        logger.info("Using Azure AI Search (production)")
        return AzureAISearchVectorStore()
    else:
        raise ValueError("No vector store configuration found")
