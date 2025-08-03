"""
Public-facing routes for articles and authentication
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
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
    return render_template('landing.html')

@bp.route('/articles/tesla-hate-machine')
def tesla_hate_machine():
    """Tesla Hate Machine article - public access"""
    # Use ALL available data for maximum impact
    months = None  # None = all time data
    
    # Get all the data needed for the article
    filtered_stats = Article.get_statistics(months)
    all_sentiment_data = Article.get_sentiment_data(months)
    top_articles = Article.get_top_articles_analysis(25, months)
    author_analysis = Article.get_author_tesla_bias(months)
    company_comparison = Article.get_company_comparison(months)
    business_metrics = Article.get_business_impact_metrics(months)
    
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
    
    return render_template('articles/tesla_hate_machine.html',
                          stats=filtered_stats,
                          sentiment_data=scatter_data,
                          correlation=correlation,
                          top_articles=top_articles,
                          author_analysis=author_analysis,
                          company_comparison=company_comparison,
                          business_metrics=business_metrics,
                          months=months)

@bp.route('/login')
def login():
    """Google OAuth login page"""
    return render_template('auth/login.html')

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
        print("=== AUTH CALLBACK DEBUG ===")
        print(f"Request URL: {request.url}")
        print(f"Request args: {dict(request.args)}")
        print(f"Request form: {dict(request.form)}")
        
        # Check if we got an authorization code (PKCE flow)
        code = request.args.get('code')
        print(f"Authorization code: {code}")
        
        if code:
            print("Attempting to exchange code for session...")
            # Exchange the code for a session using Supabase
            auth_response = supabase.auth.exchange_code_for_session({
                "auth_code": code
            })
            print(f"Auth response: {auth_response}")
            
            if auth_response.session:
                print("Session created successfully!")
                # Store session data
                session['access_token'] = auth_response.session.access_token
                session['refresh_token'] = auth_response.session.refresh_token
                
                # Get user info and check admin status
                print("Getting user info...")
                user_info = get_user_info()
                print(f"User info: {user_info}")
                
                if user_info:
                    session['user_email'] = user_info.get('email')
                    flash('Successfully logged in!', 'success')
                    return redirect(url_for('admin.index'))
                else:
                    print("Failed to get user information")
                    flash('Failed to get user information', 'error')
                    return redirect(url_for('public.login'))
            else:
                print("Failed to create session - no session in response")
                flash('Failed to create session', 'error')
                return redirect(url_for('public.login'))
        else:
            print("No code parameter, trying hash-based approach")
            # No code parameter, try the hash-based approach
            return render_template('auth/callback.html')
        
    except Exception as e:
        print(f"Auth callback error: {e}")
        import traceback
        traceback.print_exc()
        flash(f'Authentication failed: {str(e)}', 'error')
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
        return redirect(url_for('public.index'))
        
    except Exception as e:
        print(f"Logout error: {e}")
        clear_auth_session()  # Clear session anyway
        return redirect(url_for('public.index'))

@bp.route('/health')
def health_check():
    """Public health check endpoint"""
    return {'status': 'ok', 'timestamp': datetime.now().isoformat()}