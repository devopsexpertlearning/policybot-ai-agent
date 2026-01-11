"""
Interactive script to test the AI agent locally.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.agent import agent
from app.config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


async def main():
    """Interactive agent testing."""
    print("=" * 70)
    print("AI AGENT INTERACTIVE TEST")
    print("=" * 70)
    print(f"Environment: {settings.environment}")
    print(f"LLM Provider: {'Gemini' if settings.use_gemini else 'Azure OpenAI'}")
    print(f"Vector Store: {'FAISS' if settings.use_faiss else 'Azure AI Search'}")
    print("=" * 70)
    print("\nType your questions below. Type 'exit' or 'quit' to end.\n")
    
    session_id = None
    
    while True:
        try:
            query = input("\n You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break
            
            if query.lower() == 'stats':
                stats = agent.get_stats()
                print(f"\n📊 Stats: {stats}")
                continue
            
            if query.lower() == 'new':
                session_id = None
                print("\n🔄 Started new session")
                continue
            
            # Process query
            print("\n🤔 Thinking...")
            response = await agent.process_query(query, session_id)
            
            # Update session ID
            session_id = response["session_id"]
            
            # Display response
            print(f"\n Assistant: {response['answer']}")
            
            # Display sources if any
            if response.get("source"):
                print(f"\n📚 Sources: {', '.join(response['source'])}")
            
            # Display metadata
            metadata = response.get("metadata", {})
            print(f"\n📊 Method: {metadata.get('method')} | "
                  f"Query Type: {metadata.get('query_type')} | "
                  f"Time: {metadata.get('processing_time')}s")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
