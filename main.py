from flask import Flask, jsonify, render_template, send_from_directory
from flask_cors import CORS

from Camera import Camera
from Servo import Servo
from Config import Config

import subprocess
import os.path
from time import sleep

import threading
import os

camera_thread : Camera = Camera()
servo_thread : Servo = Servo(11)

app = Flask(__name__)
CORS(app)

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

@app.get('/restart')
def restart_camera():
    stop_camera()
    sleep(0.5)
    print("starting camera")
    start_camera_init_thread()
    return response(True, "Camera restarted")

@app.get('/stop')
def stop_camera():
    if not camera_thread.is_running:
        return response(False, "Camera has already stopped")

    # Stop the camera initialization thread gracefully
    camera_thread.shutdown()

    print("Shutting down camera thread")
    global camera_init_thread
    if camera_init_thread:
        camera_init_thread.join()  # Wait for the camera_init_thread to finish

    print("Fin shutting down")
    return response(True, "Camera has stopped")

@app.get('/snapshot')
def take_snapshot():
    # Taking a snapshot
    camera_thread.snapshot()
    return response(True, "Snapshot taken")

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

@app.get('/get_percentage')
def get_servo_position_percentage():
    return response(True, data={ "position": servo_thread.percentage })

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
    # return True
    return render_template('./main.html', files=file_list)

@app.route('/download/<filename>')
def download_video(filename):
    output_directory = Config().get_output_path()
    return send_from_directory(output_directory, filename, as_attachment=True)

@app.route('/video/<filename>')
def view_video(filename):
    output_directory = Config().get_output_path()
    return send_from_directory(output_directory, filename, conditional=True)

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

@app.route('/convert/<file>')
def convert(file):
    convert(file)
    return True

def convert(filename):
    dest = f'/home/james/PiSecurityCamera/output_mp4/{filename.replace("h264", "mp4")}'
    cmd='/usr/bin/ffmpeg -i "{}" -f mp4 -vcodec copy -acodec libfaac -b:a 112k -ac 2 -y "{}"'.format(Config().get_output_path() + '/' + filename, dest)

    out = f'./output_mp4/{filename.replace("h264", "mp4")}'

    cmd = ['ffmpeg', '-i', f'./output/{filename}', '-c:v', 'libx264', '-c:a', 'aac', '-y', out]
    subprocess.call(cmd)
    
    return send_from_directory('static', dest)

@app.route('/video/<filename>')
def test(filename):
    return send_from_directory('static', filename)

# Initial start
if __name__ == '__main__':
    start_camera_init_thread()
    start_servo_init_thread()
    
    app.run(host='0.0.0.0')
