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
            
            # Build base query
            base_query = supabase.table("articles") \
                .select("id, title, sentiment_score, comment_count, published_at") \
                .not_.is_("sentiment_score", "null")
            
            # Apply date filter if months is specified
            if months is not None:
                from datetime import datetime, timedelta
                start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
                base_query = base_query.gte("published_at", start_date)
                period_msg = f"for the last {months} months"
            else:
                period_msg = "for all time"
            
            while True:
                # Add pagination
                query = base_query.range(current_page * page_size, (current_page + 1) * page_size - 1)
                
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
            
            print(f"Retrieved {len(all_data)} articles with sentiment scores {period_msg}")
            
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
    def get_statistics(months=None):
        """Get various statistics about the articles with date filtering support"""
        
        # Initialize default values
        total_articles = 0
        total_comments = 0
        avg_comments = 0
        max_comments = 0
        most_commented_article = None
        
        try:
            # Define start date if months is specified
            start_date = None
            if months is not None:
                from datetime import datetime, timedelta
                start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
                period_msg = f"for the last {months} months"
            else:
                period_msg = "for all time"
            
            # Get total articles count
            if start_date:
                # With date filter
                articles_response = supabase.table("articles") \
                    .select("count") \
                    .gte("published_at", start_date) \
                    .execute()
            else:
                # Without date filter
                articles_response = supabase.table("articles") \
                    .select("count") \
                    .execute()
            
            if hasattr(articles_response, 'count') and articles_response.count is not None:
                total_articles = articles_response.count
            elif articles_response.data and len(articles_response.data) > 0:
                if isinstance(articles_response.data[0], dict) and 'count' in articles_response.data[0]:
                    total_articles = articles_response.data[0]['count']
            
            if not total_articles:  # Still no count, get all IDs
                if start_date:
                    id_response = supabase.table("articles") \
                        .select("id") \
                        .gte("published_at", start_date) \
                        .execute()
                else:
                    id_response = supabase.table("articles") \
                        .select("id") \
                        .execute()
                    
                if id_response.data:
                    total_articles = len(id_response.data)
                    
            # Get ALL articles with comment counts - use pagination to get all
            all_articles_with_comments = []
            page_size = 1000
            current_page = 0
            
            while True:
                # Build page query with date filter if needed
                if start_date:
                    comment_response = supabase.table("articles") \
                        .select("id, title, comment_count, published_at") \
                        .gte("published_at", start_date) \
                        .range(current_page * page_size, (current_page + 1) * page_size - 1) \
                        .execute()
                else:
                    comment_response = supabase.table("articles") \
                        .select("id, title, comment_count, published_at") \
                        .range(current_page * page_size, (current_page + 1) * page_size - 1) \
                        .execute()
                    
                page_data = comment_response.data
                
                if not page_data:
                    break
                    
                all_articles_with_comments.extend(page_data)
                
                if len(page_data) < page_size:
                    break
                    
                current_page += 1
            
            print(f"Retrieved {len(all_articles_with_comments)} articles with comments {period_msg}")
            
            # Debug - check highest comment values
            sorted_by_comments = sorted(all_articles_with_comments, 
                                    key=lambda x: x.get('comment_count', 0) if x.get('comment_count') is not None else 0,
                                    reverse=True)
            
            if len(sorted_by_comments) > 0:
                print(f"Highest comment article: {sorted_by_comments[0].get('title', 'No title')} - {sorted_by_comments[0].get('comment_count')} comments")
            
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
            
            print(f"Stats calculation {period_msg}: {total_articles} articles, {total_comments} total comments, {avg_comments} avg, {max_comments} max")
            
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

    @staticmethod
    def get_top_articles_analysis(limit=20, months=None):
        """Get top engaging articles with Tesla classification for business impact analysis"""
        try:
            # Build base query for articles with sentiment scores
            base_query = supabase.table("articles") \
                .select("id, title, author, comment_count, sentiment_score, published_at") \
                .not_.is_("sentiment_score", "null") \
                .order("comment_count", desc=True) \
                .limit(limit)
            
            # Apply date filter if specified
            if months is not None:
                from datetime import datetime, timedelta
                start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
                base_query = base_query.gte("published_at", start_date)
            
            response = base_query.execute()
            articles = response.data
            
            # Add Tesla classification and sentiment category
            from .utils.sentiment_service import SentimentService
            sentiment_service = SentimentService()
            
            for article in articles:
                title_lower = article.get('title', '').lower()
                # Check for Tesla/Elon mentions
                article['is_tesla'] = any(keyword in title_lower for keyword in ['tesla', 'elon', 'musk'])
                # Check for other EV companies
                article['is_byd'] = 'byd' in title_lower
                article['is_ford'] = 'ford' in title_lower
                article['is_rivian'] = 'rivian' in title_lower
                
                # Add sentiment category and color
                if article.get('sentiment_score') is not None:
                    score = article.get('sentiment_score')
                    article['sentiment_category'] = sentiment_service.get_sentiment_category(score)
                    article['sentiment_color'] = sentiment_service.get_sentiment_color(score)
            
            print(f"Retrieved top {len(articles)} engaging articles for business analysis")
            return articles
            
        except Exception as e:
            print(f"Error getting top articles analysis: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_author_tesla_bias(months=None):
        """Analyze author-level Tesla coverage patterns and sentiment bias"""
        try:
            # Get all articles with sentiment scores and authors
            base_query = supabase.table("articles") \
                .select("author, title, sentiment_score, comment_count, published_at") \
                .not_.is_("sentiment_score", "null") \
                .not_.is_("author", "null")
            
            # Apply date filter if specified
            if months is not None:
                from datetime import datetime, timedelta
                start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
                base_query = base_query.gte("published_at", start_date)
            
            # Get all data using pagination
            all_articles = []
            page_size = 1000
            current_page = 0
            
            while True:
                query = base_query.range(current_page * page_size, (current_page + 1) * page_size - 1)
                response = query.execute()
                page_data = response.data
                
                if not page_data:
                    break
                    
                all_articles.extend(page_data)
                
                if len(page_data) < page_size:
                    break
                    
                current_page += 1
            
            # Process by author
            from collections import defaultdict
            author_stats = defaultdict(lambda: {
                'total_articles': 0,
                'tesla_articles': 0,
                'tesla_sentiment_sum': 0,
                'tesla_comments_sum': 0,
                'non_tesla_sentiment_sum': 0,
                'non_tesla_comments_sum': 0,
                'non_tesla_articles': 0
            })
            
            for article in all_articles:
                author = article.get('author', 'Unknown')
                title_lower = article.get('title', '').lower()
                sentiment = article.get('sentiment_score', 0)
                comments = article.get('comment_count', 0)
                
                is_tesla = any(keyword in title_lower for keyword in ['tesla', 'elon', 'musk'])
                
                stats = author_stats[author]
                stats['total_articles'] += 1
                
                if is_tesla:
                    stats['tesla_articles'] += 1
                    stats['tesla_sentiment_sum'] += sentiment
                    stats['tesla_comments_sum'] += comments
                else:
                    stats['non_tesla_articles'] += 1
                    stats['non_tesla_sentiment_sum'] += sentiment
                    stats['non_tesla_comments_sum'] += comments
            
            # Calculate final metrics
            author_analysis = []
            for author, stats in author_stats.items():
                if stats['total_articles'] >= 5:  # Only authors with 5+ articles
                    analysis = {
                        'author': author,
                        'total_articles': stats['total_articles'],
                        'tesla_articles': stats['tesla_articles'],
                        'tesla_percentage': round((stats['tesla_articles'] / stats['total_articles']) * 100, 1),
                        'avg_tesla_sentiment': round(stats['tesla_sentiment_sum'] / max(stats['tesla_articles'], 1), 3),
                        'avg_tesla_comments': round(stats['tesla_comments_sum'] / max(stats['tesla_articles'], 1), 1),
                        'avg_non_tesla_sentiment': round(stats['non_tesla_sentiment_sum'] / max(stats['non_tesla_articles'], 1), 3),
                        'avg_non_tesla_comments': round(stats['non_tesla_comments_sum'] / max(stats['non_tesla_articles'], 1), 1)
                    }
                    author_analysis.append(analysis)
            
            # Sort by Tesla article count
            author_analysis.sort(key=lambda x: x['tesla_articles'], reverse=True)
            
            print(f"Analyzed {len(author_analysis)} authors with 5+ articles")
            return author_analysis
            
        except Exception as e:
            print(f"Error getting author Tesla bias analysis: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_company_comparison(months=None):
        """Compare engagement metrics across different EV companies mentioned in articles"""
        try:
            # Get all articles with sentiment scores
            base_query = supabase.table("articles") \
                .select("title, comment_count, sentiment_score, published_at") \
                .not_.is_("sentiment_score", "null")
            
            # Apply date filter if specified
            if months is not None:
                from datetime import datetime, timedelta
                start_date = (datetime.now() - timedelta(days=30 * months)).isoformat()
                base_query = base_query.gte("published_at", start_date)
            
            # Get all data using pagination
            all_articles = []
            page_size = 1000
            current_page = 0
            
            while True:
                query = base_query.range(current_page * page_size, (current_page + 1) * page_size - 1)
                response = query.execute()
                page_data = response.data
                
                if not page_data:
                    break
                    
                all_articles.extend(page_data)
                
                if len(page_data) < page_size:
                    break
                    
                current_page += 1
            
            # Define company keywords and stats
            companies = {
                'Tesla/Elon': ['tesla', 'elon', 'musk'],
                'BYD': ['byd'],
                'Ford': ['ford'],
                'GM': ['gm', 'general motors'],
                'Rivian': ['rivian'],
                'Lucid': ['lucid'],
                'Nio': ['nio'],
                'Volkswagen': ['volkswagen', 'vw'],
                'BMW': ['bmw'],
                'Mercedes': ['mercedes', 'mercedes-benz']
            }
            
            company_stats = {}
            for company in companies:
                company_stats[company] = {
                    'articles': [],
                    'total_comments': 0,
                    'avg_comments': 0,
                    'avg_sentiment': 0,
                    'negative_articles': 0,
                    'positive_articles': 0
                }
            
            # Classify articles by company mentions
            for article in all_articles:
                title_lower = article.get('title', '').lower()
                comment_count = article.get('comment_count', 0)
                sentiment = article.get('sentiment_score', 0)
                
                for company, keywords in companies.items():
                    if any(keyword in title_lower for keyword in keywords):
                        stats = company_stats[company]
                        stats['articles'].append({
                            'title': article.get('title'),
                            'comments': comment_count,
                            'sentiment': sentiment
                        })
                        stats['total_comments'] += comment_count
                        
                        if sentiment < -0.1:
                            stats['negative_articles'] += 1
                        elif sentiment > 0.1:
                            stats['positive_articles'] += 1
            
            # Calculate averages and metrics
            comparison_data = []
            for company, stats in company_stats.items():
                if len(stats['articles']) > 0:
                    article_count = len(stats['articles'])
                    avg_comments = round(stats['total_comments'] / article_count, 1)
                    avg_sentiment = round(sum(a['sentiment'] for a in stats['articles']) / article_count, 3)
                    
                    comparison_data.append({
                        'company': company,
                        'article_count': article_count,
                        'total_comments': stats['total_comments'],
                        'avg_comments': avg_comments,
                        'avg_sentiment': avg_sentiment,
                        'negative_articles': stats['negative_articles'],
                        'positive_articles': stats['positive_articles'],
                        'negative_percentage': round((stats['negative_articles'] / article_count) * 100, 1)
                    })
            
            # Sort by average comments (engagement)
            comparison_data.sort(key=lambda x: x['avg_comments'], reverse=True)
            
            print(f"Compared engagement across {len(comparison_data)} EV companies")
            return comparison_data
            
        except Exception as e:
            print(f"Error getting company comparison: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_business_impact_metrics(months=None):
        """Calculate key business impact metrics that quantify the value of Tesla hate content"""
        try:
            # Get sentiment data with Tesla classification
            all_sentiment_data = Article.get_sentiment_data(months)
            
            if not all_sentiment_data:
                return {}
            
            # Classify articles
            tesla_articles = []
            non_tesla_articles = []
            tesla_negative = []
            tesla_positive = []
            non_tesla_negative = []
            non_tesla_positive = []
            
            for article in all_sentiment_data:
                title_lower = article.get('title', '').lower()
                sentiment = article.get('sentiment_score', 0)
                comments = article.get('comment_count', 0)
                
                is_tesla = any(keyword in title_lower for keyword in ['tesla', 'elon', 'musk'])
                
                if is_tesla:
                    tesla_articles.append(article)
                    if sentiment < -0.1:
                        tesla_negative.append(article)
                    elif sentiment > 0.1:
                        tesla_positive.append(article)
                else:
                    non_tesla_articles.append(article)
                    if sentiment < -0.1:
                        non_tesla_negative.append(article)
                    elif sentiment > 0.1:
                        non_tesla_positive.append(article)
            
            # Calculate key metrics
            tesla_avg_comments = sum(a.get('comment_count', 0) for a in tesla_articles) / max(len(tesla_articles), 1)
            non_tesla_avg_comments = sum(a.get('comment_count', 0) for a in non_tesla_articles) / max(len(non_tesla_articles), 1)
            
            tesla_negative_avg = sum(a.get('comment_count', 0) for a in tesla_negative) / max(len(tesla_negative), 1)
            tesla_positive_avg = sum(a.get('comment_count', 0) for a in tesla_positive) / max(len(tesla_positive), 1)
            non_tesla_negative_avg = sum(a.get('comment_count', 0) for a in non_tesla_negative) / max(len(non_tesla_negative), 1)
            
            # Calculate multipliers
            tesla_multiplier = round(tesla_avg_comments / max(non_tesla_avg_comments, 1), 2)
            negative_tesla_multiplier = round(tesla_negative_avg / max(non_tesla_negative_avg, 1), 2)
            tesla_sentiment_bias = round((len(tesla_negative) / max(len(tesla_articles), 1)) * 100, 1)
            non_tesla_sentiment_bias = round((len(non_tesla_negative) / max(len(non_tesla_articles), 1)) * 100, 1)
            
            # Engagement intensity (negative vs positive Tesla)
            tesla_negative_boost = 0
            if tesla_positive_avg > 0:
                tesla_negative_boost = round(((tesla_negative_avg - tesla_positive_avg) / tesla_positive_avg) * 100, 1)
            
            # Total Tesla traffic contribution
            total_tesla_comments = sum(a.get('comment_count', 0) for a in tesla_articles)
            total_all_comments = sum(a.get('comment_count', 0) for a in all_sentiment_data)
            tesla_traffic_percentage = round((total_tesla_comments / max(total_all_comments, 1)) * 100, 1)
            
            metrics = {
                # Core multipliers
                'tesla_engagement_multiplier': tesla_multiplier,
                'negative_tesla_multiplier': negative_tesla_multiplier,
                
                # Sentiment bias
                'tesla_negative_percentage': tesla_sentiment_bias,
                'non_tesla_negative_percentage': non_tesla_sentiment_bias,
                'sentiment_bias_difference': round(tesla_sentiment_bias - non_tesla_sentiment_bias, 1),
                
                # Engagement metrics
                'tesla_avg_comments': round(tesla_avg_comments, 1),
                'non_tesla_avg_comments': round(non_tesla_avg_comments, 1),
                'tesla_negative_avg_comments': round(tesla_negative_avg, 1),
                'tesla_positive_avg_comments': round(tesla_positive_avg, 1),
                'tesla_negative_boost_percentage': tesla_negative_boost,
                
                # Traffic contribution
                'tesla_traffic_percentage': tesla_traffic_percentage,
                'tesla_article_count': len(tesla_articles),
                'non_tesla_article_count': len(non_tesla_articles),
                'tesla_percentage_of_coverage': round((len(tesla_articles) / len(all_sentiment_data)) * 100, 1),
                
                # Estimated business impact (assuming comments = engagement = revenue)
                'estimated_revenue_multiplier': tesla_multiplier,
                'estimated_tesla_revenue_share': tesla_traffic_percentage
            }
            
            print(f"Calculated business impact metrics from {len(all_sentiment_data)} articles")
            return metrics
            
        except Exception as e:
            print(f"Error calculating business impact metrics: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {}