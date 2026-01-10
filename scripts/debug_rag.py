
import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag.vector_store import get_vector_store
from app.llm.llm_client import llm_client
from app.config import settings

async def debug_query(query: str):
    print(f"\n🔍 Debugging Query: '{query}'")
    
    # Generate embedding
    print("   Generating embedding...")
    embedding = await llm_client.generate_embedding(query)
    
    # Get vector store
    vector_store = get_vector_store()
    
    # Search with very low threshold to see all candidates
    print(f"   Searching vector store (top_k=5)...")
    results = vector_store.search(embedding, top_k=5, threshold=0.0)
    
    if not results:
        print("   ❌ No results found even with threshold 0.0")
        return

    print(f"   ✅ Found {len(results)} results:")
    for i, res in enumerate(results, 1):
        score = res.get('similarity_score', 0)
        source = res['metadata'].get('source', 'unknown')
        content_preview = res['content'][:100].replace('\n', ' ') + "..."
        
        # Check if it would pass the current config threshold
        pass_threshold = score >= settings.similarity_threshold
        status_icon = "✅" if pass_threshold else "❌"
        
        print(f"   {i}. {status_icon} Score: {score:.4f} | Source: {source}")
        print(f"      Content: {content_preview}")

async def main():
    # Load config explicitly to ensure we read from .env if needed
    print(f"Current Config Threshold: {settings.similarity_threshold}")
    
    await debug_query("What is health insurance policy for employer?")
    await debug_query("What is employee policy?")

if __name__ == "__main__":
    asyncio.run(main())
