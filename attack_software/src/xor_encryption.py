from Encryption import Encryption
from attack_software.config.config import SECRET_KEY

class XOREncryption(Encryption):
    """
    XOR encryption class.
    """
    def __init__(self):
        self.secret_key = SECRET_KEY

    def encrypt(self, text):
        encrypted_text = ""

        # Iterate over each character in the text
        for i in range(len(text)):
            encrypted_text += chr(ord(text[i]) ^ ord(self.secret_key[i % len(self.secret_key)]))

        return encrypted_text

    def decrypt(self, encrypted_text):
        return self.encrypt(encrypted_text)
