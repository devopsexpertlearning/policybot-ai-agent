#!/usr/bin/env python3
"""
Advanced test script to verify the agent handles complex queries.
Tests edge cases, multi-part questions, and nuanced scenarios.
"""
import asyncio
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.agent import agent

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

async def test_query(query: str, expected_type: str, description: str):
    """Test a single query and report results."""
    print(f"\n{'='*70}")
    print(f"Test: {description}")
    print(f"Query: {query}")
    print(f"Expected: {expected_type}")
    print(f"{'='*70}")
    
    try:
        response = await agent.process_query(query)
        
        classification = response['metadata']['query_type']
        method = response['metadata']['method']
        
        # Determine pass/fail
        passed = classification == expected_type
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{status} - Classification: {classification} | Method: {method}")
        print(f"Answer: {response['answer'][:300]}...")
        
        if response.get('source'):
            print(f"Sources: {', '.join(response['source'])}")
        
        return passed
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

async def main():
    print("\n" + "="*70)
    print("ADVANCED AGENT TEST SUITE")
    print("Testing Complex Scenarios for RAG and General Queries")
    print("="*70)
    
    # Advanced test cases
    test_cases = [
        # ===== ADVANCED POLICY QUERIES (RAG) =====
        (
            "If I'm sick for a week, do I need a doctor's note and will I still get paid?",
            "POLICY",
            "Multi-part policy question (sick leave + documentation)"
        ),
        (
            "I just had a baby. What leave am I entitled to and how does it affect my benefits?",
            "POLICY",
            "Complex life event query (parental leave + benefits)"
        ),
        (
            "Can you compare the health insurance plans available to employees?",
            "POLICY",
            "Comparative analysis request"
        ),
        (
            "What happens to my unused vacation days if I quit?",
            "POLICY",
            "Policy edge case (termination scenario)"
        ),
        (
            "I need to take time off for jury duty. Is this paid and how do I request it?",
            "POLICY",
            "Specific leave type with procedural question"
        ),
        
        # ===== ADVANCED GENERAL QUERIES =====
        (
            "Explain the difference between supervised and unsupervised machine learning with examples",
            "GENERAL",
            "Complex technical explanation request"
        ),
        (
            "Write a Python decorator that measures function execution time and logs it",
            "GENERAL",
            "Advanced coding request"
        ),
        (
            "What are the key differences between REST and GraphQL APIs?",
            "GENERAL",
            "Technical comparison question"
        ),
        (
            "How would you implement a binary search tree in Python with insert and search methods?",
            "GENERAL",
            "Complex algorithmic question"
        ),
        (
            "Explain quantum computing in simple terms that a 10-year-old could understand",
            "GENERAL",
            "Explanation with specific audience constraint"
        ),
        
        # ===== EDGE CASES & AMBIGUOUS QUERIES =====
        (
            "What's the policy on remote work and can you also explain what VPN stands for?",
            "POLICY",
            "Mixed query (policy + general knowledge)"
        ),
        (
            "I'm planning to take a sabbatical next year. What should I know?",
            "POLICY",
            "Forward-looking policy question"
        ),
        (
            "How does TechCorp's 401k match compare to industry standards?",
            "POLICY",
            "Policy question with external comparison"
        ),
        (
            "Can you help me understand the difference between HSA and FSA accounts?",
            "POLICY",
            "Benefits terminology clarification"
        ),
        (
            "I want to work from a different country for 3 months. What policies apply?",
            "POLICY",
            "Complex scenario (remote work + international)"
        ),
    ]
    
    results = []
    passed_count = 0
    
    for query, expected, description in test_cases:
        passed = await test_query(query, expected, description)
        results.append((description, passed))
        if passed:
            passed_count += 1
        await asyncio.sleep(0.5)
    
    # Summary
    print("\n" + "="*70)
    print("ADVANCED TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {total - passed_count}")
    print(f"Success Rate: {(passed_count/total)*100:.1f}%")
    
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70)
    
    for description, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {description}")
    
    if passed_count == total:
        print("\n🎉 EXCELLENT! All advanced tests passed!")
        print("The agent demonstrates advanced capabilities for both RAG and general queries.")
    elif passed_count >= total * 0.8:
        print(f"\n✅ GOOD! {(passed_count/total)*100:.0f}% of advanced tests passed.")
        print("The agent handles most complex scenarios well.")
    else:
        print(f"\n⚠️  {(passed_count/total)*100:.0f}% passed. Some advanced scenarios need improvement.")

if __name__ == "__main__":
    asyncio.run(main())
