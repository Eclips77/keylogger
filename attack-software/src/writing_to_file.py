from datetime import datetime
import json
from iwriter import IWriter


class FileWriter(IWriter):

    def send_data(self,data: str, machine_name: str) -> None:
        """
        The function calls receiving_data which returns
        the information already present in the file.
        adds the new information to it. and sends to
        the writer_to_file function that inserts the
        updated data into the file.
        """

        receiving_data = self.receiving_data(machine_name)
        receiving_data[self.current_tine()] = data
        self.writer_to_file(receiving_data,machine_name)

    @staticmethod
    def receiving_data(machine_name:str) -> dict:

        """
        The function returns the information
        that already exists in the file
        """

        try:
            with open(machine_name,"r") as f:
                receiving_data = json.load(f)
                if not isinstance(receiving_data,dict):
                    return {}
            return receiving_data
        except (json.JSONDecodeError, FileNotFoundError, OSError):
            return {}

    @staticmethod
    def writer_to_file(data: dict,machine_name: str) -> None:

        """
        The function writes to a json file
        """

        with open(machine_name, "w") as f:
            json.dump(data, f)

    @staticmethod
    def current_tine():
        """
        The function returns a string
        containing the current time
        :return:
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


