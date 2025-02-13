import sys

def xor_decrypt(data: bytes, key: int) -> str:
    return "".join(chr(byte ^ key) for byte in data)

def main():
    if len(sys.argv) != 3:
        print("Usage: python py.le_decrypt.py <encrypted_file_path> <xor_key>")
        sys.exit(1)

    encrypted_file_path = sys.argv[1]
    try:
        xor_key = int(sys.argv[2])
    except ValueError:
        print("Error: XOR key must be an integer.")
        sys.exit(1)

    try:
        with open(encrypted_file_path, "rb") as file:
            encrypted_data = file.read()

        decrypted_text = xor_decrypt(encrypted_data, xor_key)
        print("Decrypted content:\n")
        print(decrypted_text)

    except FileNotFoundError:
        print(f"Error: File '{encrypted_file_path}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
