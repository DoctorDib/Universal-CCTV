from threading import Condition
from http import server

import io
import socketserver
import numpy as np

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if isinstance(buf, np.ndarray):
            buf = buf.tobytes()

        is_jpeg = buf.startswith(b'\xff\xd8')
        is_h264 = buf.startswith(b'\x00\x00\x00\x01')
        is_mjpeg = buf.startswith(b'\xFF\xD8') and b'\xFF\xD9' in buf

        if is_jpeg or is_h264 or is_mjpeg:
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)

        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server, *args, **kwargs):    
        super().__init__(request, client_address, server, *args, **kwargs)

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True