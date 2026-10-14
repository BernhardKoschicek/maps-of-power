"""Gunicorn configuration for production and container deployments."""
# pylint: disable=invalid-name

import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"
backlog = 2048

workers = int(
    os.environ.get('WEB_CONCURRENCY', os.environ.get('WORKERS', '3')))
threads = int(os.environ.get('THREADS', '2'))
worker_class = 'gthread'
worker_connections = 1000
timeout = int(os.environ.get('TIMEOUT', '120'))
keepalive = int(os.environ.get('KEEPALIVE', '5'))

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('LOG_LEVEL', 'info')
capture_output = True

# Process naming
proc_name = 'maps-of-power'
