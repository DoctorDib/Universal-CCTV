from flask import Flask, jsonify
from Camera import Camera
from Servo import Servo
import threading

camera_thread : Camera = Camera()
# camera_init_thread = None

servo_thread : Servo = Servo(11)
# servo_init_thread = None

app = Flask(__name__)

# eleven = Servo(11)

def start_camera_init_thread():
    global camera_init_thread
    camera_init_thread = threading.Thread(target=camera_thread.initialise_camera)
    camera_init_thread.start()

def start_servo_init_thread():
    global servo_init_thread
    servo_init_thread = threading.Thread(target=servo_thread.setup)
    servo_init_thread.start()

def response(has_success, description="", data={}):
    return jsonify({
        "success": has_success, 
        "description": description,
        "data": data,
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
    start_servo_init_thread()
    
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

@app.get('/move/<int:percentage>')
def ser_servo(percentage):
    try:
        servo_thread.move(percentage)
    except Exception as e:
        print(e)
    return response(True, f"Moved to: {percentage}")

@app.get('/get_position')
def get_servo_position():
    return response(True, data={ "position": servo_thread.current_position })

# Initial start
if __name__ == '__main__':
    start_camera_init_thread()
    start_servo_init_thread()
    
    app.run(host='0.0.0.0')
