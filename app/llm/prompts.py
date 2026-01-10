"""
Prompt templates and engineering for the AI agent.
"""

from typing import List, Dict, Any


class PromptTemplates:
    """Centralized prompt templates for different scenarios."""
    
    # System prompts
    SYSTEM_AGENT = """You are an intelligent AI assistant helping employees with company policy questions.

Your capabilities:
1. Answer general questions directly using your knowledge
2. Search company policy documents when questions are about specific policies
3. Provide accurate, helpful, and concise responses

Guidelines:
- Be professional and friendly
- Cite sources when using document information
- If you don't know something, say so honestly
- Ask clarifying questions when needed

Current conversation context will be provided below."""

    SYSTEM_RAG = """You are an AI assistant answering questions based on company policy documents.

CRITICAL INSTRUCTIONS:
1. Answer ONLY based on the provided context
2. If the context doesn't contain the answer, say "I don't have information about that in the available documents"
3. Always cite the source document(s) used
4. Be specific and accurate
5. Don't make up information

Context documents will be provided below."""

    # Decision-making prompt
    INTENT_CLASSIFICATION = """Classify the query into: GENERAL, POLICY, or CLARIFICATION.

Query: "What is the sick leave policy?"
Category: POLICY

Query: "Hello, how are you?"
Category: GENERAL

Query: "Can I use my personal phone for work?"
Category: POLICY

Query: "What is the capital of France?"
Category: GENERAL

Query: "I don't understand"
Category: CLARIFICATION

Query: "Write a python script to parse CSV"
Category: GENERAL

Query: "{query}"
Category:"""

    # RAG prompt with context
    RAG_WITH_CONTEXT = """You are a helpful AI assistant answering questions based on the provided company policy documents.

STRICT INSTRUCTIONS:
1. Answer the question using ONLY the information from the context below.
2. If the answer is not in the context, strictly state: "I don't have information about that in the available company policy documents."
3. Do not use outside knowledge or make up information.
4. Cite the document source for your answer (e.g. [Source: leave_policy.txt]).

CONTEXT DOCUMENTS:
{context}

USER QUESTION: {query}

Answer:"""

    # Direct answer prompt
    DIRECT_ANSWER = """Previous conversation:
{history}

User question: {query}

Provide a helpful, accurate, and concise answer.

Answer:"""

    # Conversation summary (for memory compression)
    CONVERSATION_SUMMARY = """Summarize the key points from this conversation:

{conversation}

Provide a concise summary highlighting:
1. Main topics discussed
2. Important information exchanged  
3. Any pending questions or actions

Summary:"""

    @staticmethod
    def format_context(chunks: List[Dict[str, Any]], max_length: int = 3000) -> str:
        """Format retrieved chunks into context string."""
        context_parts = []
        
        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("metadata", {}).get("source", "Unknown")
            page = chunk.get("metadata", {}).get("page", "")
            content = chunk.get("content", "")
            
            page_info = f" (Page {page})" if page else ""
            context_parts.append(f"[Document {i}: {source}{page_info}]\n{content}\n")
        
        context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > max_length:
            context = context[:max_length] + "\n...[Context truncated]"
        
        return context
    
    @staticmethod
    def format_history(messages: List[Dict[str, str]], max_messages: int = 5) -> str:
        """Format conversation history."""
        if not messages:
            return "No previous conversation."
        
        # Take last N messages
        recent_messages = messages[-max_messages:]
        
        history_parts = []
        for msg in recent_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            prefix = "User:" if role == "user" else "Assistant:"
            history_parts.append(f"{prefix} {content}")
        
        return "\n".join(history_parts)
    
    @staticmethod
    def get_rag_prompt(query: str, chunks: List[Dict[str, Any]]) -> str:
        """Get RAG prompt with formatted context."""
        context = PromptTemplates.format_context(chunks)
        return PromptTemplates.RAG_WITH_CONTEXT.format(
            context=context,
            query=query
        )
    
    @staticmethod
    def get_direct_prompt(query: str, history: List[Dict[str, str]]) -> str:
        """Get direct answer prompt with history."""
        formatted_history = PromptTemplates.format_history(history)
        return PromptTemplates.DIRECT_ANSWER.format(
            history=formatted_history,
            query=query
        )
    
    @staticmethod
    def get_intent_prompt(query: str) -> str:
        """Get intent classification prompt."""
        return PromptTemplates.INTENT_CLASSIFICATION.format(query=query)


# Few-shot examples for better performance
FEW_SHOT_EXAMPLES = {
    "intent_classification": [
        {
            "query": "What is the company's vacation policy?",
            "classification": "POLICY"
        },
        {
            "query": "How does photosynthesis work?",
            "classification": "GENERAL"
        },
        {
            "query": "Tell me more about that",
            "classification": "CLARIFICATION"
        }
    ],
    "rag_answer": [
        {
            "context": "Employees are entitled to 15 days of paid vacation per year.",
            "query": "How many vacation days do I get?",
            "answer": "According to the company policy, employees are entitled to 15 days of paid vacation per year. [Source: Company Handbook]"
        }
    ]
}
