@echo off
REM Production startup script for Fire & Smoke Detection Web App (Windows)
REM Note: Gunicorn has limited Windows support. For production on Windows, consider:
REM 1. Using WSL (Windows Subsystem for Linux)
REM 2. Using Docker
REM 3. Using waitress server instead

echo 🔥 Starting Fire & Smoke Detection Web Application (Production Mode)...

REM Set environment variables
set PYTORCH_DISABLE_STRICT_LOADING=1
set FLASK_ENV=production
set NODE_ENV=production

REM Get port from environment or default to 5000
if not defined PORT set PORT=5000

echo 🌍 Environment: production
echo 🔌 Port: %PORT%

REM Check if WSL is available and prefer it for Gunicorn
where wsl >nul 2>nul
if %ERRORLEVEL% == 0 (
    echo 🐧 Using WSL for better Gunicorn support...
    wsl gunicorn --worker-class eventlet --workers 1 --bind 0.0.0.0:%PORT% wsgi:application
) else (
    echo 🚀 Starting with Waitress (Windows-compatible WSGI server)...
    echo 💡 Install waitress for better Windows support: pip install waitress
    python -c "
import sys
try:
    from waitress import serve
    from wsgi import application
    print('✅ Starting Waitress server on port %PORT%...')
    serve(application, host='0.0.0.0', port=%PORT%)
except ImportError:
    print('❌ Waitress not found. Falling back to Flask dev server.')
    print('💡 For production on Windows, install: pip install waitress')
    import wsgi
    wsgi.application.run(host='0.0.0.0', port=%PORT%, debug=False)
except Exception as e:
    print(f'❌ Error: {e}')
    print('💡 Try: pip install waitress')
"
)

pause
