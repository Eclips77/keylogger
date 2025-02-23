from interface import IEncryptor

class Encryptor(IEncryptor):
    def __init__(self, key: str):
        self.key = key

    def encrypt(self, data: str) -> str:
        return "".join(chr(ord(c) ^ ord(self.key[i % len(self.key)])) for i, c in enumerate(data))

    def decrypt(self, data: str) -> str:
        return self.encrypt(data)
