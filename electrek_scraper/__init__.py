# electrek_scraper/__init__.py
from flask import Flask
from .config import Config
from datetime import datetime
import re

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    from .views import bp as main_bp
    app.register_blueprint(main_bp)
    
    # Add custom template filters
    @app.template_filter('nl2br')
    def nl2br(value):
        """Convert newlines to <br> tags for HTML display"""
        if value:
            value = re.sub(r'\r\n|\r|\n', '<br>', value)
            return value
        return ""
    
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