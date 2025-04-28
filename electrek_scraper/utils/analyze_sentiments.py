# electrek_scraper/utils/analyze_sentiments.py
from ..models import Article
from .sentiment_service import SentimentService
from .embedding_service import EmbeddingService
import time

def analyze_all_articles():
    """Analyze all articles without sentiment scores"""
    print("Starting sentiment analysis for all articles...")
    
    # Counters for tracking
    successful_updates = 0
    failed_updates = 0
    
    try:
        # Initialize services
        embedding_service = EmbeddingService()
        sentiment_service = SentimentService(embedding_service)
        
        # Get articles from Supabase
        from ..config import Config
        from supabase import create_client
        supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        
        # Query articles without sentiment scores
        response = supabase.table("articles") \
            .select("id, title") \
            .is_("sentiment_score", "null") \
            .execute()
            
        articles = response.data
        print(f"Found {len(articles)} articles without sentiment scores")
        
        # Process each article
        for i, article in enumerate(articles):
            try:
                article_id = article["id"]
                title = article["title"]
                
                # Skip if no title
                if not title:
                    print(f"Article {article_id} has no title, skipping")
                    continue
                    
                # Calculate sentiment score
                sentiment_score = sentiment_service.calculate_sentiment(title)
                print(f"[{i+1}/{len(articles)}] Analyzed '{title}' - Score: {sentiment_score:.2f}")
                
                # Update the sentiment score
                result = Article.update_sentiment_score(article_id, sentiment_score)
                
                if result:
                    successful_updates += 1
                else:
                    failed_updates += 1
                    print(f"Failed to update article {article_id}")
                
            except Exception as e:
                failed_updates += 1
                print(f"Error processing article {article.get('id')}: {str(e)}")
                
        print(f"Sentiment analysis complete!")
        print(f"Successfully updated: {successful_updates}/{len(articles)}")
        print(f"Failed updates: {failed_updates}/{len(articles)}")
        
        return successful_updates > 0
        
    except Exception as e:
        print(f"Error in sentiment analysis batch process: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    # This allows running the script directly
    analyze_all_articles()