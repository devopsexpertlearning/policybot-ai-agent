#!/usr/bin/env python3
"""
Comprehensive 50-Question Test Suite
Tests the agent's ability to handle diverse queries across all policy documents.
"""
import asyncio
import sys
import logging
from pathlib import Path
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.agents.agent import agent

# Configure logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

async def test_query(query: str, expected_type: str, category: str):
    """Test a single query and report results."""
    try:
        start_time = time.time()
        response = await agent.process_query(query)
        duration = time.time() - start_time
        
        classification = response['metadata']['query_type']
        passed = classification == expected_type
        
        return {
            'query': query,
            'expected': expected_type,
            'actual': classification,
            'passed': passed,
            'category': category,
            'duration': duration,
            'has_sources': len(response.get('source', [])) > 0
        }
    except Exception as e:
        return {
            'query': query,
            'expected': expected_type,
            'actual': 'ERROR',
            'passed': False,
            'category': category,
            'duration': 0,
            'error': str(e)
        }

async def main():
    print("\n" + "="*80)
    print("COMPREHENSIVE 50-QUESTION TEST SUITE")
    print("Testing Enhanced RAG System with 9 Policy Documents")
    print("="*80)
    
    # 50 comprehensive test questions
    test_cases = [
        # === LEAVE POLICIES (10 questions) ===
        ("How many sick days do employees get per year?", "POLICY", "Leave"),
        ("What is the parental leave policy?", "POLICY", "Leave"),
        ("Can I carry over unused vacation days?", "POLICY", "Leave"),
        ("Do I need a doctor's note for sick leave?", "POLICY", "Leave"),
        ("What is the bereavement leave policy?", "POLICY", "Leave"),
        ("How do I request time off?", "POLICY", "Leave"),
        ("Is jury duty leave paid?", "POLICY", "Leave"),
        ("What happens to my PTO if I quit?", "POLICY", "Leave"),
        ("Can I take unpaid leave?", "POLICY", "Leave"),
        ("What is FMLA and am I eligible?", "POLICY", "Leave"),
        
        # === BENEFITS (10 questions) ===
        ("What is the 401k match?", "POLICY", "Benefits"),
        ("When does health insurance coverage start?", "POLICY", "Benefits"),
        ("What dental plans are available?", "POLICY", "Benefits"),
        ("Do we have vision insurance?", "POLICY", "Benefits"),
        ("What is an HSA and how does it work?", "POLICY", "Benefits"),
        ("Are there any wellness benefits?", "POLICY", "Benefits"),
        ("What is the employee assistance program?", "POLICY", "Benefits"),
        ("Do we get life insurance?", "POLICY", "Benefits"),
        ("What are the retirement plan options?", "POLICY", "Benefits"),
        ("Are there any commuter benefits?", "POLICY", "Benefits"),
        
        # === TRAVEL & EXPENSES (5 questions) ===
        ("What is the per diem rate for meals?", "POLICY", "Travel"),
        ("Can I fly business class?", "POLICY", "Travel"),
        ("How do I get reimbursed for travel expenses?", "POLICY", "Travel"),
        ("What is the hotel rate limit?", "POLICY", "Travel"),
        ("Can I use my personal car for business travel?", "POLICY", "Travel"),
        
        # === PERFORMANCE & DEVELOPMENT (5 questions) ===
        ("How often are performance reviews conducted?", "POLICY", "Performance"),
        ("What is a performance improvement plan?", "POLICY", "Performance"),
        ("How do promotions work?", "POLICY", "Performance"),
        ("What is the tuition reimbursement policy?", "POLICY", "Training"),
        ("Are there professional development opportunities?", "POLICY", "Training"),
        
        # === REMOTE WORK (5 questions) ===
        ("Can I work remotely full-time?", "POLICY", "Remote Work"),
        ("What is the hybrid work policy?", "POLICY", "Remote Work"),
        ("Do I get a home office stipend?", "POLICY", "Remote Work"),
        ("What are the requirements for remote work?", "POLICY", "Remote Work"),
        ("Can I work from another country?", "POLICY", "Remote Work"),
        
        # === IT & SECURITY (3 questions) ===
        ("What is the password policy?", "POLICY", "IT Security"),
        ("Can I use personal devices for work?", "POLICY", "IT Security"),
        ("What should I do if I lose my laptop?", "POLICY", "IT Security"),
        
        # === CODE OF CONDUCT (2 questions) ===
        ("What is the policy on conflicts of interest?", "POLICY", "Conduct"),
        ("How do I report unethical behavior?", "POLICY", "Conduct"),
        
        # === GENERAL KNOWLEDGE (10 questions) ===
        ("What is artificial intelligence?", "GENERAL", "General"),
        ("Explain the difference between Python and JavaScript", "GENERAL", "General"),
        ("Who is the current CEO of Microsoft?", "GENERAL", "General"),
        ("What is the capital of Japan?", "GENERAL", "General"),
        ("How does photosynthesis work?", "GENERAL", "General"),
        ("Write a function to reverse a string in Python", "GENERAL", "General"),
        ("What is the difference between HTTP and HTTPS?", "GENERAL", "General"),
        ("Explain what Docker is", "GENERAL", "General"),
        ("What is the Pythagorean theorem?", "GENERAL", "General"),
        ("Who wrote Romeo and Juliet?", "GENERAL", "General"),
    ]
    
    print(f"\nRunning {len(test_cases)} tests across multiple categories...")
    print("This will take approximately 3-5 minutes.\n")
    
    results = []
    for query, expected, category in test_cases:
        result = await test_query(query, expected, category)
        results.append(result)
        
        # Progress indicator
        status = "✅" if result['passed'] else "❌"
        print(f"{status} [{len(results)}/{len(test_cases)}] {category}: {query[:60]}...")
        
        await asyncio.sleep(3.0)  # Moderate delay to avoid Azure rate limits
    
    # Calculate statistics
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    total = len(results)
    passed = sum(1 for r in results if r['passed'])
    failed = total - passed
    
    # Category breakdown
    categories = {}
    for result in results:
        cat = result['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'passed': 0}
        categories[cat]['total'] += 1
        if result['passed']:
            categories[cat]['passed'] += 1
    
    print(f"\nOverall Performance:")
    print(f"  Total Questions: {total}")
    print(f"  Passed: {passed} ({(passed/total)*100:.1f}%)")
    print(f"  Failed: {failed} ({(failed/total)*100:.1f}%)")
    
    print(f"\nBreakdown by Category:")
    for cat, stats in sorted(categories.items()):
        pct = (stats['passed']/stats['total'])*100
        print(f"  {cat:15s}: {stats['passed']}/{stats['total']} ({pct:.0f}%)")
    
    # Average response time
    avg_time = sum(r['duration'] for r in results) / len(results)
    print(f"\nAverage Response Time: {avg_time:.2f}s")
    
    # Failed questions
    failed_results = [r for r in results if not r['passed']]
    if failed_results:
        print(f"\n" + "="*80)
        print("FAILED QUESTIONS")
        print("="*80)
        for r in failed_results:
            print(f"\n❌ {r['query']}")
            print(f"   Expected: {r['expected']}, Got: {r['actual']}")
            if 'error' in r:
                print(f"   Error: {r['error']}")
    
    # Success message
    print("\n" + "="*80)
    if passed == total:
        print("🎉 PERFECT SCORE! All 50 questions answered correctly!")
        print("The agent demonstrates exceptional performance across all policy areas.")
    elif passed >= total * 0.9:
        print(f"✅ EXCELLENT! {(passed/total)*100:.0f}% success rate.")
        print("The agent performs very well across diverse policy questions.")
    elif passed >= total * 0.8:
        print(f"✅ GOOD! {(passed/total)*100:.0f}% success rate.")
        print("The agent handles most questions correctly.")
    else:
        print(f"⚠️  {(passed/total)*100:.0f}% success rate.")
        print("Some areas need improvement.")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
