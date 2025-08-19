"""
Data models for document processing
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import time

@dataclass
class TextChunk:
    """Text chunk with metadata for processing"""
    chunk_id: str
    text: str
    chunk_index: int
    document_id: str
    url: str = ""
    title: str = ""
    similarity_score: float = 0.0
    processed_at: float = 0.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.processed_at == 0.0:
            self.processed_at = time.time()
