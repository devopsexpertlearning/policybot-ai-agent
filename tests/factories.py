"""
Test data factories for generating realistic test data.
"""

import random
import uuid
from typing import List, Dict, Any
from datetime import datetime


class QueryFactory:
    """Factory for generating test queries."""
    
    @staticmethod
    def general_query() -> str:
        """Generate a general knowledge query."""
        queries = [
            "What is the capital of France?",
            "Who invented the telephone?",
            "When was Python created?",
            "How does photosynthesis work?",
            "Why is the sky blue?",
            "What is 25 times 4?",
            "Tell me a joke",
            "What is the weather like?",
        ]
        return random.choice(queries)
    
    @staticmethod
    def policy_query() -> str:
        """Generate a policy-related query."""
        queries = [
            "What is the leave policy?",
            "How many vacation days do I get?",
            "What is the remote work policy?",
            "What are the health benefits?",
            "What is the code of conduct?",
            "How do I request time off?",
            "What is the dress code?",
            "What are the working hours?",
            "What is the parental leave policy?",
            "How does the 401k match work?",
        ]
        return random.choice(queries)
    
    @staticmethod
    def clarification_query() -> str:
        """Generate an unclear query."""
        return random.choice([
            "huh?",
            "what?",
            "...",
            "tell me",
            "info",
            "help",
            "?",
        ])


class DocumentFactory:
    """Factory for generating test documents."""
    
    @staticmethod
    def create_chunk(source: str = None, chunk_id: int = 0) -> Dict[str, Any]:
        """Create a document chunk."""
        content_templates = [
            "Employees are entitled to {days} days of paid vacation per year.",
            "Remote work is allowed up to {days} days per week with manager approval.",
            "All employees must complete annual security training by {month}.",
            "Health insurance coverage begins on the first day of the month following hire date.",
            "The company matches 401k contributions up to {percent}% of salary.",
        ]
        
        content = random.choice(content_templates).format(
            days=random.randint(10, 30),
            month=random.choice(["January", "March", "June", "December"]),
            percent=random.randint(3, 6)
        )
        
        return {
            "content": content,
            "metadata": {
                "source": source or f"policy_{random.randint(1, 5)}.txt",
                "chunk_id": chunk_id,
                "page": random.randint(1, 10)
            }
        }
    
    @staticmethod
    def create_chunks(count: int = 5, source: str = None) -> List[Dict[str, Any]]:
        """Create multiple document chunks."""
        source = source or f"policy_{random.randint(1, 5)}.txt"
        return [
            DocumentFactory.create_chunk(source, i)
            for i in range(count)
        ]


class ResponseFactory:
    """Factory for generating test responses."""
    
    @staticmethod
    def agent_response(
        answer: str = None,
        sources: List[str] = None,
        session_id: str = None,
        method: str = None
    ) -> Dict[str, Any]:
        """Create an agent response."""
        return {
            "answer": answer or "This is a test response to your query.",
            "source": sources or ["policy.txt"],
            "session_id": session_id or str(uuid.uuid4()),
            "metadata": {
                "method": method or random.choice(["direct", "rag"]),
                "processing_time": round(random.uniform(0.5, 2.5), 2),
                "query_type": random.choice(["GENERAL", "POLICY", "CLARIFICATION"]),
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def api_response(status_code: int = 200, **kwargs) -> Dict[str, Any]:
        """Create an API response."""
        if status_code == 200:
            return ResponseFactory.agent_response(**kwargs)
        elif status_code == 422:
            return {
                "detail": [
                    {
                        "loc": ["body", "query"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ]
            }
        elif status_code == 500:
            return {
                "error": "Internal server error",
                "detail": "An error occurred processing your request"
            }
        return {}
