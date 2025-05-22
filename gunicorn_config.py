import multiprocessing
import os

# Create log directory if it doesn't exist
log_dir = "/var/www/extractor/logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Gunicorn configuration
bind = "0.0.0.0:8000"  # Bind to localhost on port 8000 (matching nginx config)
workers = multiprocessing.cpu_count() * 2 + 1  # Number of worker processes
worker_class = "sync"  # Worker class to use
timeout = 600  # Worker timeout in seconds (matching nginx timeout)
keepalive = 5  # Keepalive timeout
max_requests = 1000  # Maximum number of requests a worker will process before restarting
max_requests_jitter = 50  # Maximum jitter to add to max_requests
preload_app = True  # Load application code before worker processes are forked
daemon = False  # Don't daemonize (systemd will manage the process)
accesslog = "/var/www/extractor/logs/gunicorn_access.log"  # Access log file
errorlog = "/var/www/extractor/logs/gunicorn_error.log"  # Error log file
loglevel = "info"  # Log level

# Ensure proper umask for file creation
umask = 0o007
