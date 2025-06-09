#!/bin/bash
# Startup script for the Fire & Smoke Detection Web App
# This script sets environment variables and starts the Flask application

echo "🔥 Starting Fire & Smoke Detection Web Application..."

# Set PyTorch environment variable for compatibility
export PYTORCH_DISABLE_STRICT_LOADING=1

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=production

# Start the application
echo "🚀 Starting Flask server..."
python app.py
