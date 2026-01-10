"""
Main AI Agent with intelligent decision-making.
Decides between direct LLM response and RAG-based retrieval.
"""

import time
import logging
from typing import Dict, Any, Optional, List
from enum import Enum

from app.llm.llm_client import llm_client
from app.llm.prompts import PromptTemplates
from app.agents.memory import memory
from app.agents.tools import tool_executor
from app.rag.retriever import retriever
from app.config import settings

logger = logging.getLogger(__name__)


class QueryType(str, Enum):
    """Query classification types."""
    GENERAL = "GENERAL"
    POLICY = "POLICY"
    CLARIFICATION = "CLARIFICATION"


class ResponseMethod(str, Enum):
    """Response generation methods."""
    DIRECT = "direct"
    RAG = "rag"
    TOOL = "tool"


class AIAgent:
    """
    Intelligent AI agent that can:
    1. Classify user queries
    2. Decide between direct response and RAG
    3. Use tools when appropriate
    4. Maintain conversation context
    """
    
    def __init__(self):
        """Initialize the AI agent."""
        self.llm_client = llm_client
        self.memory = memory
        self.tool_executor = tool_executor
        self.retriever = retriever
        self.prompts = PromptTemplates()
    
    async def classify_query(self, query: str) -> QueryType:
        """
        Classify the user query to determine handling strategy.
        
        Args:
            query: User query
            
        Returns:
            Query classification
        """
        logger.info("Classifying query...")
        
        # Get intent classification prompt
        prompt = self.prompts.get_intent_prompt(query)
        
        try:
            # Get classification from LLM
            classification = await self.llm_client.generate(
                prompt=prompt,
                temperature=0.3,  # Lower temperature for classification
                max_tokens=50
            )
            
            logger.info(f"DEBUG: Raw classification response: '{classification}'")
            classification = classification.strip().upper()
            if classification.startswith("CATEGORY:"):
                classification = classification.replace("CATEGORY:", "").strip()
            
            # Map to QueryType
            if "GENERAL" in classification:
                return QueryType.GENERAL
            elif "POLICY" in classification:
                return QueryType.POLICY
            elif "CLARIFICATION" in classification:
                return QueryType.CLARIFICATION
            else:
                # Fallback: Use keyword-based heuristics
                logger.warning(f"LLM classification unclear: '{classification}', using keyword heuristics")
                return self._classify_by_keywords(query)
        
        except Exception as e:
            logger.error(f"Error classifying query: {e}")
            # Fallback to keyword-based classification
            return self._classify_by_keywords(query)
    
    def _classify_by_keywords(self, query: str) -> QueryType:
        """
        Fallback classification using keyword matching.
        
        Args:
            query: User query
            
        Returns:
            Query classification
        """
        query_lower = query.lower()
        
        # Policy-related keywords
        policy_keywords = [
            'policy', 'leave', 'vacation', 'pto', 'sick', 'benefit', 'insurance',
            'health', '401k', 'retirement', 'dental', 'vision', 'fsa', 'hsa',
            'remote', 'work from home', 'wfh', 'parental', 'maternity', 'paternity',
            'bereavement', 'holiday', 'time off', 'compensation', 'salary',
            'bonus', 'stock', 'equity', 'employee', 'hr', 'human resources',
            'code of conduct', 'ethics', 'compliance', 'security policy', 'it policy',
            'password', 'access', 'confidential', 'data protection',
            # Travel and expense keywords
            'travel', 'expense', 'reimbursement', 'per diem', 'hotel', 'airfare',
            'rental car', 'mileage', 'business trip', 'conference',
            # Leave-specific keywords
            'fmla', 'family leave', 'medical leave', 'sabbatical', 'jury duty',
            # Performance and training
            'performance review', 'promotion', 'pip', 'tuition', 'training',
            'certification', 'development', 'mentorship', 'okr'
        ]
        
        # Check for policy keywords
        if any(keyword in query_lower for keyword in policy_keywords):
            logger.info(f"Classified as POLICY via keyword matching")
            return QueryType.POLICY
        
        # Greetings and casual conversation
        greeting_patterns = ['hello', 'hi ', 'hey', 'good morning', 'good afternoon', 
                            'how are you', 'what\'s up', 'greetings']
        if any(pattern in query_lower for pattern in greeting_patterns):
            logger.info(f"Classified as GENERAL via greeting detection")
            return QueryType.GENERAL
        
        # General knowledge indicators
        general_indicators = ['what is', 'who is', 'when did', 'where is', 'how does',
                             'explain', 'define', 'capital of', 'write a', 'create a',
                             'python', 'code', 'function', 'program', 'world cup',
                             'president', 'history', 'science', 'math']
        if any(indicator in query_lower for indicator in general_indicators):
            logger.info(f"Classified as GENERAL via general knowledge indicators")
            return QueryType.GENERAL
        
        # Very short or unclear queries
        if len(query.split()) <= 2:
            logger.info(f"Classified as CLARIFICATION (too short)")
            return QueryType.CLARIFICATION
        
        # Default to POLICY for safety (use RAG)
        logger.info(f"Defaulting to POLICY (no clear match)")
        return QueryType.POLICY
    
    async def generate_direct_response(
        self,
        query: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Generate direct response using LLM without RAG.
        
        Args:
            query: User query
            session_id: Session ID
            
        Returns:
            Response dict
        """
        logger.info("Generating direct response...")
        
        # Get conversation history
        history = self.memory.get_formatted_history(
            session_id=session_id,
            max_messages=settings.max_conversation_history,
            for_llm=True
        )
        
        # Build messages for LLM
        messages = [
            {"role": "system", "content": self.prompts.SYSTEM_AGENT}
        ]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        
        # Generate response
        answer = await self.llm_client.generate_with_history(
            messages=messages,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        return {
            "answer": answer,
            "sources": [],
            "method": ResponseMethod.DIRECT
        }
    
    async def generate_rag_response(
        self,
        query: str,
        session_id: str
    ) -> Dict[str, Any]:
        """
        Generate RAG-based response using document retrieval.
        
        Args:
            query: User query
            session_id: Session ID
            
        Returns:
            Response dict
        """
        logger.info("Generating RAG response...")
        
        # Retrieve relevant documents
        documents = await self.retriever.retrieve(
            query=query,
            top_k=settings.top_k_results
        )
        
        if not documents:
            logger.warning("No relevant documents found")
            return {
                "answer": "I don't have information about that in the available company policy documents. Could you rephrase your question or ask about something else?",
                "sources": [],
                "method": ResponseMethod.RAG
            }
        
        # Format context from documents
        rag_prompt = self.prompts.get_rag_prompt(query, documents)
        
        # Generate response
        answer = await self.llm_client.generate(
            prompt=rag_prompt,
            system_prompt=self.prompts.SYSTEM_RAG,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # Extract sources
        sources = self.retriever.format_sources(documents)
        
        return {
            "answer": answer,
            "sources": sources,
            "method": ResponseMethod.RAG,
            "retrieved_documents": len(documents)
        }
    
    async def process_query(
        self,
        query: str,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point: process user query and generate response.
        
        Args:
            query: User query
            session_id: Optional session ID
            
        Returns:
            Response with answer, sources, and metadata
        """
        start_time = time.time()
        
        # Create or get session
        if session_id is None or not self.memory.session_exists(session_id):
            session_id = self.memory.create_session(session_id)
        
        logger.info(f"Processing query for session {session_id}: {query[:100]}")
        
        # Add user message to history
        self.memory.add_message(session_id, "user", query)
        
        try:
            # Step 1: Classify query
            query_type = await self.classify_query(query)
            logger.info(f"Query classified as: {query_type.value}")
            
            # Step 2: Generate response based on classification
            if query_type == QueryType.GENERAL:
                response = await self.generate_direct_response(query, session_id)
            
            elif query_type == QueryType.POLICY:
                response = await self.generate_rag_response(query, session_id)
            
            else:  # CLARIFICATION
                response = {
                    "answer": "I'm not quite sure what you're asking. Could you please provide more details or rephrase your question?",
                    "sources": [],
                    "method": ResponseMethod.DIRECT
                }
            
            # Add assistant response to history
            self.memory.add_message(
                session_id,
                "assistant",
                response["answer"],
                sources=response.get("sources")
            )
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Build final response
            return {
                "answer": response["answer"],
                "source": response.get("sources", []),  # API spec uses "source"
                "session_id": session_id,
                "metadata": {
                    "query_type": query_type.value,
                    "method": response.get("method"),
                    "processing_time": round(processing_time, 2),
                    "provider": self.llm_client.provider,
                    "environment": settings.environment
                }
            }
        
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            
            # Return error response
            error_message = "I apologize, but I encountered an error processing your request. Please try again."
            
            self.memory.add_message(session_id, "assistant", error_message)
            
            return {
                "answer": error_message,
                "source": [],
                "session_id": session_id,
                "metadata": {
                    "error": str(e),
                    "processing_time": round(time.time() - start_time, 2)
                }
            }
    
    async def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session."""
        return self.memory.get_session_info(session_id)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        return {
            "memory": self.memory.get_stats(),
            "provider": self.llm_client.provider,
            "environment": settings.environment
        }


# Global agent instance
agent = AIAgent()
