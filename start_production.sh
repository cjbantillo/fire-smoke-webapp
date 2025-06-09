#!/bin/bash
# Production startup script for Fire & Smoke Detection Web App
# Uses Gunicorn WSGI server for production deployment

echo "🔥 Starting Fire & Smoke Detection Web Application (Production Mode)..."

# Set environment variables
export PYTORCH_DISABLE_STRICT_LOADING=1
export FLASK_ENV=production
export NODE_ENV=production

# Get port from environment or default to 5000
PORT=${PORT:-5000}

echo "🌍 Environment: production"
echo "🔌 Port: $PORT"
echo "🚀 Starting Gunicorn WSGI server..."

# Start with Gunicorn
gunicorn --worker-class eventlet \
         --workers 1 \
         --bind 0.0.0.0:$PORT \
         --timeout 120 \
         --keep-alive 2 \
         --max-requests 1000 \
         --max-requests-jitter 100 \
         --preload \
         --access-logfile - \
         --error-logfile - \
         wsgi:application
