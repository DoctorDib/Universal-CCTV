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
        
    ## CUSTOM SPECIFIC
    def get_output_path(self):
        main_directory = self.get('main_location')
        save_path = self.get('save_path')
        return main_directory + save_path