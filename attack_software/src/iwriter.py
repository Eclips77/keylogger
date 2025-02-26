from abc import ABC, abstractmethod

class IWriter(ABC):
    @abstractmethod
    def send_data(self, data: str) -> None:
        pass