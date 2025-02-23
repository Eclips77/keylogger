import psutil
import time
import logging

class ActiveWindowTracker:
    def __init__(self):
        self.last_app = None

    def track_active_window(self):
        while True:
            active_app = self._get_active_window()
            if active_app != self.last_app:
                logging.info(f"Active window changed: {active_app}")
                self.last_app = active_app
            time.sleep(1)

    def _get_active_window(self):
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            try:
                return proc.info['name']
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return "Unknown"
