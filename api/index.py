"""
Vercel serverless function entry point for Flask app
"""
import sys
import os

# Add the parent directory to the path so we can import our Flask app
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from electrek_scraper import create_app
    
    # Create the Flask app
    app = create_app()
    
    # For Vercel's Python runtime, we need to expose 'app' directly
    # Vercel will handle the WSGI interface automatically
    
except Exception as e:
    # Fallback error handling for debugging
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error():
        return f"Import error: {str(e)}", 500
    
    @app.route('/health')
    def health():
        return {"status": "error", "message": str(e)}