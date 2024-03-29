from flask import Flask, jsonify, render_template, send_from_directory, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from os import listdir, getcwd

import threading

from Resources.Info import Info
from Resources.SQLiteManager import SQLiteManager
from Resources.Config import Config

try:
    # Raspberry Pi camera
    from CameraModules.CameraPi import Camera
    from Resources.Servo import Servo
    servo_thread : Servo = Servo(11)
except:
    # Anything else that's not a Raspberry Pi Camera
    from CameraModules.CameraCv import Camera
    servo_thread = None

camera_thread : Camera = Camera()

app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

react_folder = 'Client'
directory= f'{getcwd()}/{react_folder}/build/static'

def start_camera_init_thread(info_instance, config_instance, sqlite_manager_instance):
    global camera_init_thread
    camera_init_thread = threading.Thread(target=camera_thread.init_thread, args=(info_instance, config_instance, sqlite_manager_instance))
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
    success = False#camera_thread.is_running
    return response(success, "Alive and beating" if success else "Dead")

## CAMERA API

@app.get('/toggle/stream')
def toggle_stream():
    camera_thread.toggle_streaming()
    emit('is_streaming', info.is_streaming, broadcast=True)
    return response(True, "Camera initialization started")

@app.get('/toggle/recording')
def toggle_recording():
    camera_thread.toggle_recording()
    emit('is_recording', info.is_recording, broadcast=True)
    return response(True, "Camera has stopped")

@app.get('/restart')
def restart_camera():
    # stop_camera()
    # sleep(0.5)
    # start_camera()
    return response(True, "Camera restarted")

# SNAPSHOTS

@app.get('/snapshot')
def take_snapshot():
    # Taking a snapshot
    camera_thread.snapshot()
    return response(True, "Snapshot taken")

@app.route('/get/snapshot_list')
def get_snapshot_list():
    files = info.get_snapshot_files()
    return response(True, "Image List", data={ "pictures": files })

@app.route('/get/snapshot/<filename>')
def get_snapshot(filename):
    path = config.snapshot_path()
    name = f"{filename}.{config.snapshot_settings('format')}"
    return send_from_directory(path, name, conditional=True)

@app.route('/delete/snapshot/<uid>')
def delete_snapshot(uid):
    camera_thread.delete_snapshot(uid)
    return response(True, f"Successfully deleted {uid}")

# THUMBNAIL

@app.route('/get/thumbnail/<filename>')
def get_thumbnail(filename):
    # removing the format (I only care about the name)
    path = config.thumbnail_path()
    name = f"{filename}.{config.thumbnail_settings('format')}"
    return send_from_directory(path, name, conditional=True)

@app.route('/get/savedthumbnail/<filename>')
def get_saved_thumbnail(filename):
    # removing the format (I only care about the name)
    path = config.saved_thumbnail_path()
    name = f"{filename}.{config.thumbnail_settings('format')}"
    return send_from_directory(path, name, conditional=True)

## SERVO API

@app.get('/move/<int:percentage>')
def ser_servo(percentage):
    if (servo_thread is None):
        return response(False, "Servo class not active or available")
    
    try:
        servo_thread.move(percentage)
    except Exception as e:
        print(e)
    return response(True, f"Moved to: {percentage}")

@app.get('/get_position')
def get_servo_position():
    if (servo_thread is None):
        return response(False, "Servo class not active or available")
    
    return response(True, data={ "position": servo_thread.current_position })

@app.get('/get_percentage')
def get_servo_position_percentage():
    if (servo_thread is None):
        return response(False, "Servo class not active or available")
    
    return response(True, data={ "position": servo_thread.percentage })

## FILE MANAGER API

@app.get('/get_files')
def get_files():
    files = info.get_video_files()
    return response(True, data={ "files": files })

@app.get('/get_saved_files')
def get_saved_files():
    files = info.get_saved_video_files()
    return response(True, data={ "files": files })

@app.route('/videos')
def videos_page():
    output_directory = config.video_path()
    file_list = listdir(output_directory)
    # return True
    return render_template('./main.html', files=file_list)

@app.route('/savedvideos')
def saved_videos_page():
    output_directory = config.saved_video_path()
    file_list = listdir(output_directory)
    # return True
    return render_template('./main.html', files=file_list)

@app.route('/download/<filename>')
def download_video(filename):
    output_directory = config.video_path()
    return send_from_directory(output_directory, filename, as_attachment=True)

@app.route('/video/<filename>')
def view_video(filename):
    path = config.video_path()
    name = f"{filename}.{config.video_settings('format')}"
    return send_from_directory(path, name, as_attachment=True)

@app.route('/get/disk')
def get_disk_space():
    (total_gb, available_gb) = info.get_disk_space()
    return response(True, data={ "total": total_gb, "availiable": available_gb })
# CLIENT API

@app.route('/')
def index():
    ''' User will call with with thier id to store the symbol as registered'''
    path= getcwd()+ f'/{react_folder}/build'
    print(path)
    return send_from_directory(directory=path,path='index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    path= getcwd()+ f'/{react_folder}/build'
    return send_from_directory(path, filename)
                                                                    
@app.route('/static/<folder>/<file>')
def css(folder,file):
    ''' User will call with with thier id to store the symbol as registered'''
    path = folder + '/' + file
    return send_from_directory(directory=directory,path=path)

# Video feed

@app.route('/video_feed')
def video_feed():
    return camera_thread.flask_stream()

@app.route('/get/resolution')
def get_resolution():
    return config.video_settings('resolution')

@app.route('/get/framerate')
def get_framerate():
    return config.video_settings('framerate')

# SAVE VIDEOS
@app.route('/save/video/<uid>')
def save_video_file(uid):
    sqlite_manager.add_to_favourites(uid)
    info.socketio.emit('welcome_package', info.welcome_package(), namespace='/')
    return response(True)

## WEB SOCKET STUFF
@socketio.on('connect')
def handle_connect():
    info.new_client(request.sid)
    emit("welcome_package", info.welcome_package(), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    info.remove_client(request.sid)
    emit("welcome_package", info.welcome_package(), broadcast=True)

@socketio.on('action')
def handle_custom_event(action):
    print('Received action from client:', action)
    _HANDLE_ACTION(action)

def _HANDLE_ACTION(action: str):
    if action == "toggle_stream":
        toggle_stream()
    elif action == "toggle_recording":
        toggle_recording()
    else:
        # Handle the case when action doesn't match any known values
        print("Unknown action:", action)

# Initial start
if __name__ == '__main__':
    config: Config = Config()
    sqlite_manager: SQLiteManager = SQLiteManager()
    info: Info = Info(socketio, config, sqlite_manager)

    start_camera_init_thread(info, config, sqlite_manager)

    if (config.get('use_servo')):
        start_servo_init_thread()
    
    try:
        socketio.run(app, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("Flask application terminated by user.")
    finally:
        camera_thread.shutdown()
        camera_init_thread.join()
