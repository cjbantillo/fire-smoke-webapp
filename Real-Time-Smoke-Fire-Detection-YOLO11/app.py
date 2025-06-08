from flask import Flask, request, jsonify, render_template_string
import subprocess
import threading
import os
import signal
import sys

app = Flask(__name__)

# Global variable to track running processes
running_processes = {}

@app.route('/')
def index():
    # Serve the HTML file with proper UTF-8 encoding
    with open('index.html', 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/run-yolo', methods=['POST'])
def run_yolo():
    try:
        data = request.json
        model = data.get('model', 'models/best_nano_111.pt')
        source = data.get('source', 0)
        conf = data.get('conf', 0.35)
        iou = data.get('iou', 0.1)
        show = data.get('show', True)
        
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
