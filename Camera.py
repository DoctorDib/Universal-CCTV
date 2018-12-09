from fractions import Fraction
from picamera import PiCamera
from threading import Condition
from threading import Thread
from http import server
from time import gmtime, strftime

import datetime as dt

import io
import picamera
import logging
import socketserver
import time
import threading
import os

PAGE = """\
<html>
    <head>
        <title>Camera Surveillance</title>
    </head>
    <body>
        <img src="stream.mjpg" width="640" height="480" />
    </body>
</html>
"""

###########################
######## Settings #########
###########################

exposureSetting = "night"
cameraFrameRate = 5

ip = ""
port = 8000

maxVideos = 48

minutes = 60
seconds = minutes * 60

savePath = "/output"
location = "/home/pi/CameraSurveillance"
os.chdir(location + savePath)


###########################

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class MyOutput(object):
    def __init__(self, filename, sock):
        self.output_file = io.open(filename, 'wb')
        self.output_sock = sock.makefile('wb')

    def write(self, buf):
        self.output_file.write(buf)
        self.output_sock.write(buf)

    def flush(self):
        self.output_file.flush()
        self.output_sock.flush()

    def close(self):
        self.output_file.close()
        self.output_sock.close()


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')

            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def runServer():
    try:
        server = StreamingServer((ip, port), StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()


with picamera.PiCamera(resolution='640x480', framerate=cameraFrameRate) as camera:
    output = StreamingOutput()
    camera.exposure_mode = exposureSetting
    camera.start_recording(output, format='mjpeg', splitter_port=2)

    serverThread = threading.Thread(name='runServer', target=runServer)
    serverThread.start()

    while True:
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)

        if (len(files) > maxVideos):
            os.remove(files[0])  # deleting the oldest

        timeStamp = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

        camera.start_recording(timeStamp + ".h264")

        start = dt.datetime.now()
        startMili = int(dt.datetime.now().strftime("%s")) * 1000
        while True:
            camera.annotate_background = picamera.Color('black')
            camera.annotate_text_size = 20
            camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            camera.wait_recording(0.1)

            currentMili = int(dt.datetime.now().strftime("%s")) * 1000

            if ((currentMili - startMili) > (seconds * 1000)):
                print("Restarting")
                startMili = int(dt.datetime.now().strftime("%s")) * 1000

                timeStamp = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

                camera.stop_recording()
                time.sleep(1)

                camera.start_recording(timeStamp + ".h264")

                camera.annotate_background = picamera.Color('black')
                camera.annotate_text_size = 20
                camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                camera.wait_recording(0.1)
















