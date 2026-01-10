"""
Document retriever for RAG pipeline.
"""

import logging
from typing import List, Dict, Any, Optional

from app.rag.vector_store import get_vector_store
from app.llm.llm_client import llm_client
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """Retrieve relevant documents for RAG."""
    
    def __init__(self):
        """Initialize retriever."""
        self.vector_store = get_vector_store()
        self.llm_client = llm_client
    
    async def retrieve(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            threshold: Similarity threshold
            
        Returns:
            List of relevant document chunks
        """
        top_k = top_k or settings.top_k_results
        threshold = threshold or settings.similarity_threshold
        
        try:
            # Generate query embedding
            logger.info(f"Generating embedding for query: {query[:100]}...")
            query_embedding = await self.llm_client.generate_embedding(query)
            
            # Search vector store
            logger.info(f"Searching vector store (top_k={top_k}, threshold={threshold})")
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                threshold=threshold
            )
            
            logger.info(f"Retrieved {len(results)} documents")
            return results
        
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    async def retrieve_with_reranking(
        self,
        query: str,
        top_k: int = None,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve and re-rank documents for better relevance.
        
        Args:
            query: User query
            top_k: Number of documents to retrieve initially (will be reranked)
            threshold: Similarity threshold
            
        Returns:
            Re-ranked list of document chunks
        """
        # Get initial results
        results = await self.retrieve(
            query=query,
            top_k=top_k * 2 if top_k else settings.top_k_results * 2,
            threshold=threshold
        )
        
        if not results:
            return []
        
        # Simple re-ranking based on keyword matching
        # In production, could use a cross-encoder model
        query_words = set(query.lower().split())
        
        for result in results:
            content_words = set(result["content"].lower().split())
            keyword_overlap = len(query_words.intersection(content_words))
            
            # Combine original similarity with keyword overlap
            result["relevance_score"] = (
                result.get("similarity_score", 0) * 0.7 +
                (keyword_overlap / len(query_words)) * 0.3
            )
        
        # Sort by relevance and take top_k
        results.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        top_k = top_k or settings.top_k_results
        
        return results[:top_k]
    
    def format_sources(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Format source citations from documents.
        
        Args:
            documents: Retrieved documents
            
        Returns:
            List of formatted source strings
        """
        sources = []
        seen = set()
        
        for doc in documents:
            metadata = doc.get("metadata", {})
            source = metadata.get("source", "Unknown")
            page = metadata.get("page")
            
            if page:
                source_str = f"{source} (Page {page})"
            else:
                source_str = source
            
            if source_str not in seen:
                sources.append(source_str)
                seen.add(source_str)
        
        return sources


# Global retriever instance
retriever = DocumentRetriever()
