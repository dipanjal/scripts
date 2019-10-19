import ctypes
import os
import platform
import random
import re
import time
from enum import Enum
from pathlib import Path

import schedule


class OSTypes(Enum):
    WINDOWS = 'Windows'
    LINUX = 'Linux'


class WallpaperChanger:


    def is_image_file(self, file_abs_path):
        IMAGE_REGEX = "^.+\\.(jpeg|jpg|png)$"
        if os.path.isfile(file_abs_path) and re.search(IMAGE_REGEX, file_abs_path):
            return True
        return False

    def pick_an_image(self, image_abs_dir):
        image_file_abs = os.path.join(image_abs_dir, random.choice(os.listdir(image_abs_dir)))
        while not self.is_image_file(image_file_abs):
            image_file_abs = os.path.join(image_abs_dir, random.choice(os.listdir(image_abs_dir)))
        return image_file_abs

    def change_wallpaper_from_queue(self, image_abs_dir):
        # image_abs_path = image_queue.pop()
        image_name = self.pick_an_image(image_abs_dir)
        image_abs_path = os.path.join(image_abs_dir, image_name)
        if platform.system() == OSTypes.LINUX.value:
            gnome_command = "/usr/bin/gsettings set org.gnome.desktop.background picture-uri " + image_abs_path
            os.system(gnome_command)
        elif platform.system() == OSTypes.WINDOWS.name:
            SPI_SETDESKWALLPAPER = 20
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_abs_path, 0)

    def __init__(self):
        image_dir = "downloads/@Dreadnaught/"
        image_abs_dir = str(Path(image_dir).expanduser().absolute())
        # only_image_files = [os.path.join(image_abs_dir, f) for f in os.listdir(image_dir) if
        #                     self.is_image_file(os.path.join(image_abs_dir, f))]
        # image_queue = collections.deque(only_image_files)
        # schedule.every(10).seconds.do(self.change_wallpaper_from_queue, image_queue)
        self.change_wallpaper_from_queue(image_abs_dir)
        schedule.every(10).seconds.do(self.change_wallpaper_from_queue, image_abs_dir)
        while True:
            schedule.run_pending()
            time.sleep(1)

        # self.change_wallpaper_from_queue(image_abs_dir)


WallpaperChanger()
