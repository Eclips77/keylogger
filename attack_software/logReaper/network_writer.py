import requests
from interface import IWriter

class NetworkWriter(IWriter):
    def __init__(self, server_url: str):
        self.server_url = server_url

    def send_data(self, data: str, machine_name: str) -> None:
        payload = {"machine": machine_name, "data": data}
        headers = {'Content-Type': 'application/json'}
        requests.post(self.server_url, json=payload, headers=headers)
