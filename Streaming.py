from threading import Condition
from http import server

import os
import io
import socketserver

# HTML PAGES
# Read HTML content from files
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'main.html'))) as home_file:
    HOME = home_file.read()
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), 'error.html'))) as error_file:
    ERROR = error_file.read()

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
    def __init__(self, request, client_address, server, *args, **kwargs):    
        super().__init__(request, client_address, server, *args, **kwargs)

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True