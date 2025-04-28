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
        order_direction = "asc" if ascending else "desc"
        
        response = supabase.table("articles") \
            .select("*") \
            .order(order_by, desc=(not ascending)) \
            .limit(limit) \
            .execute()
            
        return response.data
    
    @staticmethod
    def update_sentiment_score(article_id, sentiment_score):
        """Update the sentiment score for an article"""
        try:
            print(f"Updating article {article_id} with sentiment score {sentiment_score}")
            
            # Convert to proper types
            article_id = int(article_id)
            sentiment_score = float(sentiment_score)
            
            # Prepare update data
            update_data = {'sentiment_score': sentiment_score}
            
            # Perform the update
            response = supabase.table("articles") \
                .update(update_data) \
                .eq("id", article_id) \
                .execute()
                
            return response.data
            
        except Exception as e:
            print(f"Error updating sentiment score: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return None

    @staticmethod
    def get_sentiment_data(months=6):
        """Get sentiment and comment data for correlation analysis"""
        try:
            # Calculate the date range
            from datetime import datetime, timedelta
            start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
            
            # Get articles with both sentiment scores and comment counts
            response = supabase.table("articles") \
                .select("id, title, sentiment_score, comment_count, published_at") \
                .gte("published_at", start_date) \
                .not_.is_("sentiment_score", "null") \
                .execute()
                
            return response.data
        except Exception as e:
            print(f"Error getting sentiment data: {str(e)}")
            return []

    @staticmethod
    def update_sentiment_score_direct(article_id, sentiment_score):
        """Update the sentiment score using a direct SQL query"""
        try:
            # Create the SQL query
            sql = f"UPDATE articles SET sentiment_score = {sentiment_score} WHERE id = '{article_id}';"
            
            print(f"Attempting direct SQL update: {sql}")
            
            # Execute the SQL
            response = supabase.rpc('execute_sql', {'sql_query': sql}).execute()
            
            print(f"Direct SQL update response: {response}")
            return True
        except Exception as e:
            print(f"Error in direct SQL update: {str(e)}")
            return False
    
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
        simplified_data = {
            'title': article_data.get('title', ''),
            'url': article_data.get('url', ''),
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

    @staticmethod
    def get_statistics():
        """Get various statistics about the articles with robust None handling"""
        
        # Initialize default values
        total_articles = 0
        total_comments = 0
        avg_comments = 0
        max_comments = 0
        most_commented_article = None
        
        try:
            # Get total number of articles - with explicit fallback
            articles_response = supabase.table("articles").select("count").execute()
            
            # Try multiple methods to get count
            if hasattr(articles_response, 'count') and articles_response.count is not None:
                total_articles = articles_response.count
            else:
                # Fallback: check the count in the data field
                if articles_response.data and isinstance(articles_response.data, list) and len(articles_response.data) > 0:
                    if isinstance(articles_response.data[0], dict) and 'count' in articles_response.data[0]:
                        total_articles = articles_response.data[0]['count']
            
            # If we still don't have a count, get all IDs and count them
            if not total_articles:
                id_response = supabase.table("articles").select("id").execute()
                if id_response.data:
                    total_articles = len(id_response.data)
                    
            print(f"Total articles: {total_articles}")
            
            # Ensure total_articles is an integer
            total_articles = int(total_articles) if total_articles is not None else 0
            
            # Only proceed with calculations if we have articles
            if total_articles > 0:
                # Fetch all comment counts for calculations
                comment_response = supabase.table("articles").select("comment_count").execute()
                
                # Filter out None values and convert to int
                comment_counts = []
                for article in comment_response.data:
                    count = article.get('comment_count')
                    if count is not None:
                        try:
                            comment_counts.append(int(count))
                        except (ValueError, TypeError):
                            # Skip invalid values
                            pass
                
                # Only calculate if we have valid comment counts
                if comment_counts:
                    # Calculate total comments
                    total_comments = sum(comment_counts)
                    
                    # Calculate average comments
                    avg_comments = round(total_comments / len(comment_counts))
                    
                    # Find maximum comments
                    max_comments = max(comment_counts)
                    
                    # Get article with most comments
                    if max_comments > 0:
                        max_article_response = supabase.table("articles") \
                            .select("title, url, comment_count") \
                            .eq("comment_count", max_comments) \
                            .limit(1) \
                            .execute()
                        
                        most_commented_article = max_article_response.data[0] if max_article_response.data else None
        
        except Exception as e:
            # Log the error but continue with default values
            print(f"Error calculating statistics: {str(e)}")
        
        return {
            "total_articles": total_articles,
            "total_comments": total_comments,
            "avg_comments": avg_comments,
            "max_comments": max_comments,
            "most_commented_article": most_commented_article
        }

    @staticmethod
    def get_monthly_stats(months=6):
        """Get monthly comment trends and article counts without using a custom RPC function"""
        
        # Get all articles within the time period
        from datetime import datetime, timedelta
        
        # Calculate the start date
        start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
        
        # Fetch all articles in the time period
        response = supabase.table("articles") \
            .select("published_at, comment_count") \
            .gte("published_at", start_date) \
            .order("published_at") \
            .execute()
        
        articles = response.data
        
        if not articles:
            # Generate dummy data if no articles found
            import random
            
            data = []
            today = datetime.now()
            
            for i in range(months):
                month_date = today - timedelta(days=30 * (months - i - 1))
                month_str = month_date.strftime("%b %Y")
                
                data.append({
                    "month": month_str,
                    "avg_comments": random.randint(60, 120),
                    "article_count": random.randint(15, 35)
                })
                
            return data
        
        # Process the data to group by month
        from collections import defaultdict
        
        # Group by month
        monthly_data = defaultdict(lambda: {"count": 0, "total_comments": 0})
        
        for article in articles:
            # Extract the month
            date = datetime.fromisoformat(article["published_at"].replace('Z', '+00:00'))
            month_key = date.strftime("%Y-%m")  # Format as YYYY-MM for sorting
            month_display = date.strftime("%b %Y")  # Format as MMM YYYY for display
            
            # Accumulate data
            monthly_data[month_key]["month"] = month_display
            monthly_data[month_key]["count"] += 1
            monthly_data[month_key]["total_comments"] += article["comment_count"]
        
        # Calculate averages and format result
        result = []
        for month_key in sorted(monthly_data.keys()):
            data = monthly_data[month_key]
            result.append({
                "month": data["month"],
                "avg_comments": round(data["total_comments"] / data["count"]),
                "article_count": data["count"]
            })
        
        return result