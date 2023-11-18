from Streaming import StreamingHandler, StreamingOutput, StreamingServer

from time import gmtime, strftime
from astral import Astral

import datetime as dt

import json
import time
import threading
import os
import sys

try:
    # Using Raspbery Pi... hopefully
    from picamera import PiCamera
except ImportError:
    # If on Windows, use a substitute library
    from PiCameraStub import PiCameraStub as PiCamera


# Read JSON content from config file
with open(os.path.abspath(os.path.split(sys.argv[0])[0]) + '/config.json') as data_file:
    data = json.load(data_file)

###########################
# SETTINGS
###########################

settings = data["settings"]

max_duration_limit_seconds = data["minutes"] * 60  # Converting to sections

savePath = data["save_path"]
location = data["main_location"]
os.chdir(location + savePath)

currentMode = ""

class Helper():
    def __init__(self):
        self.geo = Astral().geocoder
        Astral().solar_depression = data["solar_depression"]
        self.city = Astral()[data["location"]]

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
    def files_limit_check(self):
        # Removing files if over the limit
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
        if len(files) > data["max_videos"]:
            os.system('rm -rf ' + data["main_location"] + data["save_path"] + '/' + files[0])

class Camera():
    should_tick = False
    settingSelection = ""
    is_running = True

    def __init__(self, fixed_mode = False):
        self.fixed_mode = fixed_mode

        self.helper = Helper()
        self.output = StreamingOutput()
        self.file_manager = FileManager()

        self.streaming_handler = StreamingHandler
        self.streaming_handler.output = self.output  # Set output_instance as a class attribute
        self.streaming_handler.is_running = self.is_running  # Set output_instance as a class attribute

        # Camera
        self.camera = PiCamera()
        self.__set_up_camera()
        
    # STEP 1
    def __set_up_camera(self):
        # Selecting the settings
        settingSelection = self.settingSelection.split(" ")
        if (len(settingSelection) >= 2):
            # FIXED MODE - Sticks only to one setting
            self.fixed_mode = True
            self.selected_setting = data["settings"][settingSelection[0]]
        else:
            # NORMAL MODE - Cycles through day time
            resp = self.helper.checkSun(settingSelection[0])
            self.is_new_selection = resp[0]
            self.selection = resp[1]

            self.selected_setting = data["settings"][self.selection]
        
        self.camera.resolution = self.selected_setting["resolution"]
        self.camera.contrast = self.selected_setting["contrast"]
        self.camera.brightness = self.selected_setting["brightness"]
        self.camera.framerate = self.selected_setting["framerate"]
        self.camera.awb_mode = self.selected_setting["awb_mode"]
        self.camera.exposure_mode = self.selected_setting["exposure_mode"]
        self.camera.image_effect = self.selected_setting["image_effect"]

        try:
            self.camera.annotate_background = picamera.Color(data["text_settings"]["background_color"])
            self.camera.annotate_foreground = picamera.Color(data["text_settings"]["text_color"])
        except:
            # On Windows 
            print("Using windows machine, PiCamera module not avaliable")

        self.camera.annotate_text_size = data["text_settings"]["text_size"]

    # STEP 2
    def initialise_camera(self):
        version = data["version"]
        print(f"Initialising {version}")

        self.is_running = True

        self.__start_recording()
        self.__start_web_server()

        # Tick away for ever
        while(self.is_running):
            # Only tick if active
            if (self.should_tick):
                self.__tick()

    def shutdown(self):
        self.__stop_recording()

    # STEP 3
    def __start_recording(self):
        timeStamp = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

        self.camera.start_recording(timeStamp + ".h264") # it was h264]
        if self.is_new_selection and not self.fixed_mode:
            self.camera.start_recording(self.output, format='mjpeg', splitter_port=2)

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
            self.server = StreamingServer((data["ip"], data["port"]), self.streaming_handler)
            self.server.serve_forever()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the server.")
            self._kill()
        finally:
            self.__stop_recording()

    # STEP 5.1
    def __stop_recording(self):
        self.is_running = False
        self.should_tick = False
        self.camera.stop_recording()
        if self.is_new_selection and not self.fixed_mode:
            self.camera.stop_recording(splitter_port=2)

    # STEP 5
    def __tick(self):
        try:
            # Ensure we have not hit the file limit        
            self.file_manager.files_limit_check()
            # Setting timer text        
            self.camera.annotate_text = self.helper.grabTextMode(self.selection) + " - " + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # camera timeout
            self.camera.wait_recording(0.1)

            current_duration = int(dt.datetime.now().timestamp() * 1000)

            if (current_duration - self.start_duration) > (max_duration_limit_seconds * 1000):
                self.__stop_recording()
                self.__set_up_camera()
                # Giving it time to catch up and set up camera
                time.sleep(1)
                self.__start_recording()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the camera and exiting.")
            self._kill()

    def _kill(self):
        self.__stop_recording()
        self.is_running = False
        self.should_tick = False
        os._exit(0)
