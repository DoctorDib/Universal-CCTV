from time import gmtime, strftime

import os
import threading
import datetime as dt

from Resources.Clock import Clock
from Resources.Config import Config
from Resources.Helper import FileManager, Helper
from Resources.Info import Info
from Resources.SQLiteManager import SQLiteManager
from Resources.Streaming import StreamingHandler, StreamingOutput, StreamingServer

class CameraBase():
    should_tick: bool = False
    settingSelection: str = ""
    
    config: Config
    helper: Helper
    output: StreamingOutput
    file_manager: FileManager
    info: Info
    clock: Clock
    
    def generate_frames(self):
        pass

    def flask_stream(self):
        pass

    def __init__(self, fixed_mode = False):
        self.fixed_mode = fixed_mode

        self.output = StreamingOutput()
        self.clock = Clock()
        self.info = threading.Lock()

        self.streaming_handler = StreamingHandler
        self.streaming_handler.output = self.output  # Set output_instance as a class attribute
        # self.streaming_handler.is_running = self.is_running  # Set output_instance as a class attribute

    # STEP 1
    def _set_up_camera(self):
        # Selecting the settings
        settingSelection = self.settingSelection.split(" ")
        if (len(settingSelection) >= 2):
            # FIXED MODE - Sticks only to one setting
            self.fixed_mode = True
            self.selected_setting = self.config.camera_settings(settingSelection[0])
        else:
            # NORMAL MODE - Cycles through day time
            resp = self.helper.checkSun(settingSelection[0])
            self.is_new_selection = resp[0]
            self.selection = resp[1]
            self.selected_setting = self.config.camera_settings(self.selection)

    # STEP 2
            
    def init_thread(self, info: Info, config: Config, sqlite_manager: SQLiteManager):
        self.info = info
        self.config = config
        self.sqlite_manager = sqlite_manager
        
        self.helper = Helper(self.config)
        self.file_manager = FileManager(self.config)

        version = self.config.get('version')
        print(f"Initialising {version}")

        self._start_web_server()

        self.initialise_camera()
    
    def toggle_recording(self):
        with self.info.lock:
            self.info.is_recording = not self.info.is_recording
            self.info.socketio.emit('is_recording', self.info.is_recording, namespace='/')
        # self._check_should_tick_status()
    def toggle_streaming(self):
        with self.info.lock:
            self.info.is_streaming = not self.info.is_streaming
            self.info.socketio.emit('is_streaming', self.info.is_streaming, namespace='/')
        # self._check_should_tick_status()
    def _check_should_tick_status(self):
        pass

    def initialise_camera(self):
        pass

    def shutdown(self):
        self._stop_recording()

    def restart(self):
        pass

    def snapshot(self, name: str = None, is_thumbnail: bool = False) -> str:
        time_stamp = self._get_timestamp()
        name = time_stamp if name is None else name

        if (is_thumbnail):
            snapshot_format = self.config.thumbnail_settings('format')
            path = self.config.build_thumbnail_path(f"{name}.{snapshot_format}")
        else:
            snapshot_format = self.config.snapshot_settings('format')
            path = self.config.build_snapshot_path(f"{name}.{snapshot_format}")

        # Inserting into database
        self.sqlite_manager.insert_snapshot(name, is_thumbnail, snapshot_format)

        return path
    
    def delete_snapshot(self, uid: int):
        # Getting file name
        file_name = self.sqlite_manager.get_file_name(uid)
        # Deleting entry from database
        self.sqlite_manager.delete_entry(uid)

        file_path = self.config.build_snapshot_path(file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    # STEP 3
    def _start_recording(self):
        pass

    # STEP 4
    def _start_web_server(self):
        pass
        
    # STEP 4.1
    def _run_server(self):
        try:
            # Pass the StreamingOutput instance to StreamingHandler
            self.server = StreamingServer((self.config.get('ip'), self.config.get('port')), self.streaming_handler)
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the server.")
            self._kill()
        finally:
            self._stop_recording()

    # STEP 5.1
    def _start_recording(self):
        self.clock.start()

    def _stop_recording(self):
        self.clock.stop()
        # self.should_tick = False
        # self.is_running = False

    # STEP 5
    def _tick(self):
        self.file_manager.files_limit_check()
        
    def _get_formatted_time(self):
        return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def _get_timestamp(self):
        return strftime("%Y-%m-%d_%H-%M-%S", gmtime())

    def _kill(self):
        # self.is_running = False
        self.should_tick = False
        os._exit(0)
