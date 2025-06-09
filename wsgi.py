#!/usr/bin/env python3
"""
WSGI entry point for the Fire & Smoke Detection Web Application
This file is used for production deployments with WSGI servers like Gunicorn
"""

import os
import sys
from pathlib import Path

# Add the application directory to Python path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

# Set environment variables for production
os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('PYTORCH_DISABLE_STRICT_LOADING', '1')

# Import the Flask application
from app import app, socketio

# WSGI application object
application = app

# For SocketIO with WSGI
def create_app():
    """Create and configure the Flask application for WSGI"""
    return socketio

if __name__ == "__main__":
    # This won't be called in WSGI mode, but kept for compatibility
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
