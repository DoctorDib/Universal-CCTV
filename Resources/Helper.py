from astral import Astral

import datetime as dt
import os

from Resources.Config import Config

class Helper():
    def __init__(self, config: Config):
        self.config = config
        self.geo = Astral().geocoder
        Astral().solar_depression = self.config.get('solar_depression')
        self.city = Astral()[self.config.get('location')]

    def checkSun(self, selection):
        oldSelection = selection
        currentDate = dt.datetime.today().strftime('%Y %m %d').split()

        s = dt.datetime.today().strftime('%Y %m %d  %H:%M:%S')
        currentTime = dt.datetime.strptime(s, "%Y %m %d  %H:%M:%S")
        sun = self.city.sun(date=dt.date(int(currentDate[0]), int(currentDate[1]), int(currentDate[2])), local=True)

        sunrise_hour = sun["sunrise"].hour - 1
        sunset_hour = sun["sunset"].hour - 1

        if selection != "night" and ((sunset_hour <= currentTime.hour < 24) or (currentTime.hour <= sunrise_hour)):
            selection = "night"
        elif selection != "day" and (sunrise_hour <= currentTime.hour < sunset_hour):
            selection = "day"

        if selection != oldSelection:
            print(str(currentTime) + "   -   Switching to: " + selection)

        return [selection != oldSelection, selection]  # Don't do anything

    def grabTextMode(self, mode):
        if (mode == 'night'):
            return "Night"
        elif (mode == 'day'):
            return "Day"
        else:
            return "Fail"
    
class FileManager():
    def __init__(self, config: Config):
        self.config = config

    def files_limit_check(self):
        # Removing files if over the limit
        files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
        if len(files) > self.config.drive_settings('max_videos'):
            os.system('rm -rf ' + self.config.build_video_path(files[0]))