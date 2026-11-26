import json
from pathlib import Path
from platform import system

DEFAULTS = {"volume": 70, "muted": False, "playback_rate": 1.0,
            "repeat_mode": "off", "shuffle": False, "quit_after_playlist": False,
            "shortcuts": {"play_pause": "Space", "fullscreen": "F", "pip": "P",
                                             "seek_forward": "Right", "seek_backward": "Left",
                                             "volume_up": "Up", "volume_down": "Down"},
            "subtitle_offset": 0.0, "recent_files": [], "plugin_paths": [], "theme": "system"}

def settings_path():
    import os
    current = system()
    if current == "Windows":
        root = Path(os.environ.get("APPDATA") or os.environ.get("LOCALAPPDATA") or Path.home() / "AppData/Roaming")
    elif current == "Darwin":
        root = Path.home() / "Library" / "Application Support"
    else:
        root = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return root / "NOVA Player" / "settings.json"

class Settings:
    def __init__(self, path=None):
        self.path = Path(path) if path else settings_path()
        self.legacy_path = self.path.parent.parent / "NOVA Media Player" / self.path.name if path is None else None
        self.data = {**DEFAULTS, "shortcuts": dict(DEFAULTS["shortcuts"])}
        self.load()
    def load(self):
        try:
            source = self.path
            if not source.exists() and self.legacy_path and self.legacy_path.exists():
                source = self.legacy_path
            obj = json.loads(source.read_text(encoding="utf-8"))
            self.data.update(obj)
            # Drop legacy playback backend settings when upgrading NOVA profiles.
            self.data.pop("engine", None)
            self.data.pop("hardware_acceleration", None)
            self.data.pop("eq", None)
        except (OSError, ValueError, TypeError):
            pass
        return self.data
    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")
    def get(self, key, default=None): return self.data.get(key, default)
    def set(self, key, value):
        self.data[key] = value
        self.save()
