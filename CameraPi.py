from CameraBase import CameraBase
from Streaming import StreamingServer
from flask import Response

from time import sleep

import datetime as dt
import threading

from picamera import PiCamera
import picamera as pc

###########################
# SETTINGS
###########################

# max_duration_limit_seconds = data["minutes"] * 60  # Converting to sections

# os.chdir(location + savePath)

currentMode = ""

class Camera(CameraBase):
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
        ## Camera set up
        self.camera = PiCamera()

        super().__init__(fixed_mode)

        self._set_up_camera()
        self._start_web_server()
        
    # STEP 1
    def _set_up_camera(self):
        super()._set_up_camera()
        
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
        super().initialise_camera()
        self._start_recording()
        # Tick away for ever
        while(self.is_running):
            # Only tick if active
            if (self.should_tick):
                self._tick()

    def shutdown(self):
        self._stop_recording()

    def restart(self):
        self._stop_recording()
        sleep(.5) # Waiting for camera to fully shutdown
        self._set_up_camera()
        # Giving it time to catch up and set up camera
        sleep(.5)
        self.initialise_camera()

    def snapshot(self, name: str = None, is_thumbnail: bool = False):
        path = super().snapshot(name, is_thumbnail)
        # Custom Capture method
        self.camera.capture(path)
    
    def delete_snapshot(self, name: str):
        super().delete_snapshot(name)

    # STEP 3
    def _start_recording(self):
        time_stamp = super()._get_timestamp()
        video_format = self.config.video_settings('format')
        video_path = self.config.build_video_path(f"{time_stamp}.{video_format}")
        self.camera.start_recording(video_path)
        
        if self.is_new_selection and not self.fixed_mode:
            stream_format = self.config.stream_settings('format')
            self.camera.start_recording(self.output, format=stream_format, splitter_port=2)

        self.start_duration = int(dt.datetime.now().timestamp() * 1000)
        # Start should
        self.should_tick = True

        # Creating a thumbnail for recording
        self.snapshot(name=time_stamp, is_thumbnail=True)
    
    # STEP 4
    def _start_web_server(self):
        self.serverThread = threading.Thread(name='runServer', target=self._run_server)
        self.serverThread.start()
        
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
    def _stop_recording(self):
        super()._stop_recording()
        
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
    def _tick(self):
        try:     
            super()._tick()

            self.camera.annotate_text = self.helper.grabTextMode(self.selection) + " - " + super()._get_formatted_time()
            # camera timeout
            self.camera.wait_recording(0.1)

            current_duration = int(dt.datetime.now().timestamp() * 1000)

            if (current_duration - self.start_duration) > ((self.config.video_settings('max_minutes') * 60) * 1000):
                self.restart()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the camera and exiting.")
            self._kill()

    def _kill(self):
        self._stop_recording()

        super()._kill()