"""
Script to setup vector store by processing documents and creating embeddings.
Run this before starting the application for the first time.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.document_processor import DocumentProcessor
from app.rag.vector_store import get_vector_store
from app.llm.llm_client import llm_client
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Setup vector store with documents."""
    logger.info("🚀 Starting vector store setup...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Vector store type: {'FAISS' if settings.use_faiss else 'Azure AI Search'}")
    
    # Initialize components
    processor = DocumentProcessor()
    vector_store = get_vector_store()
    
    # Process documents
    documents_path = Path(__file__).parent.parent / "data" / "documents"
    logger.info(f"Processing documents from: {documents_path}")
    
    if not documents_path.exists():
        logger.error(f"Documents directory not found: {documents_path}")
        return
    
    chunks = processor.process_directory(str(documents_path))
    
    if not chunks:
        logger.error("No documents found or processed")
        return
    
    logger.info(f"✅ Processed {len(chunks)} chunks from documents")
    
    # Get statistics
    stats = processor.get_document_stats(chunks)
    logger.info(f"📊 Statistics: {stats}")
    
    # Generate embeddings
    logger.info("🔄 Generating embeddings...")
    texts = [chunk["content"] for chunk in chunks]
    
    try:
        embeddings = await llm_client.generate_embeddings_batch(texts, batch_size=1)
        logger.info(f"✅ Generated {len(embeddings)} embeddings")
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        return
    
    # Create index if using Azure Search
    if not settings.use_faiss:
        logger.info("🔧 Creating Azure AI Search index...")
        try:
            dimension = 3072 if settings.use_gemini else 1536
            vector_store.create_index(dimension=dimension)
            logger.info("✅ Index created/verified")
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            return
    
    # Add to vector store
    logger.info("💾 Adding documents to vector store...")
    try:
        vector_store.add_documents(embeddings, chunks)
        logger.info("✅ Documents added to vector store")
    except Exception as e:
        logger.error(f"Error adding documents to vector store: {e}")
        return
    
    # Save vector store (for FAISS)
    if settings.use_faiss:
        logger.info("💾 Saving FAISS index...")
        try:
            vector_store.save()
            logger.info("✅ FAISS index saved")
        except Exception as e:
            logger.error(f"Error saving FAISS index: {e}")
            return
    
    # Test retrieval
    logger.info("\n🧪 Testing retrieval...")
    test_query = "What is the leave policy?"
    logger.info(f"Test query: {test_query}")
    
    try:
        query_embedding = await llm_client.generate_embedding(test_query)
        results = vector_store.search(query_embedding, top_k=3)
        
        logger.info(f"✅ Retrieved {len(results)} documents")
        for i, result in enumerate(results, 1):
            source = result.get("metadata", {}).get("source", "Unknown")
            score = result.get("similarity_score", 0)
            logger.info(f"  {i}. {source} (score: {score:.3f})")
    except Exception as e:
        logger.error(f"Error testing retrieval: {e}")
    
    logger.info("\n✅ Vector store setup complete!")
    logger.info("You can now start the application with: python -m app.main")


if __name__ == "__main__":
    asyncio.run(main())
