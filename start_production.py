#!/usr/bin/env python3
"""
Cross-platform production server launcher
Automatically chooses the best WSGI server for the current platform
"""

import os
import sys
import platform
from pathlib import Path

def setup_environment():
    """Set up environment variables for production"""
    os.environ['PYTORCH_DISABLE_STRICT_LOADING'] = '1'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['NODE_ENV'] = 'production'
    
    port = os.environ.get('PORT', '5000')
    return int(port)

def start_with_gunicorn(port):
    """Start with Gunicorn (Linux/Mac/WSL)"""
    print("🐧 Starting with Gunicorn (recommended for Unix systems)...")
    
    try:
        import gunicorn.app.wsgiapp
        
        # Gunicorn command line arguments
        sys.argv = [
            'gunicorn',
            '--worker-class', 'eventlet',
            '--workers', '1',
            '--bind', f'0.0.0.0:{port}',
            '--timeout', '120',
            '--keep-alive', '2',
            '--max-requests', '1000',
            '--max-requests-jitter', '100',
            '--preload',
            '--access-logfile', '-',
            '--error-logfile', '-',
            'wsgi:application'
        ]
        
        gunicorn.app.wsgiapp.run()
        
    except ImportError:
        print("❌ Gunicorn not available")
        return False
    except Exception as e:
        print(f"❌ Gunicorn failed: {e}")
        return False
    
    return True

def start_with_waitress(port):
    """Start with Waitress (Windows-friendly)"""
    print("🪟 Starting with Waitress (Windows-compatible WSGI server)...")
    
    try:
        from waitress import serve
        from wsgi import application
        
        print(f"✅ Waitress server starting on http://0.0.0.0:{port}")
        serve(application, host='0.0.0.0', port=port, threads=4)
        
    except ImportError:
        print("❌ Waitress not available - install with: pip install waitress")
        return False
    except Exception as e:
        print(f"❌ Waitress failed: {e}")
        return False
    
    return True

def start_with_flask_dev(port):
    """Fallback to Flask development server"""
    print("⚠️ Falling back to Flask development server...")
    print("💡 This is NOT recommended for production!")
    
    try:
        from wsgi import application, socketio
        socketio.run(application, debug=False, host='0.0.0.0', port=port)
        
    except Exception as e:
        print(f"❌ Flask dev server failed: {e}")
        return False
    
    return True

def main():
    """Main server launcher"""
    print("🔥 Fire & Smoke Detection - Production Server Launcher")
    print("=" * 60)
    
    # Setup environment
    port = setup_environment()
    system = platform.system().lower()
    
    print(f"🌍 Environment: production")
    print(f"🔌 Port: {port}")
    print(f"💻 Platform: {system}")
    print(f"🐍 Python: {platform.python_version()}")
    
    # Try servers in order of preference
    servers = []
    
    if system in ['linux', 'darwin'] or 'wsl' in platform.uname().release.lower():
        # Unix-like systems prefer Gunicorn
        servers = [
            ('Gunicorn', start_with_gunicorn),
            ('Waitress', start_with_waitress),
            ('Flask Dev', start_with_flask_dev)
        ]
    else:
        # Windows prefers Waitress
        servers = [
            ('Waitress', start_with_waitress),
            ('Gunicorn', start_with_gunicorn),
            ('Flask Dev', start_with_flask_dev)
        ]
    
    print(f"🚀 Trying servers in order: {' → '.join([s[0] for s in servers])}")
    print()
    
    # Try each server
    for name, start_func in servers:
        print(f"🔄 Attempting to start with {name}...")
        try:
            if start_func(port):
                print(f"✅ {name} started successfully!")
                break
        except KeyboardInterrupt:
            print(f"\n🛑 {name} stopped by user")
            break
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            continue
    else:
        print("❌ All server options failed!")
        print("\n💡 Try installing missing dependencies:")
        print("   pip install gunicorn waitress")
        sys.exit(1)

if __name__ == "__main__":
    main()
