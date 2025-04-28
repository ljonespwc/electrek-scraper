# electrek_scraper/utils/sentiment_service.py
from .embedding_service import EmbeddingService
from .clustering import cosine_similarity

class SentimentService:
    def __init__(self, embedding_service=None):
        """Initialize with either a provided embedding service or create a new one"""
        self.embedding_service = embedding_service or EmbeddingService()
        
        # Pre-defined anchor texts for sentiment comparison - tuned for news headlines
        self.anchors = {
            'positive': [
                "Revolutionary breakthrough in electric vehicles",
                "Exciting new technology announced",
                "Major milestone achieved in sustainable energy",
                "Record breaking performance numbers",
                "Impressive sales figures announced"
            ],
            'negative': [
                "Major setback for electric vehicle adoption",
                "Disappointing performance numbers revealed",
                "Concerning safety issues discovered",
                "Falling short of expectations",
                "Severe production delays announced"
            ]
        }
        
        # Cache all embeddings
        self.anchor_embeddings = {
            'positive': [self.embedding_service.create_embedding(text) for text in self.anchors['positive']],
            'negative': [self.embedding_service.create_embedding(text) for text in self.anchors['negative']]
        }

    def calculate_sentiment(self, text, embedding=None):
        """Calculate sentiment score between -1 and 1"""
        if not text:
            return 0.0
            
        if embedding is None:
            embedding = self.embedding_service.create_embedding(text)
            if embedding is None:
                return 0.0
        
        # Calculate average similarity to positive and negative anchors
        pos_scores = [cosine_similarity(embedding, pos_emb) 
                    for pos_emb in self.anchor_embeddings['positive'] if pos_emb]
        neg_scores = [cosine_similarity(embedding, neg_emb) 
                    for neg_emb in self.anchor_embeddings['negative'] if neg_emb]
        
        if not pos_scores or not neg_scores:
            return 0.0
            
        avg_pos = sum(pos_scores) / len(pos_scores)
        avg_neg = sum(neg_scores) / len(neg_scores)
        
        # Scale the difference to ensure wider distribution
        sentiment = (avg_pos - avg_neg) * 2  # Multiply by 2 to spread the values
        
        # Clamp between -1 and 1
        return max(min(sentiment, 1.0), -1.0)

    def get_sentiment_category(self, score):
        """Convert numerical score to category"""
        if score is None:
            return 'neutral'
        if score >= 0.1:
            return 'positive'
        if score <= -0.1:
            return 'negative'
        return 'neutral'