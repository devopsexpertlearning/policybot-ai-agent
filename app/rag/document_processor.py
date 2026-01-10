"""
Document processing for PDFs and text files.
Extracts text, splits into chunks, and prepares for embedding.
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging
from pypdf import PdfReader
import re

from app.config import settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process documents for RAG pipeline."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize document processor.
        
        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Overlap between chunks in tokens
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    def process_pdf(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process PDF file and extract text.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            List of chunks with metadata
        """
        logger.info(f"Processing PDF: {file_path}")
        
        try:
            reader = PdfReader(file_path)
            chunks = []
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                
                if text.strip():
                    # Clean text
                    text = self._clean_text(text)
                    
                    # Split into chunks
                    page_chunks = self._split_text(text)
                    
                    # Add metadata
                    for chunk_id, chunk_text in enumerate(page_chunks, 1):
                        chunks.append({
                            "content": chunk_text,
                            "metadata": {
                                "source": os.path.basename(file_path),
                                "page": page_num,
                                "chunk_id": f"{page_num}-{chunk_id}",
                                "file_path": file_path,
                                "file_type": "pdf"
                            }
                        })
            
            logger.info(f"Extracted {len(chunks)} chunks from {len(reader.pages)} pages")
            return chunks
        
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {e}")
            return []
    
    def process_text(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Process text file.
        
        Args:
            file_path: Path to text file
            
        Returns:
            List of chunks with metadata
        """
        logger.info(f"Processing text file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Clean text
            text = self._clean_text(text)
            
            # Split into chunks
            text_chunks = self._split_text(text)
            
            # Add metadata
            chunks = []
            for chunk_id, chunk_text in enumerate(text_chunks, 1):
                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "source": os.path.basename(file_path),
                        "chunk_id": str(chunk_id),
                        "file_path": file_path,
                        "file_type": "txt"
                    }
                })
            
            logger.info(f"Extracted {len(chunks)} chunks from text file")
            return chunks
        
        except Exception as e:
            logger.error(f"Error processing text file {file_path}: {e}")
            return []
    
    def process_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Process all documents in a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List of all chunks from all documents
        """
        logger.info(f"Processing directory: {directory_path}")
        
        all_chunks = []
        directory = Path(directory_path)
        
        # Find all PDF and text files
        pdf_files = list(directory.glob("**/*.pdf"))
        txt_files = list(directory.glob("**/*.txt"))
        
        logger.info(f"Found {len(pdf_files)} PDF files and {len(txt_files)} text files")
        
        # Process PDFs
        for pdf_file in pdf_files:
            chunks = self.process_pdf(str(pdf_file))
            all_chunks.extend(chunks)
        
        # Process text files
        for txt_file in txt_files:
            chunks = self.process_text(str(txt_file))
            all_chunks.extend(chunks)
        
        logger.info(f"Total chunks extracted: {len(all_chunks)}")
        return all_chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Remove multiple spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters (keep basic punctuation)
        text = re.sub(r'[^\w\s.,!?;:()\-\'\"]+', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    def _split_text(self, text: str) -> List[str]:
        """
        Split text into chunks with overlap.
        
        Uses a simple word-based splitting strategy with overlap.
        """
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunks.append(' '.join(chunk_words))
            
            # Move start forward by (chunk_size - overlap)
            start += (self.chunk_size - self.chunk_overlap)
            
            # Break if we've processed all words
            if end >= len(words):
                break
        
        return chunks
    
    def get_document_stats(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get statistics about processed documents."""
        if not chunks:
            return {}
        
        sources = set(chunk["metadata"].get("source") for chunk in chunks)
        total_words = sum(len(chunk["content"].split()) for chunk in chunks)
        avg_chunk_size = total_words / len(chunks) if chunks else 0
        
        return {
            "total_chunks": len(chunks),
            "unique_sources": len(sources),
            "sources": list(sources),
            "total_words": total_words,
            "avg_chunk_size": avg_chunk_size
        }
