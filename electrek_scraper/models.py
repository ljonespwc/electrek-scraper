# electrek_scraper/models.py
from datetime import datetime
from supabase import create_client
from .config import Config

# Initialize Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

class Article:
    """Model to interact with the articles table in Supabase"""
    
    @staticmethod
    def get_all(limit=20, order_by="published_at", ascending=False):
        """Get all articles with optional sorting and limit"""
        # Fixed order syntax for Supabase Python client
        # Format: column(ascending or descending)
        order_direction = "asc" if ascending else "desc"
        
        response = supabase.table("articles") \
            .select("*") \
            .order(order_by, desc=(not ascending)) \
            .limit(limit) \
            .execute()
            
        return response.data
    
    @staticmethod
    def get_by_id(article_id):
        """Get a single article by ID"""
        response = supabase.table("articles") \
            .select("*") \
            .eq("id", article_id) \
            .single() \
            .execute()
            
        return response.data
    
    @staticmethod
    def create(article_data):
        """Insert a new article with simplified fields"""
        # Only store the metadata fields we care about
        simplified_data = {
            'title': article_data.get('title', ''),
            'url': article_data.get('url', ''),  # Keep for uniqueness check
            'author': article_data.get('author', ''),
            'published_at': article_data.get('published_at'),
            'comment_count': article_data.get('comment_count', 0)
        }
        
        # Handle date formatting
        if 'published_at' in simplified_data and isinstance(simplified_data['published_at'], datetime):
            simplified_data['published_at'] = simplified_data['published_at'].isoformat()
        
        print(f"Inserting simplified data: {simplified_data}")
        
        try:
            response = supabase.table("articles") \
                .insert(simplified_data) \
                .execute()
            return response.data
        except Exception as e:
            print(f"Database insert error: {str(e)}")
            raise
    
    @staticmethod
    def url_exists(url):
        """Check if article with URL already exists"""
        response = supabase.table("articles") \
            .select("id") \
            .eq("url", url) \
            .execute()
            
        return len(response.data) > 0