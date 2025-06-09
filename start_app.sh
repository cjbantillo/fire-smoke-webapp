#!/bin/bash
# Development startup script for the Fire & Smoke Detection Web App
# This script sets environment variables and starts the Flask development server
# For production, use start_production.sh instead

echo "🔥 Starting Fire & Smoke Detection Web Application (Development Mode)..."

# Set PyTorch environment variable for compatibility
export PYTORCH_DISABLE_STRICT_LOADING=1

# Set Flask environment variables for development
export FLASK_APP=app.py
export FLASK_ENV=development

# Start the development application
echo "🚀 Starting Flask development server..."
echo "⚠️ WARNING: This is a development server, not suitable for production!"
echo "💡 For production, use: bash start_production.sh"
python app.py
