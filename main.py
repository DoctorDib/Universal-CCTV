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

react_folder = 'Client'
directory= os.getcwd() + f'/{react_folder}/build/static'

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

def generate_frames():
    while camera_thread.is_running:
        frame = camera_thread.get_frame()
        yield (b'--FRAME\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
def videos_page():
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

# CLIENT API

@app.route('/')
def index():
    ''' User will call with with thier id to store the symbol as registered'''
    path= os.getcwd()+ f'/{react_folder}/build'
    print(path)
    return send_from_directory(directory=path,path='index.html')

@app.route('/static/<folder>/<file>')
def css(folder,file):
    ''' User will call with with thier id to store the symbol as registered'''
    
    path = folder+'/'+file
    return send_from_directory(directory=directory,path=path)

# Video feed

@app.route('/video_feed')
def video_feed():
    return camera_thread.flask_stream()

def response(has_success, description="", data={}):
    return jsonify({
        "success": has_success, 
        "description": description,
        "data": data,
    })


# Initial start
if __name__ == '__main__':
    # os.chdir('/home/james/PiSecurityCamera')

    start_camera_init_thread()
    start_servo_init_thread()
    
    app.run(host='0.0.0.0')
