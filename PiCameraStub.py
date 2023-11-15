# Create a PiCameraStub class to use on Windows
class PiCameraStub:
    def __init__(self):
        pass

    def start_recording(self, filename, format=None, splitter_port=None):
        print(f"Recording to {filename} with format {format} on splitter port {splitter_port}")

    def stop_recording(self, splitter_port=None):
        print(f"Stopping recording on splitter port {splitter_port}")

    def annotate_text_size(self, size):
        print(f"Setting annotation text size to {size}")

    def annotate_background(self, color):
        print(f"Setting annotation background color to {color}")

    def annotate_foreground(self, color):
        print(f"Setting annotation foreground color to {color}")

    def wait_recording(self, wait_time):
        pass # I don't want to spam the console