from abc import ABC, abstractmethod

class Encryption(ABC):
    """
    Abstract base class for encryption algorithms.
    Every encryption class must implement the encrypt and decrypt methods.
    """

    @abstractmethod
    def encrypt(self, plaintext) -> str:
        pass

    @abstractmethod
    def decrypt(self, ciphertext) -> str:
        pass