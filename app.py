from flask import Flask, request, jsonify, Response, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import cv2
import os
import subprocess
import threading
import signal
import sys
import base64
import numpy as np

# Set environment variable to handle PyTorch 2.6 compatibility
os.environ['PYTORCH_DISABLE_STRICT_LOADING'] = '1'

from ultralytics import YOLO
import json
from datetime import datetime
import time
import urllib.request

app = Flask(__name__)
CORS(app, origins=["*"])
socketio = SocketIO(app, cors_allowed_origins="*")

# Get port from environment variable or default to 5000
port = int(os.environ.get('PORT', 5000))
environment = os.environ.get('NODE_ENV', 'development')

def download_model_if_needed():
    """Download model from cloud storage if not present locally"""
    model_path = 'models/best_nano_111.pt'
    
    if not os.path.exists("models"):
        os.makedirs("models")
    
    if not os.path.exists(model_path):
        print("📥 Model not found locally. Checking for download...")
        # You can add your cloud storage URL here when ready
        # model_url = "https://your-cloud-storage/best_nano_111.pt"
        # urllib.request.urlretrieve(model_url, model_path)
        print("⚠️ Model file not found. Please ensure model is available.")
    
    return model_path

# Download model if needed
model_path = download_model_if_needed()

# Load YOLO model globally
model = None
latest_detections = []
detection_lock = threading.Lock()

def load_yolo_model(model_path):
    """
    Load YOLO model with multiple fallback methods for PyTorch compatibility
    """
    if not os.path.exists(model_path):
        print(f"⚠️ YOLO model not found at {model_path}")
        return None
    
    # Method 1: Try with environment variable set
    try:
        print("🔄 Loading YOLO model (Method 1: Standard loading)...")
        model = YOLO(model_path)
        print(f"✅ YOLO model loaded successfully from {model_path}")
        return model
    except Exception as e1:
        print(f"⚠️ Method 1 failed: {str(e1)}")
    
    # Method 2: Try with safe globals
    try:
        print("🔄 Loading YOLO model (Method 2: Safe globals)...")
        import torch
        torch.serialization.add_safe_globals([
            'ultralytics.nn.tasks.DetectionModel',
            'ultralytics.nn.modules.block.C2f',
            'ultralytics.nn.modules.block.SPPF',
            'ultralytics.nn.modules.conv.Conv',
            'ultralytics.nn.modules.head.Detect',
            'collections.OrderedDict'
        ])
        model = YOLO(model_path)
        print(f"✅ YOLO model loaded successfully with safe globals")
        return model
    except Exception as e2:
        print(f"⚠️ Method 2 failed: {str(e2)}")
    
    # Method 3: Information about potential fixes
    print("❌ All loading methods failed!")
    print("💡 Potential solutions:")
    print("   1. Update ultralytics: pip install ultralytics==8.2.0")
    print("   2. Or set: export PYTORCH_DISABLE_STRICT_LOADING=1")
    print("   3. Or downgrade PyTorch: pip install torch<2.6")
    
    return None

# Download model if needed
model_path = download_model_if_needed()

# Load YOLO model globally
model = None
latest_detections = []
detection_lock = threading.Lock()

model = load_yolo_model(model_path)

def add_detection(detection_type, confidence):
    """Add a new detection to the global list"""
    try:
        with detection_lock:
            detection = {
                'type': detection_type,
                'confidence': round(confidence * 100, 1) if confidence < 1 else round(confidence, 1),
                'timestamp': datetime.now().isoformat(),
                'id': int(time.time() * 1000)
            }
            latest_detections.append(detection)
            
            # Keep only last 50 detections
            if len(latest_detections) > 50:
                latest_detections.pop(0)
                
            print(f"🚨 Detection added: {detection}")
    except Exception as e:
        print(f"Error adding detection: {e}")

# Add CORS headers to all responses
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Global variable to track running processes
running_processes = {}

@app.route('/')
def serve_frontend():
    """Serve the frontend application"""
    if environment == 'production':
        # In production, serve the built frontend
        frontend_path = os.path.join('frontend', 'dist')
        if os.path.exists(os.path.join(frontend_path, 'index.html')):
            return send_from_directory(frontend_path, 'index.html')
    
    # Development or fallback - serve API info
    return jsonify({
        'message': 'Fire Detection API is running',
        'version': '2.0.0',
        'environment': environment,
        'endpoints': ['/health', '/run-yolo', '/stop-yolo', '/detect-frame', '/detections'],
        'model_loaded': model is not None
    })

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files for the frontend"""
    if path.startswith('api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    
    if environment == 'production':
        frontend_path = os.path.join('frontend', 'dist')
        try:
            return send_from_directory(frontend_path, path)
        except:
            # Fallback to index.html for SPA routing
            if os.path.exists(os.path.join(frontend_path, 'index.html')):
                return send_from_directory(frontend_path, 'index.html')
    
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/health', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify backend is running"""
    try:
        # Check if YOLO model file exists
        model_path = 'models/best_nano_111.pt'
        model_exists = os.path.exists(model_path)
        
        # Check if camera is accessible (basic check)
        camera_available = True
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                camera_available = ret is not None
                cap.release()
            else:
                camera_available = False
        except Exception:
            camera_available = False
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'model_available': model_exists,
            'model_loaded': model is not None,
            'camera_accessible': camera_available,
            'version': '2.0.0'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()        }), 500

