import os
import json
import logging
from flask import Flask, request, jsonify
from attack_software.config.config import NAME_FILE

app = Flask(__name__)

name_log = "logs"
if not os.path.exists(name_log):
    os.makedirs(name_log)

logging.basicConfig(
    filename="logs/log.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)



def initialize_server() -> None:
    """
    Ensures that the necessary directories exist for storing data.
    Creates the folder if it does not exist.
    """
    logging.info("Initializing server and checking necessary folders.")

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
    new_data = request.json.get('data')

    if not isinstance(new_data, dict):
        logging.error("Invalid data received")
        return jsonify({"error": "Invalid data format. Expected a JSON object."}), 400

    old_data = load_existing_data()
    data = append_to_data_list(old_data, new_data)
    save_data_to_file(data)

    return jsonify({"message": "Data saved successfully"}), 200

def append_to_data_list(old_data, new_data) -> list:
    """
    Appends new data to the existing data list.
    Ensures that the new data is a dictionary before appending.
    """
    if not isinstance(new_data, dict):
        logging.error("Data structure mismatch.")
        return new_data

    old_data.append(new_data)
    return old_data

def load_existing_data() -> list:
    """Loads existing data from the JSON file or returns an empty list."""
    if not os.path.exists(NAME_FILE):
        logging.warning(f"Data file {NAME_FILE} does not exist.")
        return []

    try:
        with open(NAME_FILE, "r") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Failed to load JSON file: {e}")
        return []


def save_data_to_file(data_list) -> None:
    """
    Saves the provided data list to the JSON file.
    Skips writing if the data list is empty.
    """
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
    data = load_existing_data()

    if not data:
        logging.error("No data available in the file.")
        return jsonify({"error": "No data available"}), 404

    logging.info("Returning stored data.")
    return jsonify(data), 200

if __name__ == '__main__':
    app.run(debug=True)
