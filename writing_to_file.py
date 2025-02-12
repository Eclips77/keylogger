from datetime import datetime
import json
import os
from iwriter import IWriter


class FileWriter(IWriter):

    def send_data(self,data: str, machine_name: str) -> None:
        """
        This function receives a string of data and a file name (machine_name).
        It takes the current time and stores it as a key in a dictionary,
        where the value is the received data.
        If the file exists, it loads the existing data; otherwise, it creates a new dictionary.
        The data is then saved into a JSON file with proper formatting.
        """

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if os.path.exists(machine_name):
            try:
                with open(machine_name, "r+") as f:
                    all_data = json.load(f)
            except json.JSONDecodeError:
                all_data = {}
        else:
            all_data = {}
        all_data[now] = data
        with open(machine_name, "w") as f:
            json.dump(all_data, f, indent=4)

