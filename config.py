import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

# Base directory of the application
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Session configuration
SESSION_TYPE = 'filesystem'
SESSION_FILE_DIR = os.path.join(BASE_DIR, 'flask_session')
SESSION_PERMANENT = False

# Ensure the logs directory exists with proper permissions
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
try:
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, mode=0o755)
    # Ensure log directory has correct permissions even if it already exists
    os.chmod(LOGS_DIR, 0o755)
except Exception as e:
    print(f"Warning: Could not create or set permissions for logs directory: {e}")
    # Fallback to /tmp for logs if we can't write to the app directory
    LOGS_DIR = '/tmp'

# Configure logging
def setup_logging():
    try:
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # Log file path
        log_file = os.path.join(LOGS_DIR, 'app.log')
        
        # Create log file if it doesn't exist and set permissions
        if not os.path.exists(log_file):
            open(log_file, 'a').close()
            os.chmod(log_file, 0o644)
        
        # Create and configure the file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(file_formatter)
        
        # Create and configure the console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Get the root logger and configure it
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        
        # Remove any existing handlers
        root_logger.handlers = []
        
        # Add the handlers
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        # Configure specific loggers
        loggers = [
            'app',
            'app.scrapers',
            'app.services',
            'app.routes',
            'werkzeug'
        ]
        
        for logger_name in loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
            # Don't propagate to avoid duplicate logs
            logger.propagate = False
            logger.handlers = []
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
    except Exception as e:
        print(f"Warning: Could not set up file logging: {e}")
        # Set up console-only logging as fallback
        logging.basicConfig(
            level=logging.INFO,
            format='%(levelname)s - %(message)s'
        )

# Call setup_logging when config is imported
setup_logging()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-please-change-in-production')
    FLASK_APP = os.getenv('FLASK_APP', 'app.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Session configuration
    SESSION_TYPE = SESSION_TYPE
    SESSION_FILE_DIR = SESSION_FILE_DIR
    SESSION_PERMANENT = SESSION_PERMANENT
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
    
    # Authentication
    USERS_FILE = os.path.join(BASE_DIR, 'app/auth/users.json')
    
    # Scraping configuration
    CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '/usr/local/bin/chromedriver')
    HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'
    
    # Report generation
    MAX_DESTINATION_COUNTRIES = 5
    MAX_HS6_CODES = 10 