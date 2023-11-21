import json
import os
import sys

class Config():

    def __init__(self):
        # Read JSON content from config file
        with open(os.path.abspath(os.path.split(sys.argv[0])[0]) + '/config.json') as data_file:
            self.data = json.load(data_file)

    def get(self, key):
        response = None

        try:
            response = self.data[key]
        except Exception as ex:
            print(f"ERROR: Failed to get '{key}' - {ex}")
        finally:
            return response
        
    def text_settings(self, key):
        base = self.get('text_settings')
        return base[key]
    
    def drive_settings(self, key):
        base = self.get('drive_settings')
        return base[key]
    
    def camera_settings(self, key):
        base = self.get('camera_settings')
        return base[key]
    
    def stream_settings(self, key):
        base = self.get('stream_settings')
        return base[key]
    def video_settings(self, key):
        base = self.get('video_settings')
        return base[key]
    def snapshot_settings(self, key):
        base = self.get('snapshot_settings')
        return base[key]
    def thumbnail_settings(self, key):
        base = self.get('thumbnail_settings')
        return base[key]
    
    ## CUSTOM SPECIFIC
    def video_path(self):
        return os.getcwd() + self.video_settings('location')
    def build_video_path(self, file_name: str):
        return f"{self.video_path()}/{file_name}"

    def snapshot_path(self):
        return os.getcwd() + self.snapshot_settings('location')
    def build_snapshot_path(self, file_name: str):
        return f"{self.snapshot_path()}/{file_name}"

    def thumbnail_path(self):
        return os.getcwd() + self.thumbnail_settings('location')
    def build_thumbnail_path(self, file_name: str):
        return f"{self.thumbnail_path()}/{file_name}"
    
    def create_directory(self, directory_path):
        # Check if the directory already exists
        if not os.path.exists(directory_path):
            # If not, create the directory
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created.")
        else:
            print(f"Directory '{directory_path}' already exists.")
