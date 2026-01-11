"""
Unit tests for document processor.
"""

import pytest
from pathlib import Path
from app.rag.document_processor import DocumentProcessor


@pytest.mark.unit
class TestDocumentProcessor:
    """Test document processing functionality."""
    
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
        dirty_text = "This  has   multiple    spaces  \n\n\n  and newlines  "
        clean_text = processor._clean_text(dirty_text)
        
        assert "  " not in clean_text
        assert clean_text == clean_text.strip()
        assert "\n\n\n" not in clean_text
    
    def test_text_cleaning_preserves_content(self, processor):
        """Test text cleaning preserves actual content."""
        text = "Important policy: Employees get 15 days vacation."
        clean_text = processor._clean_text(text)
        
        assert "Important policy" in clean_text
        assert "15 days vacation" in clean_text
    
    def test_text_splitting(self, processor):
        """Test text splitting into chunks."""
        text = " ".join(["word"] * 1000)
        chunks = processor._split_text(text)
        
        assert len(chunks) > 1
        for chunk in chunks:
            words = chunk.split()
            assert len(words) <= processor.chunk_size
    
    def test_text_splitting_with_overlap(self, processor):
        """Test chunks have proper overlap."""
        text = " ".join([f"word{i}" for i in range(1000)])
        chunks = processor._split_text(text)
        
        # Check that consecutive chunks have overlap
        if len(chunks) > 1:
            chunk1_words = set(chunks[0].split()[-processor.chunk_overlap:])
            chunk2_words = set(chunks[1].split()[:processor.chunk_overlap])
            # There should be some overlap
            assert len(chunk1_words.intersection(chunk2_words)) > 0
    
    def test_process_text_file(self, processor, tmp_path, sample_text):
        """Test processing a text file."""
        # Create temporary text file
        test_file = tmp_path / "test.txt"
        test_file.write_text(sample_text)
        
        chunks = processor.process_file(str(test_file))
        
        assert len(chunks) > 0
        for chunk in chunks:
            assert "content" in chunk
            assert "metadata" in chunk
            assert chunk["metadata"]["source"] == "test.txt"
    
    def test_process_file_metadata(self, processor, tmp_path):
        """Test file processing includes correct metadata."""
        test_file = tmp_path / "policy.txt"
        test_file.write_text("This is a test policy document.")
        
        chunks = processor.process_file(str(test_file))
        
        assert len(chunks) > 0
        chunk = chunks[0]
        assert chunk["metadata"]["source"] == "policy.txt"
        assert "chunk_id" in chunk["metadata"]
        assert chunk["metadata"]["chunk_id"] == "1"
    
    def test_process_directory(self, processor, tmp_path):
        """Test processing a directory of files."""
        # Create multiple test files
        (tmp_path / "file1.txt").write_text("Content of file 1. " * 100)
        (tmp_path / "file2.txt").write_text("Content of file 2. " * 100)
        (tmp_path / "file3.txt").write_text("Content of file 3. " * 100)
        
        chunks = processor.process_directory(str(tmp_path))
        
        assert len(chunks) > 0
        sources = set(chunk["metadata"]["source"] for chunk in chunks)
        assert len(sources) == 3
    
    def test_get_document_stats(self, processor, sample_chunks):
        """Test document statistics calculation."""
        stats = processor.get_document_stats(sample_chunks)
        
        assert stats["total_chunks"] == len(sample_chunks)
        assert "unique_sources" in stats
        assert "sources" in stats
        assert isinstance(stats["sources"], list)
    
    def test_empty_file_handling(self, processor, tmp_path):
        """Test handling of empty files."""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        
        chunks = processor.process_file(str(empty_file))
        assert len(chunks) == 0
    
    def test_chunk_size_configuration(self):
        """Test processor with custom chunk size."""
        processor = DocumentProcessor(chunk_size=100, chunk_overlap=10)
        
        assert processor.chunk_size == 100
        assert processor.chunk_overlap == 10
    
    def test_process_long_document(self, processor):
        """Test processing a long document."""
        long_text = " ".join(["word"] * 5000)
        chunks = processor._split_text(long_text)
        
        assert len(chunks) > 5
        # Verify all chunks are within size limit
        for chunk in chunks:
            assert len(chunk.split()) <= processor.chunk_size
