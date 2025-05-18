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

# Ensure the logs directory exists
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
def setup_logging():
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    
    # Create and configure the file handler
    file_handler = RotatingFileHandler(
        os.path.join(LOGS_DIR, 'app.log'),
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
    USERS_FILE = 'app/auth/users.json'
    
    # Scraping configuration
    CHROME_DRIVER_PATH = os.getenv('CHROME_DRIVER_PATH', '')
    HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'
    
    # Report generation
    MAX_DESTINATION_COUNTRIES = 5
    MAX_HS6_CODES = 10 