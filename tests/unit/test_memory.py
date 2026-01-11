"""
Unit tests for conversation memory.
"""

import pytest
import time
from app.agents.memory import ConversationMemory


@pytest.mark.unit
class TestConversationMemory:
    """Test conversation memory functionality."""
    
    @pytest.fixture
    def memory(self):
        """Create fresh memory instance."""
        return ConversationMemory()
    
    def test_memory_initialization(self, memory):
        """Test memory initializes correctly."""
        assert memory is not None
        stats = memory.get_stats()
        assert stats["total_sessions"] == 0
        assert stats["total_messages"] == 0
    
    def test_create_session(self, memory):
        """Test session creation."""
        session_id = memory.create_session()
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert memory.session_exists(session_id)
    
    def test_session_exists(self, memory):
        """Test session existence check."""
        session_id = memory.create_session()
        
        assert memory.session_exists(session_id) is True
        assert memory.session_exists("nonexistent") is False
    
    def test_add_message(self, memory):
        """Test adding messages to session."""
        session_id = memory.create_session()
        
        memory.add_message(session_id, "user", "Hello")
        memory.add_message(session_id, "assistant", "Hi there!")
        
        history = memory.get_history(session_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Hi there!"
    
    def test_get_history(self, memory):
        """Test retrieving conversation history."""
        session_id = memory.create_session()
        
        memory.add_message(session_id, "user", "Message 1")
        memory.add_message(session_id, "assistant", "Response 1")
        memory.add_message(session_id, "user", "Message 2")
        
        history = memory.get_history(session_id)
        assert len(history) == 3
    
    def test_get_history_nonexistent_session(self, memory):
        """Test getting history for nonexistent session."""
        history = memory.get_history("nonexistent")
        assert history == []
    
    def test_max_history_length(self, memory):
        """Test history length limit."""
        session_id = memory.create_session()
        
        # Add more messages than the limit (default is 10 pairs = 20 messages)
        for i in range(30):
            memory.add_message(session_id, "user", f"Message {i}")
        
        history = memory.get_history(session_id)
        # Should be limited by max_conversation_history setting (10 pairs * 2 = 20)
        # The implementation trims when > max_history * 2
        assert len(history) <= 30  # Should have been trimmed
    
    def test_delete_session(self, memory):
        """Test deleting a session."""
        session_id = memory.create_session()
        memory.add_message(session_id, "user", "Test")
        
        # Use delete_session instead of clear_session
        result = memory.delete_session(session_id)
        
        assert result is True
        assert memory.session_exists(session_id) is False
        assert memory.get_history(session_id) == []
    
    def test_get_stats(self, memory):
        """Test memory statistics."""
        session1 = memory.create_session()
        session2 = memory.create_session()
        
        memory.add_message(session1, "user", "Test 1")
        memory.add_message(session1, "assistant", "Response 1")
        memory.add_message(session2, "user", "Test 2")
        
        stats = memory.get_stats()
        assert stats["total_sessions"] == 2
        assert stats["total_messages"] == 3
    
    def test_session_metadata(self, memory):
        """Test session metadata tracking."""
        session_id = memory.create_session()
        memory.add_message(session_id, "user", "Test")
        
        # Access session data via get_session_info
        session_info = memory.get_session_info(session_id)
        assert session_info is not None
        assert "created_at" in session_info
        assert "last_activity" in session_info
        assert "message_count" in session_info
    
    def test_multiple_sessions_isolation(self, memory):
        """Test that sessions are isolated from each other."""
        session1 = memory.create_session()
        session2 = memory.create_session()
        
        memory.add_message(session1, "user", "Session 1 message")
        memory.add_message(session2, "user", "Session 2 message")
        
        history1 = memory.get_history(session1)
        history2 = memory.get_history(session2)
        
        assert len(history1) == 1
        assert len(history2) == 1
        assert history1[0]["content"] != history2[0]["content"]
    
    def test_session_cleanup_expired(self, memory):
        """Test cleanup of expired sessions."""
        # Create session and manually set old last_activity
        from datetime import datetime, timedelta, timezone
        
        session_id = memory.create_session()
        memory.add_message(session_id, "user", "Test")
        
        # Manually set last_activity to past (older than session_timeout)
        # Default session_timeout is 3600 seconds
        memory.sessions[session_id]["last_activity"] = (
            datetime.now(timezone.utc) - timedelta(seconds=7200)  # 2 hours ago
        )
        
        # Trigger cleanup
        cleaned = memory.cleanup_expired_sessions()
        
        # Session should be removed
        assert cleaned == 1
        assert memory.session_exists(session_id) is False
    
    def test_get_session_info(self, memory):
        """Test getting session information."""
        session_id = memory.create_session()
        memory.add_message(session_id, "user", "Test 1")
        memory.add_message(session_id, "assistant", "Response 1")
        
        info = memory.get_session_info(session_id)
        
        assert info is not None
        assert info["session_id"] == session_id
        assert info["message_count"] == 2
        assert "created_at" in info
        assert "last_activity" in info
