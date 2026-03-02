#!/usr/bin/env python3
from flask import Flask, render_template, Response, jsonify
from flask_cors import CORS
import threading
import time
from picamera2 import Picamera2
from picamera2.encoders import MJPEGEncoder
from picamera2.outputs import FileOutput
import io
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global variables
camera = None
encoder = None
output_buffer = None
frame_count = 0
start_time = None
camera_ready = False
stream_active = False

class StreamingOutput(io.BytesIO):
    def __init__(self):
        super().__init__()
        self.frame = None
        self.condition = threading.Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()
        return len(buf)

def init_camera():
    global camera, encoder, output_buffer, camera_ready, start_time
    try:
        camera = Picamera2()

        # Configure for high quality
        config = camera.create_video_configuration(
            main={"size": (1920, 1440), "format": "RGB888"},
            encode="mjpeg",
            lores={"size": (640, 480), "format": "YUV420"}
        )
        camera.configure(config)

        # Set camera options for autofocus
        camera.set_controls({
            "AfMode": 0,  # Continuous autofocus
            "FrameRate": 30,
            "ExposureTime": 10000,
            "AnalogueGain": 1.0
        })

        output_buffer = StreamingOutput()
        encoder = MJPEGEncoder(bitrate=5000000)  # 5 Mbps

        camera.start_recording(encoder, FileOutput(output_buffer))
        camera_ready = True
        start_time = time.time()
        print("Camera initialized successfully")
        return True
    except Exception as e:
        print(f"Camera initialization error: {e}")
        camera_ready = False
        return False

def generate_frames():
    """Generator for streaming video frames"""
    while True:
        if output_buffer and output_buffer.frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n'
                   b'Content-Length: ' + str(len(output_buffer.frame)).encode() + b'\r\n'
                   b'\r\n' + output_buffer.frame + b'\r\n')
        else:
            time.sleep(0.01)

@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Stream video frames"""
    if not camera_ready:
        return "Camera not ready", 503
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/status')
def status():
    """Return system and camera status"""
    if camera_ready:
        uptime = time.time() - start_time
        return jsonify({
            'status': 'online',
            'camera': 'connected',
            'uptime_seconds': int(uptime),
            'timestamp': datetime.now().isoformat()
        })
    else:
        return jsonify({'status': 'offline', 'camera': 'disconnected'}), 503

@app.route('/api/camera/settings', methods=['GET'])
def get_camera_settings():
    """Return current camera settings"""
    if camera_ready:
        try:
            controls = camera.camera_controls
            return jsonify({
                'resolution': '1920x1440',
                'framerate': 30,
                'encoding': 'MJPEG'
            })
        except:
            pass
    return jsonify({}), 503

@app.route('/api/camera/focus', methods=['POST'])
def set_focus():
    """Adjust autofocus mode"""
    if not camera_ready:
        return jsonify({'error': 'Camera not ready'}), 503
    try:
        # AfMode: 0 = continuous, 1 = auto, 2 = manual
        camera.set_controls({"AfMode": 0})
        return jsonify({'status': 'focus_adjusted'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/capture', methods=['POST'])
def capture_frame():
    """Capture a single frame as JPEG"""
    if not camera_ready:
        return jsonify({'error': 'Camera not ready'}), 503
    try:
        metadata = camera.capture_metadata()
        camera.capture_file('/tmp/capture.jpg')
        with open('/tmp/capture.jpg', 'rb') as f:
            return Response(f.read(), mimetype='image/jpeg')
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    print("Starting bird box camera server...")
    if init_camera():
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    else:
        print("Failed to initialize camera")
        exit(1)
