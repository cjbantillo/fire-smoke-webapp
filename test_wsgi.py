#!/usr/bin/env python3
"""
Test script to verify WSGI configuration works properly
"""

import os
import sys
import time
import requests
import subprocess
from pathlib import Path

def test_wsgi_setup():
    """Test if WSGI configuration is working"""
    print("🔄 Testing WSGI setup...")
    
    # Test 1: Check if wsgi.py imports correctly
    try:
        print("📝 Testing WSGI import...")
        import wsgi
        print("✅ WSGI module imports successfully")
        
        app = wsgi.application
        print(f"✅ Flask application object: {type(app)}")
        
    except Exception as e:
        print(f"❌ WSGI import failed: {str(e)}")
        return False
    
    # Test 2: Check if gunicorn can be imported
    try:
        print("📝 Testing Gunicorn availability...")
        import gunicorn
        print(f"✅ Gunicorn available: {gunicorn.__version__}")
        
    except ImportError:
        print("❌ Gunicorn not available - install with: pip install gunicorn")
        return False
    
    # Test 3: Check if eventlet is available (for WebSocket support)
    try:
        print("📝 Testing Eventlet availability...")
        import eventlet
        print(f"✅ Eventlet available: {eventlet.__version__}")
        
    except ImportError:
        print("❌ Eventlet not available - install with: pip install eventlet")
        return False
    
    print("🎉 All WSGI components are properly configured!")
    return True

def show_deployment_commands():
    """Show available deployment commands"""
    print("\n📋 Available deployment options:")
    print("\n🔧 Development:")
    print("   Windows: start_app.bat")
    print("   Linux/Mac: bash start_app.sh")
    print("   Direct: python app.py")
    
    print("\n🚀 Production (WSGI):")
    print("   Windows: start_production.bat")
    print("   Linux/Mac: bash start_production.sh")
    print("   Direct: gunicorn --worker-class eventlet -w 1 wsgi:application")
    
    print("\n☁️ Cloud Deployment:")
    print("   Render: Uses Procfile automatically")
    print("   Heroku: Uses Procfile automatically")
    print("   Docker: Create Dockerfile with gunicorn command")

if __name__ == "__main__":
    print("🔥 Fire & Smoke Detection - WSGI Configuration Test")
    print("=" * 60)
    
    success = test_wsgi_setup()
    show_deployment_commands()
    
    if success:
        print("\n✅ WSGI setup is ready for production deployment!")
    else:
        print("\n❌ WSGI setup needs attention before production deployment.")
        
    print("\n💡 Next steps:")
    print("1. Test locally: python wsgi.py")
    print("2. Test with Gunicorn: gunicorn wsgi:application")
    print("3. Deploy to cloud platform with updated Procfile")
