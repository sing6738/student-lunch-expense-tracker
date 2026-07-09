# Gunicorn configuration for low-resource environments (Free Tier: 0.1 CPU, 512MB RAM)

# 1 worker process is enough for low traffic and saves a massive amount of RAM.
# Flask apps typically use 50-100MB per worker. 
workers = 1

# Using threads allows the single worker to handle multiple requests concurrently
# when one request is waiting on I/O (like database queries).
threads = 2
worker_class = "gthread"

# Set a timeout to prevent stuck requests from hogging the single worker.
timeout = 30

# Max requests before restarting a worker to prevent memory leaks over time.
max_requests = 1000
max_requests_jitter = 50

# Bind to 0.0.0.0 for PaaS providers (Render, Heroku, etc.)
bind = "0.0.0.0:5000"
