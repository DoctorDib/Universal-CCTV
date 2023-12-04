import cv2
from flask import Flask, jsonify, render_template, send_from_directory, send_file
from flask_cors import CORS

try:
    # Raspberry Pi camera
    from CameraPi import Camera
except:
    # Anything else that's not a Raspberry Pi Camera
    from CameraCv import Camera
    
from Servo import Servo
from Config import Config

import os
import os.path
import subprocess
import os.path
import psutil
import platform
from time import sleep
import threading
import os

camera_thread : Camera() = Camera()
servo_thread : Servo = Servo(11)

# _ntuple_diskusage = namedtuple('usage', 'total used free')

app = Flask(__name__)
CORS(app)

react_folder = 'Client'
directory= f'{os.getcwd()}/{react_folder}/build/static'

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
        if cv2.waitKey(1) & 0xFF == ord('q'): 
            break
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

    if (Config().get('use_servo')):
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

# SNAPSHOTS

@app.get('/snapshot')
def take_snapshot():
    # Taking a snapshot
    camera_thread.snapshot()
    return response(True, "Snapshot taken")

@app.route('/get/snapshot_list')
def get_snapshot_list():
    path = Config().snapshot_path()
    picture_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join
    (path, f))]
    return response(True, "Image List", data={ "pictures": picture_files })

@app.route('/get/snapshot/<filename>')
def get_snapshot(filename):
    path = Config().snapshot_path()
    return send_from_directory(path, filename, conditional=True)

@app.route('/delete/snapshot/<filename>')
def delete_snapshot(filename):
    camera_thread.delete_snapshot(filename)
    return response(True, f"Successfully deleted {filename}")

# THUMBNAIL

@app.route('/get/thumbnail/<filename>')
def get_thumbnail(filename):
    # removing the format (I only care about the name)
    filename = filename.split('.')[0]
    path = Config().thumbnail_path()
    name = f"{filename}.{Config().thumbnail_settings('format')}"
    return send_from_directory(path, name, conditional=True)

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
    output_directory = Config().video_path()
    file_list = os.listdir(output_directory)
    return response(True, data={ "files": file_list })

@app.route('/videos')
def videos_page():
    output_directory = Config().video_path()
    file_list = os.listdir(output_directory)
    # return True
    return render_template('./main.html', files=file_list)

@app.route('/download/<filename>')
def download_video(filename):
    output_directory = Config().video_path()
    return send_from_directory(output_directory, filename, as_attachment=True)

@app.route('/video/<filename>')
def view_video(filename):
    output_directory = Config().video_path()
    return send_from_directory(output_directory, filename, as_attachment=True)

@app.route('/get/disk')
def get_disk_space():
    system_platform = platform.system()

    if system_platform == 'Windows':
        partitions = psutil.disk_partitions()
        for partition in partitions:
            if 'fixed' in partition.opts.lower():
                disk_usage = psutil.disk_usage(partition.mountpoint)
                total_space = disk_usage.total
                available_space = disk_usage.free
                break
    elif system_platform == 'Linux':
        disk_usage = psutil.disk_usage('/')
        total_space = disk_usage.total
        available_space = disk_usage.free
    else:
        print(f"Unsupported platform: {system_platform}")
        return response(False, f"Unsupported platform to grab disk space: {system_platform}")

    total_gb = total_space / (1024 ** 3)
    available_gb = available_space / (1024 ** 3)

    return response(True, data={ "total": total_gb, "availiable": available_gb })
# CLIENT API

@app.route('/')
def index():
    ''' User will call with with thier id to store the symbol as registered'''
    path= os.getcwd()+ f'/{react_folder}/build'
    print(path)
    return send_from_directory(directory=path,path='index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    path= os.getcwd()+ f'/{react_folder}/build'
    return send_from_directory(path, filename)

@app.route('/static/<folder>/<file>')
def css(folder,file):
    ''' User will call with with thier id to store the symbol as registered'''
    
    path = folder+'/'+file
    return send_from_directory(directory=directory,path=path)

# Video feed

@app.route('/video_feed')
def video_feed():
    return camera_thread.flask_stream()

# @app.route('/video/<filename>')
# def test(filename):
#     return send_from_directory('static', filename)

# Initial start
if __name__ == '__main__':
    start_camera_init_thread()

    if (Config().get('use_servo')):
        start_servo_init_thread()
    
    app.run(host='0.0.0.0')
