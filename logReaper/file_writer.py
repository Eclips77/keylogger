import os
from datetime import datetime
from interface import IWriter

class FileWriter(IWriter):
    def __init__(self, directory="logs"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def send_data(self, data: str, machine_name: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.directory, f"{machine_name}_log_{timestamp}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(data)
