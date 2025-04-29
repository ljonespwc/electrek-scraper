# electrek_scraper/utils/analyze_sentiments.py
from ..models import Article
from .sentiment_service import SentimentService
import time
import random

def analyze_all_articles(batch_size=25):
    """Analyze articles without sentiment scores in limited batches"""
    print(f"Starting sentiment analysis in batches of {batch_size}...")
    
    # Initialize sentiment service
    sentiment_service = SentimentService()
    
    # Get articles from Supabase
    from ..config import Config
    from supabase import create_client
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
    
    # Query articles without sentiment scores
    response = supabase.table("articles") \
        .select("id, title") \
        .is_("sentiment_score", "null") \
        .limit(batch_size) \
        .execute()
        
    articles = response.data
    print(f"Processing {len(articles)} out of potentially more articles without sentiment scores")
    
    # Process each article
    success_count = 0
    error_count = 0
    
    for i, article in enumerate(articles):
        try:
            article_id = article["id"]
            title = article["title"]
            
            # Skip if no title
            if not title:
                print(f"Article {article_id} has no title, skipping")
                continue
                
            # Calculate sentiment score
            print(f"[{i+1}/{len(articles)}] Analyzing: '{title}'")
            sentiment_score = sentiment_service.calculate_sentiment(title)
            
            # Update in database
            Article.update_sentiment_score(article_id, sentiment_score)
            
            # Get category for display
            category = sentiment_service.get_sentiment_category(sentiment_score)
            
            # Log result
            print(f"  Score: {sentiment_score:.2f} ({category})")
            success_count += 1
            
            # Add a random delay between requests (0.5-1.5 seconds)
            # This helps avoid rate limits and adds variability between requests
            time.sleep(random.uniform(0.5, 1.5))
            
        except Exception as e:
            print(f"Error processing article {article.get('id')}: {str(e)}")
            error_count += 1
    
    print(f"Sentiment analysis batch complete! Processed {success_count} articles successfully with {error_count} errors.")
    print(f"Run this process again to process more batches.")
    
    if success_count > 0:
        return True
    else:
        return False

if __name__ == "__main__":
    # This allows running the script directly
    analyze_all_articles()