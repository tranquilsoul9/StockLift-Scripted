import os

# Gunicorn configuration for Render deployment
# Render provides PORT environment variable, default to 8050 for local development
port = os.environ.get('PORT', '8050')
bind = f"0.0.0.0:{port}"
workers = 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True

# Debug: Print the port being used
print(f"Gunicorn binding to: {bind}")
