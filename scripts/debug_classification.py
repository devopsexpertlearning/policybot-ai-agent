
import asyncio
import sys
import os
from pathlib import Path
import time
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.agent import agent, QueryType

async def test_classification(query: str):
    start = time.time()
    classification = await agent.classify_query(query)
    duration = time.time() - start
    
    print(f"Query: '{query}'")
    print(f"   -> Result: {classification.value}")
    print(f"   -> Time:   {duration:.2f}s")
    return classification

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    
    test_queries = [
        # Policy Queries (Should be POLICY)
        "What is the sick leave policy?",
        "Health insurance for employer",
        "Can I work from home?",
        "Tell me about the 401k match",
        
        # General Queries (Should be GENERAL)
        "What is the capital of France?",
        "Write a python function to add two numbers",
        "Hello, how are you?",
        "Who is the president of USA?",
        
        # Ambiguous/Clarification (Should be CLARIFICATION or GENERAL)
        "policy",
        "help",
        "I don't understand"
    ]
    
    print("🔍 Testing Query Classification...")
    print("-" * 50)
    
    results = {}
    for q in test_queries:
        res = await test_classification(q)
        results[q] = res
        print("-" * 20)

if __name__ == "__main__":
    asyncio.run(main())
