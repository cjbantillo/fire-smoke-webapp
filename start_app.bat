@echo off
REM Development startup script for the Fire & Smoke Detection Web App (Windows)
REM This script sets environment variables and starts the Flask development server
REM For production, use start_production.bat instead

echo 🔥 Starting Fire & Smoke Detection Web Application (Development Mode)...

REM Set PyTorch environment variable for compatibility
set PYTORCH_DISABLE_STRICT_LOADING=1

REM Set Flask environment variables for development
set FLASK_APP=app.py
set FLASK_ENV=development

REM Start the development application
echo 🚀 Starting Flask development server...
echo ⚠️ WARNING: This is a development server, not suitable for production!
echo 💡 For production, use: start_production.bat
python app.py

pause
