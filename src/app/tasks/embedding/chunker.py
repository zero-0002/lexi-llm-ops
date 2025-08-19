"""
Text chunking functionality
"""
import re
import uuid
from typing import List, Optional
from .models import TextChunk

class TextChunker:
    """Text chunking with overlap and size control"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, document_id: str = None, url: str = "", title: str = "") -> List[TextChunk]:
        """Chunk text into overlapping segments"""
        if not text or not text.strip():
            return []
        
        # Clean text
        text = self._clean_text(text)
        
        if len(text) <= self.chunk_size:
            # Single chunk
            chunk_id = str(uuid.uuid4())
            return [TextChunk(
                chunk_id=chunk_id,
                text=text,
                chunk_index=0,
                document_id=document_id or chunk_id,
                url=url,
                title=title
            )]
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                sentence_end = text.rfind('.', start + self.chunk_size // 2, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunk_id = str(uuid.uuid4())
                chunks.append(TextChunk(
                    chunk_id=chunk_id,
                    text=chunk_text,
                    chunk_index=chunk_index,
                    document_id=document_id or chunk_id,
                    url=url,
                    title=title
                ))
                chunk_index += 1
            
            # Move start forward, considering overlap
            start = max(start + 1, end - self.overlap)
            if start >= end:
                break
        
        return chunks
    
    def chunk_document(self, document: dict, task_logger=None) -> List[TextChunk]:
        """Chunk a document dict into TextChunk objects"""
        if not document:
            return []
        
        # Extract document fields
        doc_id = document.get('doc_id', str(uuid.uuid4()))
        text = document.get('text', '')
        url = document.get('url', '')
        title = document.get('title', '')
        
        if task_logger:
            task_logger.info(f"Chunking document {doc_id} with {len(text)} characters")
        
        # Use existing chunk_text method
        return self.chunk_text(text, document_id=doc_id, url=url, title=title)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters at start/end
        text = text.strip()
        return text
