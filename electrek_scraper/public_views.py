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
            'description': 'I analyzed 2,962 articles and 156,636 comments from the EV publication, Electrek. The results reveal a not-so-clever business model built on Tesla hate.',
            'url': 'public.fred_lambert_sellout',
            'template_path': 'articles/fred_lambert_sellout.html',
            'category': 'Analysis'
        }
    ]
    
    # Add reading times to articles
    for article in articles:
        template_path = os.path.join(current_app.root_path, 'templates', article['template_path'])
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                article_content = f.read()
            article['reading_time'] = reading_estimator.format_reading_time(article_content)
        except:
            article['reading_time'] = "12 min read"  # Fallback
    
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
    
    # Calculate reading time for the article
    from .utils.reading_time import ReadingTimeEstimator
    reading_estimator = ReadingTimeEstimator()
    
    # Read the article template to calculate reading time
    from flask import current_app
    import os
    
    template_path = os.path.join(current_app.root_path, 'templates', 'articles', 'fred_lambert_sellout.html')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
        reading_time = reading_estimator.format_reading_time(article_content)
    except:
        reading_time = "10 min read"  # Fallback for shorter version
    
    response = make_response(render_template('articles/fred_lambert_sellout.html',
                                           stats=filtered_stats,
                                           sentiment_data=scatter_data,
                                           correlation=correlation,
                                           top_articles=top_articles,
                                           author_analysis=author_analysis,
                                           company_comparison=company_comparison,
                                           business_metrics=business_metrics,
                                           reading_time=reading_time,
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