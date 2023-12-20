import threading
import os
import psutil
import platform

from Config import Config
from flask_socketio import SocketIO, emit


class Info():
    config: Config
    clients : list[str] = []
    camera_running : bool = False
    is_recording : bool = False
    is_streaming : bool = False
    servo_position: float = 0
    storage_used: float = 0
    video_files: list[str] = []
    snapshot_files: list[str] = []
    lock: threading.Lock 
    control_lock_state: bool = False

    def __init__(self, socketio):
        self.value = 0
        self.lock = threading.Lock()
        self.socketio: SocketIO = socketio

    def welcome_package(self):
        return {
            "is_recording": self.is_recording,
            "is_streaming": self.is_streaming,
            "clients_count": len(self.clients),
            "servo_position": self.servo_position,
            "storage_used": self.storage_used,
            "video_files": self.get_video_files(),
            "snapshot_files": self.get_snapshot_files(),
            "saved_video_files": self.get_saved_video_files(),
            "control_lock_state": self.control_lock_state,
        }
    
    def lock_controls(self):
        self.control_lock_state = True
        self.socketio.emit('control_lock_state', self.control_lock_state, namespace='/')
    
    def unlock_controls(self):
        self.control_lock_state = False
        self.socketio.emit('control_lock_state', self.control_lock_state, namespace='/')
    
    def new_client(self, id: str):
        self.clients.append(id)
    def remove_client(self, id: str):
        self.clients.remove(id)

    def get_video_files(self):
        output_directory = Config().video_path()
        video_files = os.listdir(output_directory)
        self.socketio.emit('video_files', video_files, namespace='/')
        return video_files

    def get_snapshot_files(self):
        path = Config().snapshot_path()
        snapshot_files = [f for f in os.listdir(path) if os.path.isfile(os.path.join
        (path, f))]
        self.socketio.emit('snapshot_files', snapshot_files, namespace='/')
        return snapshot_files

    def get_saved_video_files(self):
        output_directory = Config().saved_video_path()
        video_files = os.listdir(output_directory)
        self.socketio.emit('saved_video_files', video_files, namespace='/')
        return video_files
    
    def get_disk_space(self):
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
            return False

        total_gb = total_space / (1024 ** 3)
        available_gb = available_space / (1024 ** 3)

        self.storage_used = available_gb
        
        self.socketio.emit('storage_used', self.storage_used, namespace='/')

        return (total_gb, available_gb)

