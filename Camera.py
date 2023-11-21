from Config import Config
from Streaming import StreamingHandler, StreamingOutput, StreamingServer
from flask import Response

from time import gmtime, strftime, sleep
from astral import Astral

import datetime as dt
import threading
import os

try:
    # Using Raspbery Pi... hopefully
    from picamera import PiCamera
    import picamera as pc
except ImportError:
    print("IMPORT ERROR, NOT BEING RAN ON RASPBERRY PI")
    # If on Windows, use a substitute library
    from PiCameraStub import PiCameraStub as PiCamera

###########################
# SETTINGS
###########################

# max_duration_limit_seconds = data["minutes"] * 60  # Converting to sections

# os.chdir(location + savePath)

currentMode = ""

class Helper():
    def __init__(self):
        self.config = Config()
        self.geo = Astral().geocoder
        Astral().solar_depression = self.config.get('solar_depression')
        self.city = Astral()[self.config.get('location')]

    def checkSun(self, selection):
        oldSelection = selection
        currentDate = dt.datetime.today().strftime('%Y %m %d').split()

        s = dt.datetime.today().strftime('%Y %m %d  %H:%M:%S')
        currentTime = dt.datetime.strptime(s, "%Y %m %d  %H:%M:%S")
        sun = self.city.sun(date=dt.date(int(currentDate[0]), int(currentDate[1]), int(currentDate[2])), local=True)

        sunrise_hour = sun["sunrise"].hour - 1
        sunset_hour = sun["sunset"].hour - 1

        if selection != "night" and ((sunset_hour <= currentTime.hour < 24) or (currentTime.hour <= sunrise_hour)):
            selection = "night"
        elif selection != "day" and (sunrise_hour <= currentTime.hour < sunset_hour):
            selection = "day"

        if selection != oldSelection:
            print(str(currentTime) + "   -   Switching to: " + selection)

        return [selection != oldSelection, selection]  # Don't do anything

    def grabTextMode(self, mode):
        if (mode == 'night'):
            return "Night"
        elif (mode == 'day'):
            return "Day"
        else:
            return "Fail"
    
class FileManager():
    def __init__(self):
        self.config = Config()

    def files_limit_check(self):
        # Removing files if over the limit
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
        if len(files) > self.config.drive_settings('max_videos'):
            os.system('rm -rf ' + self.config.build_video_path(files[0]))

