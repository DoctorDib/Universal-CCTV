import datetime as dt
import threading
import cv2 
import logging

from time import sleep

from flask import Response

from CameraBase import CameraBase
from Streaming import StreamingServer
from Info import Info

currentMode = ""

class Camera(CameraBase):
    def generate_frames(self):
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break   
            with self.output.condition:
                self.output.condition.wait()
                frame = self.output.frame
            yield (b'--FRAME\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            
    def flask_stream(self):
        return Response(self.generate_frames(), mimetype='multipart/x-mixed-replace; boundary=FRAME')

    def __init__(self, fixed_mode = False):
        super().__init__(fixed_mode)

        self._set_up_camera()
        self._start_web_server()

    def toggle_recording(self):
        super().toggle_recording()
        if (self.info.is_recording):
            self._start_recording()
        else:
            self._stop_recording()

        self._check_should_tick_status()

    def toggle_streaming(self):
        super().toggle_streaming()        
        self._check_should_tick_status()

    def _check_should_tick_status(self):
        super()._check_should_tick_status()
        if (self.should_tick is False and (self.info.is_recording or self.info.is_streaming)):
            self.should_tick = True
            self.initialise_camera(self.info)
        elif (self.should_tick is True and (not self.info.is_recording and not self.info.is_streaming)):
            self.should_tick = False

    # STEP 1
    def _set_up_camera(self):
        # Potential custom code?
        super()._set_up_camera()

    # STEP 2
    def initialise_camera(self, info):
        super().initialise_camera(info)

        info.lock_controls()

        # Preparing the camera to be used once again
        source = self.config.video_settings('source')
        self.camera = cv2.VideoCapture(source) # TODO Change here

        resolution = self.config.get_resolution()
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

        # Waiting for camera to initialise
        sleep(2)
        
        self.info = info

        if (self.info.control_lock_state):
            self.info.unlock_controls()

        # Tick away for ever
        while(self.should_tick):
            self._tick()
        
    def shutdown(self):
        self.info.is_recording = False
        self.info.is_streaming = False
        self.should_tick = False

        self.server.shutdown()
        self.serverThread.join()

        self._stop_recording()

    def restart(self):
        if (self.info.is_recording):
            self._stop_recording()

        self.clock.reset()
        sleep(.5) # Waiting for camera to fully shutdown
        self._set_up_camera()
        # Giving it time to catch up and set up camera
        sleep(.5)
        self.initialise_camera(self.info)

    def snapshot(self, name: str = None, is_thumbnail: bool = False):
        path = super().snapshot(name, is_thumbnail)
        frame = self.get_frame()
        if (frame is None):
            return
        cv2.imwrite(path, frame)
        self.info.get_snapshot_files()
    
    def delete_snapshot(self, name: str):
        super().delete_snapshot(name)
        self.info.get_snapshot_files()

    # STEP 3
    def _start_recording(self):
        time_stamp = super()._get_timestamp()
        self.start_duration = int(dt.datetime.now().timestamp() * 1000)

        # Getting video settings
        video_format = self.config.video_settings('cv_format')
        framerate = self.config.video_settings('framerate')
        codec = self.config.video_settings('codec')
        
        resolution = self.config.get_resolution()
        resolution_input = (resolution[0], resolution[1])

        self.fourcc = cv2.VideoWriter_fourcc(*codec)
        video_path = self.config.build_video_path(f"{time_stamp}.{video_format}")
        
        self.out = cv2.VideoWriter(video_path, self.fourcc, framerate, resolution_input)  
        
        with self.info.lock:
            self.info.get_video_files()
            
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
            if self.out is not None:
                logging.info("Releasing self.out")
                self.out.release()

            if self.camera is not None:
                logging.info("Releasing self.camera")
                self.camera.release()

            with self.info.lock:
                self.info.get_video_files()

        except cv2.error as e:
            logging.error("Error when closing camera on Port 1")
            logging.error(e)

        except Exception as e:
            logging.error("An unexpected error occurred:")
            logging.error(e)

    # STEP 5
    def _tick(self):
        try:            
            super()._tick()
            
            cv2.waitKey(1)

            frame = self.get_frame()

            if (frame is None):
                return

            # Saving recording
            if (self.info.is_recording):
                self.out.write(frame)

            # Streaming
            if (self.info.is_streaming):
                format = self.config.stream_settings('cv_format')
                _, encoded_frame = cv2.imencode(f'.{format}', frame)
                self.output.write(encoded_frame)

            if (self.clock.check_bounds(self.config.video_settings('max_minutes'))):
                self.restart()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the camera and exiting.")
            self._kill()

    def get_frame (self):
        if (not self.info.is_streaming and not self.info.is_recording):
            return

        _, frame = self.camera.read()

        if (frame is None):
            return None
        
        # Rotate image
        rotation = self.config.video_settings('rotation')
        if (rotation == 90):
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif(rotation == 180):
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif (rotation == 270):
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)

        # Get the height and width of the frame
        height, width, _ = frame.shape

        # Define the dimensions of the black bar
        bar_height = int(height / 20)  # You can adjust the height as needed
        bar_color = (0, 0, 0)  # Black color

        # Create a black bar at the top middle of the frame
        frame[0:bar_height, :] = bar_color

        font_scale = .5
        font_thickness = 1

        # Add text to the black bar
        text = super()._get_formatted_time()
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(text, font, font_scale, font_thickness)[0]
        text_x = int((width - text_size[0]) / 2)
        text_y = int(bar_height / 2) + int(text_size[1] / 2)
        cv2.putText(frame, text, (text_x, text_y), font, font_scale, (255, 255, 255), font_thickness, cv2.LINE_AA)

        return frame

    def _kill(self):
        self._stop_recording()
        super()._kill()