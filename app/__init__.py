from flask import Flask
from flask_login import LoginManager
from flask_session import Session
from config import Config
import os
import logging
from logging.handlers import RotatingFileHandler

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

def format_number(value):
    """Format numbers with commas as thousand separators."""
    try:
        # Remove any existing commas and spaces
        value = str(value).replace(',', '').replace(' ', '')
        
        # Check if it's a number with a decimal point
        if '.' in value:
            # Format float with commas
            parts = value.split('.')
            integer_part = "{:,}".format(int(parts[0]))
            return f"{integer_part}.{parts[1]}"
        else:
            # Format integer with commas
            return "{:,}".format(int(value))
    except (ValueError, TypeError):
        return value

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Ensure the session directory exists
    if app.config['SESSION_TYPE'] == 'filesystem':
        os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)
    
    # Initialize extensions
    login_manager.init_app(app)
    Session(app)
    
    # Register custom filters
    app.jinja_env.filters['format_number'] = format_number
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/extractor.log',
                                         maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Extractor startup')
    
    # Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.auth.models import User
        return User.get(user_id)
    
    return app 