                                                                                                                                                                    #!/usr/bin/env python3
"""
Comprehensive test script to verify the agent handles both RAG and general queries.
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.agent import agent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def test_query(query: str, expected_type: str):
    """Test a single query and report results."""
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print(f"Expected Type: {expected_type}")
    print(f"{'='*60}")
    
    try:
        response = await agent.process_query(query)
        
        print(f"✓ Classification: {response['metadata']['query_type']}")
        print(f"✓ Method: {response['metadata']['method']}")
        print(f"✓ Processing Time: {response['metadata']['processing_time']}s")
        print(f"✓ Answer Preview: {response['answer'][:200]}...")
        
        if response.get('source'):
            print(f"✓ Sources: {', '.join(response['source'])}")
        
        # Verify expected type
        if response['metadata']['query_type'] == expected_type:
            print(f"✅ PASS - Correctly classified as {expected_type}")
        else:
            print(f"❌ FAIL - Expected {expected_type}, got {response['metadata']['query_type']}")
        
        return response
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None

async def main():
    print("\n" + "="*60)
    print("COMPREHENSIVE AGENT TEST")
    print("Testing RAG and General Query Handling")
    print("="*60)
    
    # Test cases: (query, expected_classification)
    test_cases = [
        # POLICY queries (should use RAG)
        ("What is the sick leave policy?", "POLICY"),
        ("How many vacation days do I get?", "POLICY"),
        ("What are the health insurance options?", "POLICY"),
        ("Can I work remotely?", "POLICY"),
        ("What is the 401k matching policy?", "POLICY"),
        
        # GENERAL queries (should use direct LLM)
        ("Hello, how are you?", "GENERAL"),
        ("What is the capital of France?", "GENERAL"),
        ("Explain what machine learning is", "GENERAL"),
        ("Write a Python function to add two numbers", "GENERAL"),
        ("Who won the World Cup in 2022?", "GENERAL"),
    ]
    
    results = []
    for query, expected in test_cases:
        result = await test_query(query, expected)
        results.append((query, expected, result))
        await asyncio.sleep(0.5)  # Small delay between queries
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, expected, result in results 
                 if result and result['metadata']['query_type'] == expected)
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Agent is working correctly!")
    else:
        print("\n⚠️  Some tests failed - Review the output above")

if __name__ == "__main__":
    asyncio.run(main())
