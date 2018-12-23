from fractions import Fraction
from picamera import PiCamera
from threading import Condition
from threading import Thread
from http import server
from time import gmtime, strftime
from astral import Astral

import datetime as dt

import json
import astral
import io
import picamera
import logging
import socketserver
import time
import threading
import os

###########################
# PAGES
###########################

HOME = """\
<html>
    <head>
        <link rel="icon" href="/home/pi/CameraSurveillance/pic/webcam.png">
        <title>Camera Surveillance</title>
    </head>
    <body>
        <img src="stream.mjpg" />
    </body>
</html>
"""

ERROR = """\
<html>
    <head>
        <link rel="icon" href="/home/pi/CameraSurveillance/pic/webcam.png">
        <title>Nice try...</title>
    </head>
    <body>
        <h1> Well you tried, I guess...</h1>
    </body>
</html>
"""

###########################
# SETTINGS
###########################

with open('/home/pi/CameraSurveillance/config.json') as data_file:
    data = json.load(data_file)

ip = data["ip"]
port = data["port"]
maxVideos = data["max_videos"]
settings = data["settings"]
minutes = data["minutes"]
seconds = minutes * 60  # Converting to sections

settingSelection = "night -x"

savePath = data["save_path"]
location = data["main_location"]
os.chdir(location + savePath)

###########################
# ASTRAL SETUP
###########################

geo = Astral().geocoder
Astral().solar_depression = data["solar_depression"]
city = Astral()[data["location"]]

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


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = HOME.encode('utf-8')
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
            content = ERROR.encode('utf-8')
            self.send_response(404)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


def runServer():
    try:
        server = StreamingServer((ip, port), StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()


def checkSun(selection):
    oldSelection = selection
    currentDate = dt.datetime.today().strftime('%Y %m %d').split()

    s = dt.datetime.today().strftime('%Y %m %d  %H:%M:%S')
    currentTime = dt.datetime.strptime(s, "%Y %m %d  %H:%M:%S")
    sun = city.sun(date=dt.date(int(currentDate[0]), int(currentDate[1]), int(currentDate[2])), local=True)
    # Currently disabled due to high sun exposure..
    if selection != "night" and (sun["sunset"].hour < currentTime.hour < 24) or (currentTime.hour < sun["sunrise"].hour):
        selection = "night"

    elif selection != "morning" and sun["sunrise"].hour < currentTime.hour < 12:
        selection = "morning"

    elif selection != "afternoon" and 12 <= currentTime.hour < sun["sunset"].hour:
        selection = "afternoon"

    if selection != oldSelection:
        print(str(currentTime) + "   -   Switching to: " + selection)
    return [selection != oldSelection, selection]  # Don't do anything


with picamera.PiCamera() as camera:
    fixedMode = False

    output = StreamingOutput()

    settingSelection = settingSelection.split(" ")
    if(len(settingSelection) >= 2):
        # FIXED MODE - Sticks only to one setting
        fixedMode = True
        selectedSetting = settings[settingSelection[0]]
    else:
        # NORMAL MODE - Cycles through day time
        resp = checkSun(settingSelection[0])
        selectedSetting = settings[resp[1]]


    camera.resolution = selectedSetting["resolution"]
    camera.contrast = selectedSetting["contrast"]
    camera.brightness = selectedSetting["brightness"]
    camera.framerate = selectedSetting["framerate"]
    camera.awb_mode = selectedSetting["awb_mode"]
    camera.exposure_mode = selectedSetting["exposure_mode"]
    camera.image_effect = selectedSetting["image_effect"]

    camera.start_recording(output, format='mjpeg', splitter_port=2)
    serverThread = threading.Thread(name='runServer', target=runServer)
    serverThread.start()

    timeStamp = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

    camera.start_recording(timeStamp + ".h264")

    start = dt.datetime.now()
    startMili = int(dt.datetime.now().strftime("%s")) * 1000
    while True:
        # Removing files if over the limit
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
        if len(files) > maxVideos:
            os.system('rm -rf /home/pi/CameraSurveillance/output/' + files[0])

        camera.annotate_background = picamera.Color(data["text_settings"]["background_color"])
        camera.annotate_foreground = picamera.Color(data["text_settings"]["text_color"])
        camera.annotate_text_size = data["text_settings"]["text_size"]
        camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        camera.wait_recording(0.1)

        currentMili = int(dt.datetime.now().strftime("%s")) * 1000

        if (currentMili - startMili) > (seconds * 1000):
            camera.stop_recording()
            resp = checkSun(selectedSetting)
            if resp[0] and not fixedMode:
                print("Restarting")
                startMili = int(dt.datetime.now().strftime("%s")) * 1000
                timeStamp = strftime("%Y-%m-%d_%H-%M-%S", gmtime())

                camera.stop_recording(splitter_port=2)

                selectedSetting = settings[resp[1]]
                camera.resolution = selectedSetting["resolution"]
                camera.contrast = selectedSetting["contrast"]
                camera.brightness = selectedSetting["brightness"]
                camera.framerate = selectedSetting["framerate"]
                camera.awb_mode = selectedSetting["awb_mode"]
                camera.exposure_mode = selectedSetting["exposure_mode"]
                camera.image_effect = selectedSetting["image_effect"]

            time.sleep(1)

            camera.start_recording(timeStamp + ".h264")
            if resp[0] and not fixedMode:
                camera.start_recording(output, format='mjpeg', splitter_port=2)

            camera.annotate_background = picamera.Color(data["text_settings"]["background_color"])
            camera.annotate_foreground = picamera.Color(data["text_settings"]["text_color"])
            camera.annotate_text_size = data["text_settings"]["text_size"]
            camera.annotate_text = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            camera.wait_recording(0.1)
