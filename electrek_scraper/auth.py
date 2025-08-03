"""
Authentication decorators and helpers for Supabase OAuth
"""
from functools import wraps
from flask import request, redirect, url_for, session, current_app, jsonify
from supabase import create_client
from .config import Config
import jwt

# Initialize Supabase client
supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

def login_required(f):
    """Decorator to require authentication for admin routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            # Try to get token from session
            access_token = session.get('access_token')
            if not access_token:
                return redirect(url_for('public.login'))
        else:
            access_token = auth_header.replace('Bearer ', '')
        
        try:
            # Verify the JWT token
            decoded_token = jwt.decode(
                access_token, 
                options={"verify_signature": False}  # Supabase handles signature verification
            )
            
            # Check if user is admin
            user_email = decoded_token.get('email')
            if not is_admin_user(user_email):
                return jsonify({'error': 'Admin access required'}), 403
                
            # Store user info in request context
            request.user = decoded_token
            return f(*args, **kwargs)
            
        except jwt.InvalidTokenError:
            return redirect(url_for('public.login'))
    
    return decorated_function

def admin_required(f):
    """Decorator specifically for admin-only access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is authenticated
        access_token = session.get('access_token')
        if not access_token:
            return redirect(url_for('public.login'))
        
        try:
            # Verify the JWT token
            decoded_token = jwt.decode(
                access_token, 
                options={"verify_signature": False}
            )
            
            # Check if user is admin
            user_email = decoded_token.get('email')
            if not is_admin_user(user_email):
                return jsonify({'error': 'Admin access required'}), 403
                
            request.user = decoded_token
            return f(*args, **kwargs)
            
        except jwt.InvalidTokenError:
            return redirect(url_for('public.login'))
    
    return decorated_function

def is_admin_user(email):
    """Check if user email is in admin role"""
    if not email:
        return False
    
    try:
        result = supabase.table('user_roles').select('role').eq('email', email).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]['role'] == 'admin'
        return False
    except Exception as e:
        print(f"Error checking admin status: {e}")
        return False

def get_user_info():
    """Get current user information from session"""
    access_token = session.get('access_token')
    if not access_token:
        return None
    
    try:
        decoded_token = jwt.decode(
            access_token, 
            options={"verify_signature": False}
        )
        return decoded_token
    except jwt.InvalidTokenError:
        return None

def clear_auth_session():
    """Clear authentication session data"""
    session.pop('access_token', None)
    session.pop('refresh_token', None)
    session.pop('user_email', None)