"""
Vercel serverless function entry point for Flask app
"""
import sys
import os

# Add the parent directory to the path so we can import our Flask app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from electrek_scraper import create_app

# Create the Flask app
app = create_app()

# Vercel expects a function that handles the request
def handler(request):
    """Handle incoming requests for Vercel"""
    return app(request.environ, request.start_response)

# For Vercel, we also need to export the app directly
# This allows Vercel's Python runtime to handle the WSGI interface
if __name__ != "__main__":
    # When imported by Vercel, expose the app
    application = app