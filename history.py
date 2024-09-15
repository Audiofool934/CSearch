import os
import json
from datetime import datetime
from slugify import slugify


def load_history(history_file_path):
    """Loads history from the JSON file."""
    os.makedirs(os.path.dirname(history_file_path), exist_ok=True)

    if os.path.exists(history_file_path):
        with open(history_file_path, "r") as file:
            return json.load(file)
    else:
        return {}


def save_history(history_file_path, history):
    """Saves the history to the JSON file."""
    with open(history_file_path, "w") as file:
        json.dump(history, file, indent=4)


def update_history(history_folder_path, target_domains):
    """Updates the history with the given target_domains."""
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    history_file_path = os.path.join(history_folder_path, "history.json")
    domains_key = slugify(str(sorted(target_domains)))
    history = load_history(history_file_path)

    if domains_key not in history:
        dict_path = os.path.join(history_folder_path, domains_key)
        history[domains_key] = {
            "time": time,
            "dict_path": dict_path,
        }
        os.makedirs(dict_path, exist_ok=True)
    else:
        history[domains_key]["time"] = time

    save_history(history_file_path, history)

    return history