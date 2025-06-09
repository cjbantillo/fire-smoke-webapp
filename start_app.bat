@echo off
REM Startup script for the Fire & Smoke Detection Web App (Windows)
REM This script sets environment variables and starts the Flask application

echo 🔥 Starting Fire & Smoke Detection Web Application...

REM Set PyTorch environment variable for compatibility
set PYTORCH_DISABLE_STRICT_LOADING=1

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=production

REM Start the application
echo 🚀 Starting Flask server...
python app.py

pause
