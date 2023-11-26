from CameraBase import CameraBase
from Streaming import StreamingServer
from flask import Response

from time import sleep

import datetime as dt
import threading
import cv2 

currentMode = ""

class Camera(CameraBase):
    test: super

    def generate_frames(self):
        while self.is_running:
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
        # Camera
        self.camera = cv2.VideoCapture(0) # TODO Change here 

        self.test = super()

        super().__init__(fixed_mode)

        self._set_up_camera()
        self._start_web_server()
        
    # STEP 1
    def _set_up_camera(self):
        # Potential custom code?
        super()._set_up_camera()

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
        # TODO - Add custom snap shot capture
    
    def delete_snapshot(self, name: str):
        super().delete_snapshot(name)

    # STEP 3
    def _start_recording(self):
        self.start_duration = int(dt.datetime.now().timestamp() * 1000)
        self.should_tick = True
        # Creating a thumbnail for recording
        # self.snapshot(name=time_stamp, is_thumbnail=True)
    
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
            self.camera.stop()
            self.camera.stream.release()
        except Exception as e:
            print("Error when closing camera on Port 1")
            print(e)

    # STEP 5
    def _tick(self):
        try:
            super()._tick()
            cv2.waitKey(1)

            self.get_frame()

            current_duration = int(dt.datetime.now().timestamp() * 1000)

            if (current_duration - self.start_duration) > ((self.config.video_settings('max_minutes') * 60) * 1000):
                self.restart()
        except KeyboardInterrupt:
            print("KeyboardInterrupt: Stopping the camera and exiting.")
            self._kill()

    def get_frame (self):
        _, frame = self.camera.read()
        
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

        format = self.config.stream_settings('format')
        _, encoded_frame = cv2.imencode(f'.{format}', frame)

        self.output.write(encoded_frame)

    def _kill(self):
        self._stop_recording()
        super()._kill()