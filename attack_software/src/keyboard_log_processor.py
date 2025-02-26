import time
import socket
from uuid import getnode as get_mac

class KeyboardLogProcessor:
    def __init__(self):
        self.logs = {}

    def get_computer_info(self):
        mac = get_mac()
        return {
            "computer_name": socket.gethostname(),
            "mac_address": mac
        }

    def process_keylog(self, keylog_str):
        time_stamp = time.strftime("%H:%M:%S")
        computer_info = self.get_computer_info()

        self.logs = {
            "timestamp": time_stamp,
            "computer_name": computer_info["computer_name"],
            "mac_address": computer_info["mac_address"],
            "data": keylog_str
        }

    def get_log(self):
        return self.logs

if __name__ == "__main__":
    processor = KeyboardLogProcessor()
    processor.process_keylog("hello world")
    print(processor.get_log())
