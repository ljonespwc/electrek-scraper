# electrek_scraper/__init__.py
from flask import Flask
from .config import Config
from datetime import datetime
import re

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    from .public_views import bp as public_bp
    from .admin_views import bp as admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)
    
    # Add custom template filters
    @app.template_filter('nl2br')
    def nl2br(value):
        """Convert newlines to <br> tags for HTML display"""
        if value:
            value = re.sub(r'\r\n|\r|\n', '<br>', value)
            return value
        return ""
    
    @app.template_filter('thousands_separator')
    def thousands_separator(value):
        """Add thousands separator to a number"""
        try:
            return f"{int(value):,}"
        except (ValueError, TypeError):
            return value
    
    # Add current year for footer
    @app.context_processor
    def inject_current_year():
        """Inject current year for use in templates"""
        return {'current_year': datetime.now().year}
    
    # Add route to test if the app is running
    @app.route('/health')
    def health_check():
        return {'status': 'ok', 'timestamp': datetime.now().isoformat()}
    
    return app