from flask import Flask, request, jsonify, Response
from flask_socketio import SocketIO, emit
import cv2
import os
import subprocess
import threading
import signal
import sys
import base64
import numpy as np
from ultralytics import YOLO
import json
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Load YOLO model globally
model = None
try:
    model_path = 'models/best_nano_111.pt'
    if os.path.exists(model_path):
        model = YOLO(model_path)
        print(f"✅ YOLO model loaded successfully from {model_path}")
    else:
        print(f"⚠️ YOLO model not found at {model_path}")
except Exception as e:
    print(f"❌ Error loading YOLO model: {str(e)}")

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
def index():
    return jsonify({
        'message': 'Fire Detection API is running',
        'version': '2.0.0',
        'endpoints': ['/health', '/run-yolo', '/stop-yolo', '/detect-frame'],
        'model_loaded': model is not None
    })

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
    print("📋 Available endpoints:")
    print("   GET  /health - Health check")
    print("   POST /run-yolo - Start YOLO detection")
    print("   POST /stop-yolo - Stop YOLO detection")
    print("   POST /detect-frame - Process single frame")
    print("   WebSocket /socket.io - Real-time detection")
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
