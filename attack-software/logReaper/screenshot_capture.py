import pyautogui
import os
from datetime import datetime
import logging

class ScreenshotCapture:
    def __init__(self, directory="screenshots"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def take_screenshot(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.directory, f"screenshot_{timestamp}.png")
        pyautogui.screenshot().save(filename)
        logging.info(f"Screenshot saved as {filename}")
