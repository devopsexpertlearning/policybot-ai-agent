"""
Unit tests for extended document processor functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.rag.document_processor import DocumentProcessor

@pytest.fixture
def mock_docx():
    """Mock python-docx."""
    with patch('app.rag.document_processor.docx') as mock:
        yield mock

class TestDocumentProcessorExtended:
    """Test extended capabilities (DOCX, logging)."""

    def test_process_docx_success(self, mock_docx):
        """Test successful DOCX processing."""
        # Setup mock document
        mock_doc = Mock()
        p1 = Mock()
        p1.text = "Paragraph 1"
        p2 = Mock()
        p2.text = "Paragraph 2"
        mock_doc.paragraphs = [p1, p2]
        
        mock_docx.Document.return_value = mock_doc
        
        processor = DocumentProcessor()
        chunks = processor.process_docx("test.docx")
        
        assert len(chunks) > 0
        assert "Paragraph 1" in chunks[0]["content"]
        assert chunks[0]["metadata"]["file_type"] == "docx"
        mock_docx.Document.assert_called_with("test.docx")

    def test_process_docx_not_installed(self):
        """Test graceful failure when python-docx is missing."""
        with patch('app.rag.document_processor.docx', None):
            processor = DocumentProcessor()
            chunks = processor.process_docx("test.docx")
            assert chunks == []

    def test_process_file_dispatch_docx(self, mock_docx):
        """Test dispatching .docx to process_docx."""
        # Setup mock
        mock_doc = Mock()
        mock_doc.paragraphs = [Mock(text="Content")]
        mock_docx.Document.return_value = mock_doc

        processor = DocumentProcessor()
        chunks = processor.process_file("test.docx")
        
        assert len(chunks) > 0
        assert chunks[0]["metadata"]["file_type"] == "docx"

    def test_process_directory_finds_docx(self, mock_docx, tmp_path):
        """Test that process_directory finds .docx files."""
        # Create a dummy docx file (empty file is enough as we mock opening)
        d = tmp_path / "documents"
        d.mkdir()
        p = d / "test.docx"
        p.touch()
        
        # Setup mock
        mock_doc = Mock()
        mock_doc.paragraphs = [Mock(text="Content")]
        mock_docx.Document.return_value = mock_doc
        
        processor = DocumentProcessor()
        chunks = processor.process_directory(str(d))
        
        # Should call process_docx which uses our mock
        assert len(chunks) > 0
        mock_docx.Document.assert_called()