@app.route('/api/detections', methods=['GET'])
@app.route('/detections', methods=['GET'])
def get_detections():
    """Get latest detection results"""
    try:
        with detection_lock:
            # Return last 5 detections
            recent_detections = latest_detections[-5:] if latest_detections else []
        
        return jsonify({
            'status': 'success',
            'detections': recent_detections,
            'total_count': len(latest_detections),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to get detections: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

# NEW: Frame-by-frame detection endpoint
@app.route('/detect-frame', methods=['POST'])
def detect_frame():
    """Process a single frame for fire/smoke detection"""
    try:
        if not model:
            return jsonify({
                'error': 'YOLO model not loaded',
                'detections': []
            }), 500
        
        # Get image data from request
        data = request.get_json()
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        try:
            image_data = data['image']
            # Remove data URL prefix if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return jsonify({'error': 'Invalid image data'}), 400
            
            # NEW: Color format conversion (browser gives RGB, OpenCV expects BGR)
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            
            # NEW: Resize frame to optimal YOLO input size
            frame_resized = cv2.resize(frame, (640, 640))
                
        except Exception as e:
            return jsonify({'error': f'Image decoding failed: {str(e)}'}), 400
        
        # Run YOLO detection on resized frame
        results = model(frame_resized, conf=0.30, iou=0.1, verbose=False)
        
        # Extract detections
        detections = []
        if results and len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for i in range(len(boxes)):
                box = boxes[i]
                detection = {
                    'class': model.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': {
                        'x1': float(box.xyxy[0][0]),
                        'y1': float(box.xyxy[0][1]),
                        'x2': float(box.xyxy[0][2]),
                        'y2': float(box.xyxy[0][3])
                    }
                }
                detections.append(detection)
        
        return jsonify({
            'detections': detections,
            'timestamp': datetime.now().isoformat(),
            'frame_processed': True
        })
        
    except Exception as e:
        return jsonify({
            'error': f'Detection failed: {str(e)}',
            'detections': []
        }), 500

# NEW: WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected to WebSocket')
    emit('status', {'message': 'Connected to fire detection server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from WebSocket')

@socketio.on('video_frame')
def handle_video_frame(data):
    """Handle real-time video frame processing via WebSocket"""
    try:
        if not model:
            emit('detection_error', {'error': 'YOLO model not loaded'})
            return
        
        # Process frame same way as detect_frame endpoint
        image_data = data.get('frame')
        if not image_data:
            emit('detection_error', {'error': 'No frame data provided'})
            return
        
        # Decode and process frame
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            emit('detection_error', {'error': 'Invalid frame data'})
            return
        
        # NEW: Color format conversion and resizing
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_resized = cv2.resize(frame, (640, 640))
        
        # Run detection on resized frame
        results = model(frame_resized, conf=0.30, iou=0.1, verbose=False)
        
        # Extract detections
        detections = []
        if results and len(results) > 0 and results[0].boxes is not None:
            boxes = results[0].boxes
            for i in range(len(boxes)):
                box = boxes[i]
                detection = {
                    'class': model.names[int(box.cls[0])],
                    'confidence': float(box.conf[0]),
                    'bbox': {
                        'x1': float(box.xyxy[0][0]),
                        'y1': float(box.xyxy[0][1]),
                        'x2': float(box.xyxy[0][2]),
                        'y2': float(box.xyxy[0][3])
                    }
                }
                detections.append(detection)
        
        # Emit results back to client
        emit('detection_results', {
            'detections': detections,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        emit('detection_error', {'error': f'Frame processing failed: {str(e)}'})

@app.route('/run-yolo', methods=['POST'])
def run_yolo():
    try:
        # Test camera access first
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return jsonify({
                'status': 'error',
                'message': 'Camera not found or already in use by another application.'
            }), 503
        
        # Test camera read
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return jsonify({
                'status': 'error',
                'message': 'Camera detected but unable to capture frames. Please check camera permissions.'
            }), 503
            
        def run_command():
            try:
                # Build YOLO command
                cmd = [
                    'yolo', 'detect', 'predict',
                    'model=models/best_nano_111.pt',
                    'source=0',
                    'conf=0.35',
                    'iou=0.1',
                    'show=True'
                ]
                
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                running_processes['yolo'] = process
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    print(f"YOLO completed successfully: {stdout}")
                else:
                    print(f"YOLO failed: {stderr}")
            except Exception as e:
                print(f"Error running YOLO: {str(e)}")
        
        thread = threading.Thread(target=run_command)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'YOLO detection started successfully! Check your camera window.'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start YOLO detection: {str(e)}'
        }), 500

@app.route('/stop-yolo', methods=['POST'])
def stop_yolo():
    try:
        if 'yolo' in running_processes:
            process = running_processes['yolo']
            if process.poll() is None:  # Process is still running
                process.terminate()
                process.wait(timeout=5)
                del running_processes['yolo']
                return jsonify({
                    'status': 'success',
                    'message': 'YOLO detection stopped successfully.'
                })
            else:
                del running_processes['yolo']
                return jsonify({
                    'status': 'success',
                    'message': 'YOLO detection was already stopped.'
                })
        else:
            return jsonify({
                'status': 'success',
                'message': 'No YOLO detection process was running.'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to stop YOLO detection: {str(e)}'
        }), 500

def signal_handler(sig, frame):
    print('\nShutting down server...')
    # Clean up any running processes
    for name, process in running_processes.items():
        if process.poll() is None:
            print(f'Terminating {name} process...')
            process.terminate()
            process.wait()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    print("🔥 Fire Detection API Server Starting...")
    print(f"🌍 Environment: {environment}")
    print(f"🔌 Port: {port}")
    print("📋 Available endpoints:")
    print("   GET  /health - Health check")
    print("   GET  /detections - Get latest detections")
    print("   POST /run-yolo - Start YOLO detection")
    print("   POST /stop-yolo - Stop YOLO detection")
    print("   POST /detect-frame - Process single frame")
    print("   WebSocket /socket.io - Real-time detection")
    
    debug_mode = environment == 'development'
    socketio.run(app, debug=debug_mode, host='0.0.0.0', port=port)
