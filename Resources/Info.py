from flask_socketio import SocketIO
from typing import List

import threading
import psutil
import platform

from Resources.Config import Config
from Resources.SQLiteManager import SQLiteManager

class Info():
    config: Config
    clients : List[str] = []
    camera_running : bool = False
    is_recording : bool = False
    is_streaming : bool = False
    servo_position: float = 0
    storage_used: float = 0
    video_files: List[str] = []
    snapshot_files: List[str] = []
    lock: threading.Lock 
    control_lock_state: bool = False
    is_windows: bool = False

    def __init__(self, socketio, config: Config, sqlite_manager: SQLiteManager):
        system_platform = platform.system()

        self.value = 0
        self.config = config
        self.sqlite_manager = sqlite_manager
        self.lock = threading.Lock()
        self.socketio: SocketIO = socketio
        self.is_windows = system_platform == "Windows"

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
        video_format = self.config.video_settings('cv_format' if self.is_windows else 'pi_format')
        video_files = self.sqlite_manager.get_entries(video_format, is_favourite=False)
        self.socketio.emit('video_files', video_files, namespace='/')
        return video_files

    def get_snapshot_files(self):
        snapshot_format = self.config.snapshot_settings('format')
        snapshot_files = self.sqlite_manager.get_entries(snapshot_format, is_favourite=False)
        self.socketio.emit('snapshot_files', snapshot_files, namespace='/')
        return snapshot_files

    def get_saved_video_files(self):
        video_format = self.config.video_settings('cv_format' if self.is_windows else 'pi_format')
        video_files = self.sqlite_manager.get_entries(video_format, is_favourite=True)
        self.socketio.emit('saved_video_files', video_files, namespace='/')
        return video_files
    
    def get_disk_space(self):
        system_platform = platform.system()

        if self.is_windows:
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

