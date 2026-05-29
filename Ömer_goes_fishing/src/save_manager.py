import json
import os
import time

SAVE_DIR = "./saves"

# Ordner erstellen, falls er noch nicht existiert
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

def get_save_path(slot):
    return os.path.join(SAVE_DIR, f"save_slot_{slot}.json")

def load_save(slot):
    path = get_save_path(slot)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

def save_game(slot, game_data):
    path = get_save_path(slot)
    # Zeitstempel automatisch hinzufügen
    game_data["timestamp"] = time.strftime("%d.%m.%Y %H:%M")
    with open(path, "w") as f:
        json.dump(game_data, f, indent=4)

def delete_save(slot):
    path = get_save_path(slot)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False