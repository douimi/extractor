import multiprocessing

# Gunicorn configuration
bind = "0.0.0.0:5000"  # Unix socket for Nginx to connect to
workers = multiprocessing.cpu_count() * 2 + 1  # Number of worker processes
worker_class = "sync"  # Worker class to use
timeout = 120  # Worker timeout in seconds
keepalive = 5  # Keepalive timeout
max_requests = 1000  # Maximum number of requests a worker will process before restarting
max_requests_jitter = 50  # Maximum jitter to add to max_requests
preload_app = True  # Load application code before worker processes are forked
daemon = False  # Don't daemonize (systemd will manage the process)
accesslog = "/var/log/gunicorn/access.log"  # Access log file
errorlog = "/var/log/gunicorn/error.log"  # Error log file
loglevel = "info"  # Log level 
