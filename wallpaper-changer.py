import ctypes
import os
import re
import collections
import schedule
import time

from pathlib import Path


class WallpaperChanger:

    def is_image_file(self, file_path):
        IMAGE_REGEX = "^.+\\.(jpeg|jpg|png)$"
        if os.path.isfile(file_path) and re.search(IMAGE_REGEX, file_path):
            return True
        return False

    def change_wallpaper_from_queue(self, image_queue):
        image_abs_path = image_queue.pop()
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, image_abs_path, 0)

    def __init__(self):
        image_dir = "downloads/@Dreadnaught/"
        image_abs_dir = str(Path(image_dir).expanduser().absolute())
        only_image_files = [os.path.join(image_abs_dir, f) for f in os.listdir(image_dir) if
                            self.is_image_file(os.path.join(image_abs_dir, f))]
        image_queue = collections.deque(only_image_files)
        schedule.every(10).seconds.do(self.change_wallpaper_from_queue, image_queue)
        while True:
            schedule.run_pending()
            time.sleep(1)


WallpaperChanger()
