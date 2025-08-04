"""
Public-facing routes for articles and authentication
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, make_response
from supabase import create_client
from .config import Config
from .models import Article
from .auth import clear_auth_session, get_user_info
import numpy as np
from datetime import datetime

bp = Blueprint('public', __name__)
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

@bp.route('/')
def index():
    """Public landing page with article listings"""
    from .utils.reading_time import ReadingTimeEstimator
    from flask import current_app
    import os
    
    # Calculate reading time for articles
    reading_estimator = ReadingTimeEstimator()
    
    # Define articles with their template paths
    articles = [
        {
            'title': 'The Business of Hate: Anti-Tesla Blog by the Numbers',
            'description': 'How one Tesla superfan transformed into Tesla\'s harshest critic and built a business model around manufactured outrage.',
            'url': 'public.fred_lambert_sellout',
            'template_path': 'articles/fred_lambert_sellout.html',
            'category': 'Lance Jones'
        }
    ]
    
    # Add reading times and engagement data from database
    for article in articles:
        # Extract article slug from URL
        article_slug = article['url'].split('.')[-1]  # e.g., 'public.fred_lambert_sellout' -> 'fred_lambert_sellout'
        article_slug = article_slug.replace('_', '-')  # Convert to kebab-case for database
        
        # Get article metadata (reading time, word count)
        metadata = Article.get_article_metadata(article_slug)
        if metadata:
            reading_minutes = metadata['reading_time_minutes']
            article['reading_time'] = f"{reading_minutes} min read" if reading_minutes != 1 else "1 min read"
        else:
            # Fallback to calculation if not in database
            template_path = os.path.join(current_app.root_path, 'templates', article['template_path'])
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    article_content = f.read()
                article['reading_time'] = reading_estimator.format_reading_time(article_content)
            except:
                article['reading_time'] = "10 min read"  # Fallback
        
        # Get engagement data (sparkles)
        engagement = Article.get_article_engagement(article_slug)
        sparkle_count = engagement.get('sparkle', 0)
        article['sparkle_count'] = sparkle_count
        article['show_sparkles'] = sparkle_count > 50
    
    response = make_response(render_template('landing_clean.html', articles=articles))
    
    # Cache landing page for 6 hours on Vercel's CDN
    response.headers['Cache-Control'] = 'public, max-age=21600'
    return response


@bp.route('/articles/fred-lambert-sellout')
def fred_lambert_sellout():
    """Tesla Hate Machine Sharp article - public access"""
    from .utils.cache_service import ChartDataCache
    
    # Use ALL available data for maximum impact
    months = None  # None = all time data
    cache = ChartDataCache(ttl_days=30)  # Cache for 1 month
    
    # Try to get all chart data from cache
    chart_data = cache.get('tesla_article_complete', months)
    
    if chart_data is None:
        # Generate fresh data and cache it
        filtered_stats = Article.get_statistics(months)
        all_sentiment_data = Article.get_sentiment_data(months)
        top_articles = Article.get_top_articles_analysis(25, months)
        author_analysis = Article.get_author_tesla_bias(months)
        company_comparison = Article.get_company_comparison(months)
        business_metrics = Article.get_business_impact_metrics(months)
        
        # Bundle all data for caching
        chart_data = {
            'filtered_stats': filtered_stats,
            'all_sentiment_data': all_sentiment_data,
            'top_articles': top_articles,
            'author_analysis': author_analysis,
            'company_comparison': company_comparison,
            'business_metrics': business_metrics
        }
        
        # Cache the complete dataset
        cache.set('tesla_article_complete', chart_data, months)
    
    # Extract data from cache
    filtered_stats = chart_data['filtered_stats']
    all_sentiment_data = chart_data['all_sentiment_data']
    top_articles = chart_data['top_articles']
    author_analysis = chart_data['author_analysis']
    company_comparison = chart_data['company_comparison']
    business_metrics = chart_data['business_metrics']
    
    # Get sentiment service for categorization
    from .utils.sentiment_service import SentimentService
    sentiment_service = SentimentService()
    
    # Process sentiment data for correlation analysis
    scatter_data = []
    for article in all_sentiment_data:
        if article.get('sentiment_score') is not None and article.get('comment_count') is not None:
            sentiment_category = sentiment_service.get_sentiment_category(article.get('sentiment_score'))
            scatter_data.append({
                'id': article.get('id'),
                'title': article.get('title', 'Untitled'),
                'sentiment_score': article.get('sentiment_score'),
                'comment_count': article.get('comment_count'),
                'published_at': article.get('published_at'),
                'sentiment_category': sentiment_category
            })
    
    # Calculate correlation
    correlation = None
    if len(scatter_data) >= 5:
        try:
            sentiment_scores = [article['sentiment_score'] for article in scatter_data]
            comment_counts = [article['comment_count'] for article in scatter_data]
            correlation = np.corrcoef(sentiment_scores, comment_counts)[0, 1]
        except Exception as e:
            print(f"Error calculating correlation: {str(e)}")
    
    # Get reading time and engagement data from database
    article_slug = 'fred-lambert-sellout'
    
    # Get article metadata (reading time)
    metadata = Article.get_article_metadata(article_slug)
    if metadata:
        reading_minutes = metadata['reading_time_minutes']
        reading_time = f"{reading_minutes} min read" if reading_minutes != 1 else "1 min read"
    else:
        # Fallback to calculation if not in database
        from .utils.reading_time import ReadingTimeEstimator
        reading_estimator = ReadingTimeEstimator()
        from flask import current_app
        import os
        
        template_path = os.path.join(current_app.root_path, 'templates', 'articles', 'fred_lambert_sellout.html')
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                article_content = f.read()
            reading_time = reading_estimator.format_reading_time(article_content)
        except:
            reading_time = "10 min read"  # Fallback
    
    # Get engagement data (sparkles)
    engagement = Article.get_article_engagement(article_slug)
    sparkle_count = engagement.get('sparkle', 0)
    show_sparkles = sparkle_count > 50
    
    response = make_response(render_template('articles/fred_lambert_sellout.html',
                                           stats=filtered_stats,
                                           sentiment_data=scatter_data,
                                           correlation=correlation,
                                           top_articles=top_articles,
                                           author_analysis=author_analysis,
                                           company_comparison=company_comparison,
                                           business_metrics=business_metrics,
                                           reading_time=reading_time,
                                           sparkle_count=sparkle_count,
                                           show_sparkles=show_sparkles,
                                           article_slug=article_slug,
                                           months=months))
    
    # Cache for 30 days on Vercel's CDN
    response.headers['Cache-Control'] = 'public, max-age=2592000'
    return response

@bp.route('/login')
def login():
    """Google OAuth login page"""
    return render_template('auth/login_standalone.html')

@bp.route('/auth/google')
def google_auth():
    """Initiate Google OAuth flow"""
    try:
        # Get the redirect URL from Supabase
        # Build the proper redirect URL using the current request's host
        redirect_url = f"{request.scheme}://{request.host}/auth/callback"
        
        auth_response = supabase.auth.sign_in_with_oauth({
            "provider": "google",
            "options": {
                "redirect_to": redirect_url
            }
        })
        
        if auth_response.url:
            return redirect(auth_response.url)
        else:
            flash('Error initiating Google login', 'error')
            return redirect(url_for('public.login'))
            
    except Exception as e:
        print(f"Google auth error: {e}")
        flash('Error with Google authentication', 'error')
        return redirect(url_for('public.login'))

@bp.route('/auth/callback')
def auth_callback():
    """Handle OAuth callback from Supabase"""
    try:
        # Check if we got an authorization code (PKCE flow)
        code = request.args.get('code')
        
        if code:
            # Exchange the code for a session using Supabase
            auth_response = supabase.auth.exchange_code_for_session({
                "auth_code": code
            })
            
            if auth_response.session:
                # Store session data
                session['access_token'] = auth_response.session.access_token
                session['refresh_token'] = auth_response.session.refresh_token
                
                # Get user info and check admin status
                user_info = get_user_info()
                
                if user_info:
                    session['user_email'] = user_info.get('email')
                    flash('Successfully logged in!', 'success')
                    return redirect(url_for('admin.index'))
                else:
                    flash('Failed to get user information', 'error')
                    return redirect(url_for('public.login'))
            else:
                flash('Failed to create session', 'error')
                return redirect(url_for('public.login'))
        else:
            # No code parameter, try the hash-based approach
            return render_template('auth/callback.html')
        
    except Exception as e:
        print(f"Auth callback error: {e}")
        flash('Authentication failed', 'error')
        return redirect(url_for('public.login'))

@bp.route('/auth/session', methods=['POST'])
def set_session():
    """Set session data from OAuth callback"""
    try:
        data = request.get_json()
        access_token = data.get('access_token')
        refresh_token = data.get('refresh_token')
        
        if access_token:
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            
            # Get user info and check admin status
            user_info = get_user_info()
            if user_info:
                session['user_email'] = user_info.get('email')
                return {'status': 'success', 'redirect': url_for('admin.index')}
            
        return {'status': 'error', 'message': 'Invalid session data'}
        
    except Exception as e:
        print(f"Session error: {e}")
        return {'status': 'error', 'message': str(e)}

@bp.route('/logout')
def logout():
    """Logout and clear session"""
    try:
        # Sign out from Supabase
        supabase.auth.sign_out()
        
        # Clear local session
        clear_auth_session()
        
        flash('Successfully logged out', 'success')
        return redirect(url_for('public.login'))
        
    except Exception as e:
        print(f"Logout error: {e}")
        clear_auth_session()  # Clear session anyway
        return redirect(url_for('public.login'))

@bp.route('/health')
def health_check():
    """Public health check endpoint"""
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}

@bp.route('/api/engagement/<article_slug>')
def get_engagement(article_slug):
    """Get engagement data for an article"""
    try:
        response = supabase.table('article_engagement').select('*').eq('article_slug', article_slug).execute()
        
        engagement_data = {}
        for item in response.data:
            engagement_data[item['interaction_type']] = item['count']
        
        return {'success': True, 'data': engagement_data}
    except Exception as e:
        print(f"Error getting engagement: {e}")
        return {'success': False, 'error': str(e)}, 500

@bp.route('/api/engagement/<article_slug>/sparkle', methods=['POST'])
def add_sparkle(article_slug):
    """Add a sparkle to an article (up to 100 per user)"""
    try:
        # Get client IP and create user identifier
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        
        # Get or create session ID for better user tracking
        if 'user_session' not in session:
            import uuid
            session['user_session'] = str(uuid.uuid4())
        
        user_identifier = f"{client_ip}_{session['user_session']}"
        
        # Check user's current contribution count
        user_response = supabase.table('user_sparkle_contributions').select('*').eq('article_slug', article_slug).eq('user_identifier', user_identifier).execute()
        
        if user_response.data:
            current_contribution = user_response.data[0]['contribution_count']
            if current_contribution >= 100:
                return {'success': False, 'error': 'Maximum sparkles reached (100)', 'user_count': current_contribution, 'at_limit': True}, 429
            
            # Increment user contribution
            new_user_count = current_contribution + 1
            supabase.table('user_sparkle_contributions').update({
                'contribution_count': new_user_count,
                'last_contributed_at': 'NOW()',
                'updated_at': 'NOW()'
            }).eq('id', user_response.data[0]['id']).execute()
        else:
            # First sparkle from this user
            new_user_count = 1
            supabase.table('user_sparkle_contributions').insert({
                'article_slug': article_slug,
                'user_identifier': user_identifier,
                'contribution_count': 1
            }).execute()
        
        # Update total article sparkle count
        response = supabase.table('article_engagement').select('*').eq('article_slug', article_slug).eq('interaction_type', 'sparkle').execute()
        
        if response.data:
            # Update existing count
            new_total_count = response.data[0]['count'] + 1
            supabase.table('article_engagement').update({'count': new_total_count, 'updated_at': 'NOW()'}).eq('id', response.data[0]['id']).execute()
        else:
            # Insert new record
            supabase.table('article_engagement').insert({
                'article_slug': article_slug,
                'interaction_type': 'sparkle',
                'count': 1
            }).execute()
            new_total_count = 1
        
        # Check for milestones
        milestone = None
        if new_user_count in [10, 25, 50, 100]:
            milestone = new_user_count
        
        return {
            'success': True, 
            'total_count': new_total_count,
            'user_count': new_user_count,
            'milestone': milestone,
            'at_limit': new_user_count >= 100
        }
    except Exception as e:
        print(f"Error adding sparkle: {e}")
        return {'success': False, 'error': str(e)}, 500

@bp.route('/api/engagement/<article_slug>/sparkle/user', methods=['GET'])
def get_user_sparkle_count(article_slug):
    """Get current user's sparkle contribution count"""
    try:
        # Get client IP and session ID
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
        
        if 'user_session' not in session:
            return {'success': True, 'user_count': 0, 'at_limit': False}
        
        user_identifier = f"{client_ip}_{session['user_session']}"
        
        # Get user's contribution count
        user_response = supabase.table('user_sparkle_contributions').select('*').eq('article_slug', article_slug).eq('user_identifier', user_identifier).execute()
        
        if user_response.data:
            user_count = user_response.data[0]['contribution_count']
            return {'success': True, 'user_count': user_count, 'at_limit': user_count >= 100}
        else:
            return {'success': True, 'user_count': 0, 'at_limit': False}
            
    except Exception as e:
        print(f"Error getting user sparkle count: {e}")
        return {'success': False, 'error': str(e)}, 500

@bp.route('/api/articles/<article_slug>/metadata')
def get_article_metadata(article_slug):
    """Get article metadata including reading time"""
    try:
        response = supabase.table('articles_metadata').select('*').eq('article_slug', article_slug).execute()
        
        if response.data:
            return {'success': True, 'data': response.data[0]}
        else:
            return {'success': False, 'error': 'Article not found'}, 404
    except Exception as e:
        print(f"Error getting article metadata: {e}")
        return {'success': False, 'error': str(e)}, 500