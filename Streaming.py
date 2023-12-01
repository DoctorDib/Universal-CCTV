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
            # If buf is a NumPy array, convert it to bytes
            buf = buf.tobytes()

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
    def __init__(self, request, client_address, server, *args, **kwargs):    
        super().__init__(request, client_address, server, *args, **kwargs)

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True