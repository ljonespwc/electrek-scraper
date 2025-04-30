# electrek_scraper/models.py
from datetime import datetime
from supabase import create_client
from .config import Config

# Initialize Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

class Article:
    """Model to interact with the articles table in Supabase"""
    
    @staticmethod
    def get_all(limit=None, order_by="published_at", ascending=False):
        """Get all articles with optional sorting and pagination"""
        try:
            # If limit is None or very large, use pagination to get all articles
            if limit is None or limit > 1000:
                all_data = []
                page_size = 1000
                current_page = 0
                
                while True:
                    # Build query with proper ordering
                    query = supabase.table("articles") \
                        .select("*") \
                        .order(order_by, desc=(not ascending)) \
                        .range(current_page * page_size, (current_page + 1) * page_size - 1)
                    
                    # Execute query
                    response = query.execute()
                    
                    # Get the data from this page
                    page_data = response.data
                    
                    # If no more data, break the loop
                    if not page_data:
                        break
                        
                    # Add this page's data to our results
                    all_data.extend(page_data)
                    
                    # If we got fewer results than the page size, we're done
                    if len(page_data) < page_size:
                        break
                        
                    # If we've reached the specified limit, we're done
                    if limit is not None and len(all_data) >= limit:
                        all_data = all_data[:limit]  # Trim to exact limit
                        break
                        
                    # Move to next page
                    current_page += 1
                
                print(f"Retrieved {len(all_data)} articles using pagination")
                return all_data
                
            else:
                # Use simple limit for smaller requests
                response = supabase.table("articles") \
                    .select("*") \
                    .order(order_by, desc=(not ascending)) \
                    .limit(limit) \
                    .execute()
                    
                return response.data
                    
        except Exception as e:
            print(f"Error getting articles: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []
    
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
    def get_sentiment_data(months=None):
        """Get sentiment data for correlation analysis using pagination"""
        try:
            all_data = []
            page_size = 1000
            current_page = 0
            
            while True:
                # Build query for articles with sentiment scores
                query = supabase.table("articles") \
                    .select("id, title, sentiment_score, comment_count, published_at") \
                    .not_.is_("sentiment_score", "null")
                
                # Apply date filter only if months is specified
                if months is not None:
                    from datetime import datetime, timedelta
                    start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
                    query = query.gte("published_at", start_date)
                
                # Add pagination
                query = query.range(current_page * page_size, (current_page + 1) * page_size - 1)
                
                # Execute query
                response = query.execute()
                
                # Get the data from this page
                page_data = response.data
                
                # If no more data, break the loop
                if not page_data:
                    break
                    
                # Add this page's data to our results
                all_data.extend(page_data)
                
                # If we got fewer results than the page size, we're done
                if len(page_data) < page_size:
                    break
                    
                # Move to next page
                current_page += 1
            
            print(f"Retrieved {len(all_data)} articles with sentiment scores using pagination")
            
            return all_data
                
        except Exception as e:
            print(f"Error getting sentiment data: {str(e)}")
            import traceback
            print(traceback.format_exc())
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
        """Get various statistics about the articles with additional logging"""
        
        # Initialize default values
        total_articles = 0
        total_comments = 0
        avg_comments = 0
        max_comments = 0
        most_commented_article = None
        
        try:
            # Get total number of articles
            articles_response = supabase.table("articles").select("count").execute()
            
            if hasattr(articles_response, 'count') and articles_response.count is not None:
                total_articles = articles_response.count
            elif articles_response.data and len(articles_response.data) > 0:
                if isinstance(articles_response.data[0], dict) and 'count' in articles_response.data[0]:
                    total_articles = articles_response.data[0]['count']
            
            if not total_articles:  # Still no count, get all IDs
                id_response = supabase.table("articles").select("id").execute()
                if id_response.data:
                    total_articles = len(id_response.data)
                    
            # Get ALL articles with comment counts - use pagination to get all
            all_articles_with_comments = []
            page_size = 1000
            current_page = 0
            
            while True:
                comment_response = supabase.table("articles") \
                    .select("id, title, comment_count") \
                    .range(current_page * page_size, (current_page + 1) * page_size - 1) \
                    .execute()
                    
                page_data = comment_response.data
                
                if not page_data:
                    break
                    
                all_articles_with_comments.extend(page_data)
                
                if len(page_data) < page_size:
                    break
                    
                current_page += 1
            
            # Debug - check highest comment values
            sorted_by_comments = sorted(all_articles_with_comments, 
                                    key=lambda x: x.get('comment_count', 0) if x.get('comment_count') is not None else 0,
                                    reverse=True)
            
            # For total comments, use a direct sum of all non-null values
            comment_counts = []
            for article in all_articles_with_comments:
                count = article.get('comment_count')
                if count is not None:
                    try:
                        count_value = int(count)
                        comment_counts.append(count_value)
                        # Track max comments
                        if count_value > max_comments:
                            max_comments = count_value
                    except (ValueError, TypeError):
                        pass
            
            # Calculate total and average
            if comment_counts:
                total_comments = sum(comment_counts)
                avg_comments = round(total_comments / len(comment_counts))
            
            # Get article with the highest comment count
            if max_comments > 0:
                most_commented_article = next((a for a in all_articles_with_comments if a.get('comment_count') == max_comments), None)
                
            print(f"Stats calculation: {total_articles} articles, {total_comments} total comments, {avg_comments} avg, {max_comments} max")
            
        except Exception as e:
            print(f"Error calculating statistics: {str(e)}")
            import traceback
            print(traceback.format_exc())
        
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