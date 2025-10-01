import faiss
import numpy as np
from rank_bm25 import BM25Okapi
import re
from typing import List, Tuple, Dict
import hashlib
import json
import redis

class FAISSRetriever:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.index = None
        self.chunks = []
        self.bm25_index = None
        # Initialize cache
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    def build_index(self, embeddings: np.ndarray, chunks: List[str]):
        """Build FAISS index"""
        self.chunks = chunks
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)
        
        # Build BM25 index for re-ranking
        tokenized_chunks = [self._tokenize(chunk) for chunk in chunks]
        self.bm25_index = BM25Okapi(tokenized_chunks)
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization for BM25"""
        return re.findall(r'\w+', text.lower())
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        return hashlib.md5(query.encode()).hexdigest()
    
    def search(self, query: str, k: int = 5, rerank: bool = True) -> List[Tuple[str, float]]:
        """Search with caching and optional re-ranking"""
        
        # Check cache first
        cache_key = self._get_cache_key(query)
        cached_result = self.redis_client.get(cache_key)
        if cached_result:
            return json.loads(cached_result)
        
        # FAISS search
        query_embedding = self.model.encode([query])
        faiss.normalize_L2(query_embedding)
        distances, indices = self.index.search(query_embedding, k*2)  # Get more for re-ranking
        
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(distance)))
        
        # Re-rank with BM25
        if rerank and self.bm25_index:
            reranked_results = self._rerank_with_bm25(query, results)
            results = reranked_results[:k]
        else:
            results = results[:k]
        
        # Cache the results
        self.redis_client.setex(cache_key, 3600, json.dumps(results))  # Cache for 1 hour
        return results
    
    def _rerank_with_bm25(self, query: str, initial_results: List[Tuple[str, float]]) -> List[Tuple[str, float]]:
        """Re-rank results using BM25"""
        bm25_scores = self.bm25_index.get_scores(self._tokenize(query))
        
        combined_results = []
        for chunk, faiss_score in initial_results:
            chunk_idx = self.chunks.index(chunk)
            bm25_score = bm25_scores[chunk_idx] if chunk_idx < len(bm25_scores) else 0
            
            # Combine scores (you can adjust weights)
            combined_score = 0.7 * faiss_score + 0.3 * (bm25_score / 10)  # Normalize BM25 score
            combined_results.append((chunk, combined_score))
        
        # Sort by combined score
        combined_results.sort(key=lambda x: x[1], reverse=True)
        return combined_results