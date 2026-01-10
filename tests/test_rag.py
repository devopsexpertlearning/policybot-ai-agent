"""
Tests for the RAG pipeline.
"""

import pytest
from app.rag.document_processor import DocumentProcessor
from pathlib import Path


class TestRAG:
    """Test RAG components."""
    
    @pytest.fixture
    def processor(self):
        """Create document processor."""
        return DocumentProcessor()
    
    def test_processor_initialization(self, processor):
        """Test processor initializes with correct settings."""
        assert processor.chunk_size > 0
        assert processor.chunk_overlap >= 0
        assert processor.chunk_overlap < processor.chunk_size
    
    def test_text_cleaning(self, processor):
        """Test text cleaning."""
        dirty_text = "This  has   multiple    spaces  "
        clean_text = processor._clean_text(dirty_text)
        assert "  " not in clean_text
        assert clean_text == clean_text.strip()
    
    def test_text_splitting(self, processor):
        """Test text splitting into chunks."""
        text = " ".join(["word"] * 1000)
        chunks = processor._split_text(text)
        
        assert len(chunks) > 1
        for chunk in chunks:
            words = chunk.split()
            assert len(words) <= processor.chunk_size
    
    def test_document_stats(self, processor):
        """Test document statistics calculation."""
        chunks = [
            {
                "content": "test content",
                "metadata": {"source": "doc1.txt"}
            },
            {
                "content": "more test content",
                "metadata": {"source": "doc2.txt"}
            }
        ]
        
        stats = processor.get_document_stats(chunks)
        assert stats["total_chunks"] == 2
        assert stats["unique_sources"] == 2
        assert "sources" in stats
