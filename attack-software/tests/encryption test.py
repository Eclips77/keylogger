import unittest
from xor_encryption import XOREncryption

class TestXOREncryption(unittest.TestCase):
    def setUp(self):
        """Initialize the XOREncryption instance before each test."""
        self.xor_encryption = XOREncryption()

    def test_basic_encryption_decryption(self):
        """Test if encryption and decryption work correctly."""
        text = "Hello, World!"
        encrypted = self.xor_encryption.encrypt(text)
        decrypted = self.xor_encryption.decrypt(encrypted)
        self.assertEqual(decrypted, text, "Decryption should return the original text.")

    def test_empty_string(self):
        """Test encryption and decryption of an empty string."""
        text = ""
        encrypted = self.xor_encryption.encrypt(text)
        decrypted = self.xor_encryption.decrypt(encrypted)
        self.assertEqual(decrypted, text, "Empty string should remain unchanged.")

    def test_special_characters(self):
        """Test encryption with special characters."""
        text = "!@#$%^&*()_+-=[]{};':,.<>/?\n\t"
        encrypted = self.xor_encryption.encrypt(text)
        decrypted = self.xor_encryption.decrypt(encrypted)
        self.assertEqual(decrypted, text, "Special characters should be encrypted and decrypted correctly.")

    def test_long_text(self):
        """Test encryption with a long text."""
        text = "A" * 1000  # 1000-character long string
        encrypted = self.xor_encryption.encrypt(text)
        decrypted = self.xor_encryption.decrypt(encrypted)
        self.assertEqual(decrypted, text, "Long text should be processed correctly.")

    def test_reversible_encryption(self):
        """Ensure encryption does not return the original text."""
        text = "SensitiveData"
        encrypted = self.xor_encryption.encrypt(text)
        self.assertNotEqual(encrypted, text, "Encryption should modify the original text.")

if __name__ == '__main__':
    unittest.main()
