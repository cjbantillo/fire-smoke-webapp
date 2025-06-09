#!/usr/bin/env python3
"""
Simple script to start the Flask backend server
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    print("Starting Fire-Smoke Detection Backend Server...")
    print("Server will be available at: http://localhost:5000")
    print("Health Check: http://localhost:5000/health")
    print("Press Ctrl+C to stop the server")
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
