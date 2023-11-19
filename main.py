from flask import Flask, jsonify, render_template, send_from_directory

from Camera import Camera
from Servo import Servo
from Config import Config

import threading
import os

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

## CAMERA API

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

## SERVO API

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

## FILE MANAGER API

@app.get('/get_files')
def get_files():
    output_directory = Config().get_output_path()
    file_list = os.listdir(output_directory)
    return response(True, data={ "files": file_list })

@app.route('/videos')
def index():
    output_directory = Config().get_output_path()
    file_list = os.listdir(output_directory)
    print(os.getcwd())
    print("============")
    print("============")
    print("============")
    print("============")
    print("============")
    print("============")
    # return True
    return render_template('./main.html', files=file_list)

@app.route('/download/<filename>')
def download_video(filename):
    output_directory = Config().get_output_path()
    return send_from_directory(output_directory, filename)

@app.route('/video/<filename>')
def view_video(filename):
    output_directory = Config().get_output_path()
    video_path = os.path.join(output_directory, filename)
    return render_template('video.html', video_path=video_path)

# Initial start
if __name__ == '__main__':
    os.chdir('/home/james/PiSecurityCamera')

    start_camera_init_thread()
    start_servo_init_thread()
    
    app.run(host='0.0.0.0')
