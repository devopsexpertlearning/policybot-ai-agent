#!/usr/bin/env python3
"""
Comprehensive 100-Question Test Suite
Tests the agent's ability to handle diverse queries across all policy documents,
including the new PDF and DOCX files.
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
        
        # Determine if test passed
        passed = False
        actual_answer = response.get('answer', '')
        
        # Policy queries should retrieve sources and have a policy classification
        if expected_type == "POLICY":
            if classification == "POLICY" and len(response.get('source', [])) > 0:
                if "I don't have information" not in actual_answer:
                    passed = True
        
        # General queries should have GENERAL classification
        elif expected_type == "GENERAL":
            if classification == "GENERAL":
                passed = True
                
        return {
            'query': query,
            'expected': expected_type,
            'actual': classification,
            'passed': passed,
            'category': category,
            'duration': duration,
            'answer_snippet': actual_answer[:100] + "..." if len(actual_answer) > 100 else actual_answer,
            'sources': response.get('source', [])
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
    print("COMPREHENSIVE 100-QUESTION TEST SUITE")
    print("Testing Enhanced RAG System with PDF, DOCX, and Text Documents")
    print("="*80)
    
    test_cases = [
        # === LEAVE POLICIES (15 questions) ===
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
        ("What is the sabbatical leave policy?", "POLICY", "Leave"), # New
        ("How much voting leave do I get?", "POLICY", "Leave"), # New
        ("What counts as immediate family for bereavement?", "POLICY", "Leave"), # New
        ("What is the maximum PTO accrual?", "POLICY", "Leave"), # New
        ("Who is eligible for sick leave?", "POLICY", "Leave"), # New
        
        # === BENEFITS (15 questions) ===
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
        ("What is short-term disability coverage?", "POLICY", "Benefits"), # New
        ("Do we have pet insurance?", "POLICY", "Benefits"), # New (Might be "no info" but should process)
        ("Is there a gym reimbursement?", "POLICY", "Benefits"), # New
        ("What are the mental health benefits?", "POLICY", "Benefits"), # New
        ("How do I enroll in benefits?", "POLICY", "Benefits"), # New
        
        # === TRAVEL & EXPENSES (10 questions) ===
        ("What is the per diem rate for meals?", "POLICY", "Travel"),
        ("Can I fly business class?", "POLICY", "Travel"),
        ("How do I get reimbursed for travel expenses?", "POLICY", "Travel"),
        ("What is the hotel rate limit?", "POLICY", "Travel"),
        ("Can I use my personal car for business travel?", "POLICY", "Travel"),
        ("What is the receipt requirement?", "POLICY", "Travel"), # New
        ("Can I expense client entertainment?", "POLICY", "Travel"), # New
        ("What is the policy on alcohol expenses?", "POLICY", "Travel"), # New
        ("How soon must expense reports be submitted?", "POLICY", "Travel"), # New
        ("Is laundry reimbursable during travel?", "POLICY", "Travel"), # New
        
        # === PERFORMANCE & DEVELOPMENT (10 questions) ===
        ("How often are performance reviews conducted?", "POLICY", "Performance"),
        ("What is a performance improvement plan?", "POLICY", "Performance"),
        ("How do promotions work?", "POLICY", "Performance"),
        ("What is the tuition reimbursement policy?", "POLICY", "Training"),
        ("Are there professional development opportunities?", "POLICY", "Training"),
        ("What is the annual training budget?", "POLICY", "Training"), # New
        ("How are bonuses calculated?", "POLICY", "Performance"), # New
        ("What is the mentoring program?", "POLICY", "Training"), # New
        ("Can I attend conferences?", "POLICY", "Training"), # New
        ("What are the core competencies evaluated?", "POLICY", "Performance"), # New
        
        # === REMOTE WORK (10 questions) ===
        ("Can I work remotely full-time?", "POLICY", "Remote Work"),
        ("What is the hybrid work policy?", "POLICY", "Remote Work"),
        ("Do I get a home office stipend?", "POLICY", "Remote Work"),
        ("What are the requirements for remote work?", "POLICY", "Remote Work"),
        ("Can I work from another country?", "POLICY", "Remote Work"),
        ("Who approves remote work requests?", "POLICY", "Remote Work"), # New
        ("What are the working hours for remote employees?", "POLICY", "Remote Work"), # New
        ("Is internet reimbursed for remote work?", "POLICY", "Remote Work"), # New
        ("Can I work from a coffee shop?", "POLICY", "Remote Work"), # New
        ("What equipment is provided for remote work?", "POLICY", "Remote Work"), # New
        
        # === IT & SECURITY (10 questions) ===
        ("What is the password policy?", "POLICY", "IT Security"),
        ("Can I use personal devices for work?", "POLICY", "IT Security"),
        ("What should I do if I lose my laptop?", "POLICY", "IT Security"),
        ("Is two-factor authentication required?", "POLICY", "IT Security"), # New
        ("What is the policy on installing software?", "POLICY", "IT Security"), # New
        ("How do I report a security incident?", "POLICY", "IT Security"), # New
        ("What is the clean desk policy?", "POLICY", "IT Security"), # New
        ("Can I use a USB drive?", "POLICY", "IT Security"), # New
        ("What is the data classification policy?", "POLICY", "IT Security"), # New
        ("How often should I change my password?", "POLICY", "IT Security"), # New
        
        # === PRIVACY POLICY (DOCX) (10 questions) ===
        ("What is the privacy policy?", "POLICY", "Privacy (DOCX)"),
        ("What personal information is collected?", "POLICY", "Privacy (DOCX)"),
        ("How is my data used?", "POLICY", "Privacy (DOCX)"),
        ("Do you share data with third parties?", "POLICY", "Privacy (DOCX)"),
        ("How long is data retained?", "POLICY", "Privacy (DOCX)"),
        ("What are my privacy rights?", "POLICY", "Privacy (DOCX)"),
        ("How is data secured?", "POLICY", "Privacy (DOCX)"),
        ("Who is the data protection officer?", "POLICY", "Privacy (DOCX)"),
        ("What are cookies used for?", "POLICY", "Privacy (DOCX)"),
        ("How can I request data deletion?", "POLICY", "Privacy (DOCX)"),
        
        # === COMPANY PROCEDURES (PDF) (10 questions) ===
        ("What are the company procedures for June?", "POLICY", "Procedures (PDF)"),
        ("What is the effective date of the latest policy update?", "POLICY", "Procedures (PDF)"),
        ("Who approved the June procedures?", "POLICY", "Procedures (PDF)"),
        ("What is the scope of the company policy?", "POLICY", "Procedures (PDF)"),
        ("Are there specific safety procedures?", "POLICY", "Procedures (PDF)"),
        ("What is the procedure for document retention?", "POLICY", "Procedures (PDF)"),
        ("How are policy violations handled?", "POLICY", "Procedures (PDF)"),
        ("What is the revision history of the policy?", "POLICY", "Procedures (PDF)"),
        ("Who is responsible for policy enforcement?", "POLICY", "Procedures (PDF)"),
        ("Where can I find the full procedure manual?", "POLICY", "Procedures (PDF)"),

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
    print("This will take approximately 5-8 minutes.\n")
    
    results = []
    # Using a semaphore to limit concurrency if we were parallelizing, 
    # but sequential with delay is safer for rate limits.
    
    for i, (query, expected, category) in enumerate(test_cases, 1):
        result = await test_query(query, expected, category)
        results.append(result)
        
        # Progress indicator
        status = "✅" if result['passed'] else "❌"
        print(f"{status} [{i}/{len(test_cases)}] {category}: {query[:50]}...")
        print(f"   Answer: {result['answer_snippet']}")
        
        # Small delay to apply backpressure
        await asyncio.sleep(1.0)
    
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
        print(f"  {cat:20s}: {stats['passed']}/{stats['total']} ({pct:.0f}%)")
    
    # Failed questions
    failed_results = [r for r in results if not r['passed']]
    if failed_results:
        print(f"\n" + "="*80)
        print("FAILED QUESTIONS")
        print("="*80)
        for r in failed_results:
            print(f"\n❌ {r['category']}: {r['query']}")
            print(f"   Expected: {r['expected']}, Got: {r['actual']}")
            print(f"   Answer: {r['answer_snippet']}")
            if 'error' in r:
                print(f"   Error: {r['error']}")
    
    # Success message
    print("\n" + "="*80)
    if passed == total:
        print("🎉 PERFECT SCORE! All 100 questions answered correctly!")
    elif passed >= total * 0.9:
        print(f"✅ EXCELLENT! {(passed/total)*100:.0f}% success rate.")
    elif passed >= total * 0.8:
        print(f"✅ GOOD! {(passed/total)*100:.0f}% success rate.")
    else:
        print(f"⚠️  {(passed/total)*100:.0f}% success rate.")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(main())