class Camera():
    should_tick = False
    settingSelection = ""
    is_running = True

    def generate_frames(self):
        while self.is_running:
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame
            yield (b'--FRAME\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    def flask_stream(self):
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=FRAME')

    def __init__(self, fixed_mode = False):
        self.fixed_mode = fixed_mode

        self.config = Config()
        self.helper = Helper()
        self.output = StreamingOutput()
        self.file_manager = FileManager()

        # Create video folder if it does not exist
        self.config.create_directory(self.config.video_path())
        # Create snapshop folder if it does not exist
        self.config.create_directory(self.config.snapshot_path())
        # Create thumbnail folder if it does not exist
        self.config.create_directory(self.config.thumbnail_path())

        self.streaming_handler = StreamingHandler
        self.streaming_handler.output = self.output  # Set output_instance as a class attribute
        self.streaming_handler.is_running = self.is_running  # Set output_instance as a class attribute

        # Camera
        self.camera = PiCamera()
        self.__set_up_camera()
        self.__start_web_server()
        
    # STEP 1
    def __set_up_camera(self):
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
        
        self.camera.resolution = self.selected_setting["resolution"]
        self.camera.framerate = self.selected_setting["framerate"]
        self.camera.awb_mode = self.selected_setting["awb_mode"]
        self.camera.exposure_mode = self.selected_setting["exposure_mode"]
        self.camera.brightness = self.selected_setting["brightness"]
        self.camera.contrast = self.selected_setting["contrast"]
        self.camera.saturation = self.selected_setting["saturation"]
        self.camera.sharpness = self.selected_setting["sharpness"]
        self.camera.image_effect = self.selected_setting["image_effect"]
        self.camera.iso = self.selected_setting["iso"]
        self.camera.meter_mode = self.selected_setting["meter_mode"]
        self.camera.video_stabilization = self.selected_setting["video_stabilization"]
        self.camera.sensor_mode = self.selected_setting["sensor_mode"]
        self.camera.rotation = self.selected_setting["rotation"]

        try:
            self.camera.annotate_background = pc.Color(self.config.text_settings("background_color"))
            self.camera.annotate_foreground = pc.Color(self.config.text_settings("text_color"))
        except Exception as e:
            # On Windows 
            print("ERROR: Using windows machine, PiCamera module not avaliable")
            print(f"More Info: {e}")

        self.camera.annotate_text_size =self.config.text_settings("text_size")

    # STEP 2
    def initialise_camera(self):
        version = self.config.get('version')
        print(f"Initialising {version}")

        self.is_running = True

        self.__start_recording()
        
        # Tick away for ever
        while(self.is_running):
            # Only tick if active
            if (self.should_tick):
                self.__tick()

    def shutdown(self):
        self.__stop_recording()

    def restart(self):
        self.__stop_recording()
        sleep(.5) # Waiting for camera to fully shutdown
        self.__set_up_camera()
        # Giving it time to catch up and set up camera
        sleep(.5)
        self.initialise_camera()

    def snapshot(self, name: str = None, is_thumbnail: bool = False):
        time_stamp = self.__get_timestamp()
        name = time_stamp if name is None else name

        if (is_thumbnail):
            snapshot_format = self.config.thumbnail_settings('format')
            path = self.config.build_thumbnail_path(f"{name}.{snapshot_format}")
        else:
            snapshot_format = self.config.snapshot_settings('format')
            path = self.config.build_snapshot_path(f"{name}.{snapshot_format}")
            
        self.camera.capture(path)
    
    def delete_snapshot(self, name: str):
        file_path = self.config.snapshot_path(name)
        if os.path.exists(file_path):
            os.remove(file_path)

    # STEP 3
    def __start_recording(self):
        time_stamp = self.__get_timestamp()
        video_format = self.config.video_settings('format')
        video_path = self.config.build_video_path(f"{time_stamp}.{video_format}")
        # Creating a thumbnail for recording
        self.camera.start_recording(video_path)
        self.snapshot(name=time_stamp, is_thumbnail=True)

        if self.is_new_selection and not self.fixed_mode:
            stream_format = self.config.stream_settings('format')
            self.camera.start_recording(self.output, format=stream_format, splitter_port=2)

        self.start_duration = int(dt.datetime.now().timestamp() * 1000)
        # Start should
        self.should_tick = True
    
    # STEP 4
    def __start_web_server(self):
        self.serverThread = threading.Thread(name='runServer', target=self.__run_server)
        self.serverThread.start()
        
    # STEP 4.1
    def __run_server(self):
        try:
            # Pass the StreamingOutput instance to StreamingHandler
            self.server = StreamingServer((self.config.get('ip'), self.config.get('port')), self.streaming_handler)
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the server.")
            self._kill()
        finally:
            self.__stop_recording()

    # STEP 5.1
    def __stop_recording(self):
        self.should_tick = False
        self.is_running = False

        try:
            self.camera.stop_recording()
        except Exception as e:
            print("Error when closing camera on Port 1")
            print(e)
        
        try:
            if self.is_new_selection and not self.fixed_mode:
                self.camera.stop_recording(splitter_port=2)
        except Exception as e:
            print("Error when closing camera on Port 1")
            print(e)

    # STEP 5
    def __tick(self):
        try:
            # Ensure we have not hit the file limit        
            self.file_manager.files_limit_check()
            # Setting timer text        
            self.camera.annotate_text = self.helper.grabTextMode(self.selection) + " - " + self.__get_formatted_time()
            # camera timeout
            self.camera.wait_recording(0.1)

            current_duration = int(dt.datetime.now().timestamp() * 1000)

            if (current_duration - self.start_duration) > ((self.config.video_settings('max_minutes') * 60) * 1000):
                self.restart()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the camera and exiting.")
            self._kill()

    def __get_formatted_time(self):
        return dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    def __get_timestamp(self):
        return strftime("%Y-%m-%d_%H-%M-%S", gmtime())

    def _kill(self):
        self.__stop_recording()
        self.is_running = False
        self.should_tick = False
        os._exit(0)
