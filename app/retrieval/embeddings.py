from typing import List   # ✅ Add this
from sentence_transformers import SentenceTransformer
import numpy as np
import pickle
import os

class EmbeddingGenerator:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.embeddings = None
        self.chunks = []
    
    def generate_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Generate embeddings for text chunks"""
        self.chunks = chunks
        print(f"🔄 Generating embeddings for {len(chunks)} chunks...")
        self.embeddings = self.model.encode(chunks, show_progress_bar=True, batch_size=32)
        print(f"✅ Embeddings generated with shape: {self.embeddings.shape}")
        return self.embeddings
    
    def save_embeddings(self, save_path: str):
        """Save embeddings and chunks"""
        if self.embeddings is not None:
            with open(save_path, 'wb') as f:
                pickle.dump({
                    'embeddings': self.embeddings,
                    'chunks': self.chunks
                }, f)
            print(f"💾 Saved embeddings to {save_path}")
