"""
Session-based memory management for conversations.
"""

import uuid
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import asyncio
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manage conversation history for sessions."""
    
    def __init__(self):
        """Initialize memory store."""
        self.sessions: Dict[str, Dict] = {}
        self.cleanup_task = None
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new session.
        
        Args:
            session_id: Optional session ID (generates if not provided)
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            "messages": [],
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "metadata": {}
        }
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        sources: Optional[List[str]] = None
    ) -> None:
        """
        Add a message to session history.
        
        Args:
            session_id: Session ID
            role: Message role (user/assistant)
            content: Message content
            sources: Optional source documents
        """
        if session_id not in self.sessions:
            self.create_session(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow(),
            "sources": sources
        }
        
        self.sessions[session_id]["messages"].append(message)
        self.sessions[session_id]["last_activity"] = datetime.utcnow()
        
        # Trim history if too long
        max_history = settings.max_conversation_history
        if len(self.sessions[session_id]["messages"]) > max_history * 2:
            # Keep system message + last max_history pairs
            self.sessions[session_id]["messages"] = (
                self.sessions[session_id]["messages"][-(max_history * 2):]
            )
    
    def get_history(
        self,
        session_id: str,
        max_messages: Optional[int] = None
    ) -> List[Dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Session ID
            max_messages: Maximum number of messages to return
            
        Returns:
            List of messages
        """
        if session_id not in self.sessions:
            return []
        
        messages = self.sessions[session_id]["messages"]
        
        if max_messages:
            return messages[-max_messages:]
        
        return messages
    
    def get_formatted_history(
        self,
        session_id: str,
        max_messages: Optional[int] = None,
        for_llm: bool = False
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM.
        
        Args:
            session_id: Session ID
            max_messages: Maximum number of messages
            for_llm: Format for LLM API (role/content only)
            
        Returns:
            Formatted messages
        """
        messages = self.get_history(session_id, max_messages)
        
        if for_llm:
            # Format for LLM API
            return [
                {"role": msg["role"], "content": msg["content"]}
                for msg in messages
            ]
        
        return messages
    
    def session_exists(self, session_id: str) -> bool:
        """Check if session exists."""
        return session_id in self.sessions
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get session information."""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "last_activity": session["last_activity"],
            "message_count": len(session["messages"])
        }
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        timeout = timedelta(seconds=settings.session_timeout)
        now = datetime.utcnow()
        
        expired_sessions = [
            session_id
            for session_id, session in self.sessions.items()
            if now - session["last_activity"] > timeout
        ]
        
        for session_id in expired_sessions:
            self.delete_session(session_id)
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    async def start_cleanup_task(self):
        """Start background task for session cleanup."""
        while True:
            await asyncio.sleep(settings.cleanup_interval)
            self.cleanup_expired_sessions()
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        return {
            "total_sessions": len(self.sessions),
            "total_messages": sum(
                len(session["messages"])
                for session in self.sessions.values()
            ),
            "active_sessions": len([
                s for s in self.sessions.values()
                if datetime.utcnow() - s["last_activity"] < timedelta(minutes=5)
            ])
        }


# Global memory instance
memory = ConversationMemory()
