import logging
from pynput import mouse

class MouseTracker:
    def __init__(self):
        self._listener = None
        self._is_tracking = False

    def start_tracking(self):
        if not self._is_tracking:
            self._is_tracking = True
            self._listener = mouse.Listener(on_click=self._on_click, on_scroll=self._on_scroll, on_move=self._on_move)
            self._listener.start()

    def stop_tracking(self):
        if self._is_tracking:
            self._is_tracking = False
            if self._listener:
                self._listener.stop()

    def _on_move(self, x, y):
        logging.info(f"Mouse moved to {x}, {y}")

    def _on_click(self, x, y, button, pressed):
        logging.info(f"Mouse {'pressed' if pressed else 'released'} {button} at {x}, {y}")

    def _on_scroll(self, x, y, dx, dy):
        direction = "up" if dy > 0 else "down"
        logging.info(f"Mouse scrolled {direction} at {x}, {y}")
