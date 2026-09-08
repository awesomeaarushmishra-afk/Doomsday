import json
import os
import pygame as pg

SETTINGS_FILE = "user_settings.json"

DEFAULT_KEYBINDS = {
    "forward": pg.K_w,
    "backward": pg.K_s,
    "strafe_left": pg.K_a,
    "strafe_right": pg.K_d,
    "interact": pg.K_e,
    "cheat_menu": pg.K_c,
    "minimap_toggle": pg.K_TAB,
}

DEFAULT_SETTINGS = {
    "mouse_sensitivity": 0.0003,
    "music_volume": 0.7,
    "fov_degrees": 60,
    "keybinds": dict(DEFAULT_KEYBINDS),
}


class SettingsManager:
    """Loads, saves, and applies user-adjustable settings (sensitivity, volume, FOV, keybinds)."""

    def __init__(self):
        self.values = self._load()

    def _load(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    data = json.load(f)
                # Merge with defaults so new keys added later don't crash old save files
                merged = dict(DEFAULT_SETTINGS)
                merged.update(data)
                merged["keybinds"] = dict(DEFAULT_KEYBINDS)
                merged["keybinds"].update(data.get("keybinds", {}))
                return merged
            except Exception as e:
                print(f"Failed to load settings, using defaults: {e}")
        return {
            "mouse_sensitivity": DEFAULT_SETTINGS["mouse_sensitivity"],
            "music_volume": DEFAULT_SETTINGS["music_volume"],
            "fov_degrees": DEFAULT_SETTINGS["fov_degrees"],
            "keybinds": dict(DEFAULT_KEYBINDS),
        }

    def save(self):
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(self.values, f, indent=2)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value):
        self.values[key] = value

    def get_keybind(self, action):
        return self.values["keybinds"].get(action, DEFAULT_KEYBINDS.get(action))

    def set_keybind(self, action, key_code):
        self.values["keybinds"][action] = key_code

    def reset_to_defaults(self):
        self.values = {
            "mouse_sensitivity": DEFAULT_SETTINGS["mouse_sensitivity"],
            "music_volume": DEFAULT_SETTINGS["music_volume"],
            "fov_degrees": DEFAULT_SETTINGS["fov_degrees"],
            "keybinds": dict(DEFAULT_KEYBINDS),
        }
