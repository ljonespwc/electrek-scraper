# electrek_scraper/utils/embedding_service.py
import numpy as np
import requests
from .proxy_manager import ProxyManager
import os
import json

class EmbeddingService:
    def __init__(self, use_proxy=False):
        """Initialize the embedding service with proxy support"""
        self.proxy_manager = ProxyManager() if use_proxy else None
        
        # Use OpenAI API for embeddings (requires API key)
        self.openai_api_key = os.environ.get('OPENAI_API_KEY')
        self.embedding_model = "text-embedding-3-large"
        
        # If no OpenAI API key, use a simplified embedding method
        self.use_openai = self.openai_api_key is not None
        
    def create_embedding(self, text):
        """Create an embedding vector for the given text"""
        if not text:
            return None
            
        if self.use_openai:
            return self._create_openai_embedding(text)
        else:
            return self._create_simple_embedding(text)
            
    def _create_openai_embedding(self, text):
        """Create an embedding using OpenAI API"""
        if not self.openai_api_key:
            return None
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        data = {
            "input": text[:8000],  # OpenAI has token limits
            "model": self.embedding_model
        }
        
        try:
            if self.proxy_manager:
                response = self.proxy_manager.make_request(
                    "https://api.openai.com/v1/embeddings",
                    method="POST",
                    headers=headers,
                    json=data
                )
            else:
                response = requests.post(
                    "https://api.openai.com/v1/embeddings",
                    headers=headers,
                    json=data
                )
                
            if response and response.status_code == 200:
                result = response.json()
                embedding = result["data"][0]["embedding"]
                return embedding
            else:
                print(f"Error creating OpenAI embedding: {response.text if response else 'No response'}")
                return None
        except Exception as e:
            print(f"Exception in OpenAI embedding: {str(e)}")
            return None
            
    def _create_simple_embedding(self, text):
        """Create a simplified embedding for testing purposes"""
        # This is a very simplified embedding approach
        # In production, use a proper embedding model or API
        words = text.lower().split()
        # Create a basic frequency vector (very simplified)
        embedding = np.zeros(100)
        
        for i, word in enumerate(words):
            if i < 100:
                # Very basic: just put word positions into the vector
                embedding[i] = hash(word) % 100 / 100
                
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding.tolist()