from flask import Flask, jsonify
from Camera import Camera
import threading

camera_thread = Camera()
camera_init_thread = None

app = Flask(__name__)

def start_camera_init_thread():
    global camera_init_thread
    camera_init_thread = threading.Thread(target=camera_thread.initialise_camera)
    camera_init_thread.start()

def response(has_success, description = ""):
    return jsonify({
        "success": has_success, 
        "description": description
    })

@app.route('/ping')
def ping():
    return response(True, "Pong")

@app.route('/heartbeat')
def heart_beat():
    success = camera_thread.is_running
    return response(success, "Alive and beating" if success else "Dead")

@app.get('/start')
def start_camera():
    if camera_thread.is_running:
        return response(False, "Camera already running")

    start_camera_init_thread()
    
    return response(True, "Camera initialization started")

@app.get('/stop')
def stop_camera():
    if not camera_thread.is_running:
        return response(False, "Camera has already stopped")

    # Stop the camera initialization thread gracefully
    camera_thread.shutdown()

    global camera_init_thread
    if camera_init_thread:
        camera_init_thread.join()  # Wait for the camera_init_thread to finish

    return response(True, "Camera has stopped")

if __name__ == '__main__':
    app.run()
