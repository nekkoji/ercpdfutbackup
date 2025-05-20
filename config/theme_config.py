import os
import json

CONFIG_FILE = "theme_config.json"

def load_theme():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("dark_mode", False)
        except json.JSONDecodeError:
            return False
    return False

def save_theme(enabled):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"dark_mode": enabled}, f)
