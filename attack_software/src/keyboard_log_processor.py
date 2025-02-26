import time
import socket
from uuid import getnode as get_mac

class KeyboardLogProcessor:

    def get_computer_info(self):
        mac = get_mac()
        computer_name = socket.gethostname()
        return {
            "computer_name": f"{computer_name} - {mac}"

        }

    def process_keylog(self, keylog_str):
        time_stamp = time.strftime("%H:%M:%S")
        computer_info = self.get_computer_info()

        return ({
            "timestamp": time_stamp,
            "computer_name": computer_info["computer_name"],
            "data": keylog_str
        })


if __name__ == "__main__":
    processor = KeyboardLogProcessor()
    print(processor.process_keylog("hello world"))
