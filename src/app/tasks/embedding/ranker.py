"""
Chunk ranking and relevance scoring
"""
import math
from typing import List, Dict, Any
from .models import TextChunk

class ChunkRanker:
    """Rank and score text chunks for relevance"""
    
    def __init__(self, query: str = ""):
        self.query = query.lower() if query else ""
        self.query_terms = set(self.query.split()) if self.query else set()
    
    def rank_chunks(self, chunks: List[TextChunk], query: str = None, limit: int = 10, task_logger=None) -> List[TextChunk]:
        """Rank chunks by relevance to query"""
        if not chunks:
            return []
        
        # Update query if provided
        if query:
            self.query = query.lower()
            self.query_terms = set(self.query.split())
        
        if not self.query_terms:
            # No query, return first N chunks
            return chunks[:limit]
        
        # Score each chunk
        scored_chunks = []
        for chunk in chunks:
            score = self._calculate_relevance_score(chunk.text)
            chunk.similarity_score = score
            scored_chunks.append(chunk)
        
        # Sort by score (descending) and return top N
        scored_chunks.sort(key=lambda x: x.similarity_score, reverse=True)
        return scored_chunks[:limit]
    
    def _calculate_relevance_score(self, text: str) -> float:
        """Calculate simple TF-based relevance score"""
        if not self.query_terms or not text:
            return 0.0
        
        text_lower = text.lower()
        text_terms = text_lower.split()
        
        if not text_terms:
            return 0.0
        
        # Count query term frequencies
        term_scores = []
        for query_term in self.query_terms:
            # Term frequency in chunk
            tf = text_terms.count(query_term)
            if tf > 0:
                # Simple TF-IDF approximation
                tf_score = 1 + math.log(tf)
                term_scores.append(tf_score)
        
        if not term_scores:
            return 0.0
        
        # Average score across matching terms
        avg_score = sum(term_scores) / len(self.query_terms)
        
        # Boost if multiple query terms found
        matching_terms = len(term_scores)
        coverage_bonus = matching_terms / len(self.query_terms)
        
        return avg_score * (1 + coverage_bonus)
    
    def filter_by_threshold(self, chunks: List[TextChunk], threshold: float = 0.05, task_logger=None) -> List[TextChunk]:
        """Filter chunks by minimum relevance threshold"""
        if not chunks:
            return []
        
        filtered = [chunk for chunk in chunks if chunk.similarity_score >= threshold]
        
        if task_logger:
            task_logger.info(f"Filtered {len(chunks)} chunks to {len(filtered)} above threshold {threshold}")
        
        return filtered
