# services/embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
import pickle
import os

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.embeddings: Dict[str, np.ndarray] = {}
        self.chunks: List[str] = []

    def generate_embeddings(self, chunks: List[str]):
        """Generate embeddings for text chunks"""
        self.chunks = chunks
        embeddings = self.model.encode(chunks)
        
        # Store chunks with their embeddings
        for i, chunk in enumerate(chunks):
            self.embeddings[chunk] = embeddings[i]
        
        # Save embeddings to disk
        self._save_embeddings()

    def search_similar_chunks(self, query: str, top_k: int = 3) -> List[str]:
        """Find most similar chunks to the query"""
        # Generate embedding for the query
        query_embedding = self.model.encode([query])[0]
        
        # Calculate similarities
        similarities = []
        for chunk, embedding in self.embeddings.items():
            similarity = self._calculate_similarity(query_embedding, embedding)
            similarities.append((chunk, similarity))
        
        # Sort by similarity and get top k chunks
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in similarities[:top_k]]

    def _calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))

    def _save_embeddings(self):
        """Save embeddings to disk"""
        with open('embeddings.pkl', 'wb') as f:
            pickle.dump((self.embeddings, self.chunks), f)

    def _load_embeddings(self):
        """Load embeddings from disk"""
        if os.path.exists('embeddings.pkl'):
            with open('embeddings.pkl', 'rb') as f:
                self.embeddings, self.chunks = pickle.load(f)