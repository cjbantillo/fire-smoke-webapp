from flask import Flask, request, jsonify, render_template_string
import subprocess
import threading
import os
import signal
import sys

app = Flask(__name__)

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
    # Serve the HTML file with proper UTF-8 encoding
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

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
        
        status = {
            'status': 'healthy',
            'backend': 'running',
            'model_available': model_exists,
            'camera_accessible': camera_available,
            'timestamp': os.times()._asdict() if hasattr(os.times(), '_asdict') else 'unavailable'
        }
        
        return jsonify(status), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'backend': 'running_with_issues'
        }), 500

@app.route('/run-yolo', methods=['POST'])
def run_yolo():
    try:
        data = request.json
        model = data.get('model', 'models/best_nano_111.pt')
        source = data.get('source', 0)
        conf = data.get('conf', 0.35)
        iou = data.get('iou', 0.1)
        show = data.get('show', True)
        
        # Check if model file exists
        if not os.path.exists(model):
            return jsonify({
                'status': 'error',
                'message': f'Model file not found: {model}. Please ensure the YOLO model is available.'
            }), 404
        
        # Check if camera is accessible before starting YOLO
        try:
            import cv2
            cap = cv2.VideoCapture(source if isinstance(source, int) else 0)
            if not cap.isOpened():
                cap.release()
                return jsonify({
                    'status': 'error',
                    'message': 'Camera not accessible. Please check if camera is connected and not in use by another application.'
                }), 503
            
            # Test camera read
            ret, frame = cap.read()
            cap.release()
            
            if not ret:
                return jsonify({
                    'status': 'error',
                    'message': 'Camera detected but unable to capture frames. Please check camera permissions.'
                }), 503
                
        except Exception as cam_error:
            return jsonify({
                'status': 'error',
                'message': f'Camera error: {str(cam_error)}'
            }), 503
        
        # Build the YOLO command
        cmd = [
            'yolo', 'detect', 'predict',
            f'model={model}',
            f'source={source}',
            f'conf={conf}',
            f'iou={iou}',
            f'show={show}'
        ]
        
        # Start the process in a separate thread
        def run_command():
            try:
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
            process.terminate()
            del running_processes['yolo']
            return jsonify({
                'status': 'success',
                'message': 'YOLO detection stopped successfully!'
            })
        else:
            return jsonify({
                'status': 'info',
                'message': 'No YOLO process is currently running.'
            })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to stop YOLO detection: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
