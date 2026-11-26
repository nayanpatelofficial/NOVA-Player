from pathlib import Path

def discover_plugins(paths):
    found = []
    for raw in paths:
        root = Path(raw).expanduser()
        if root.is_dir():
            for item in sorted(root.iterdir()):
                found.append({"name": item.stem, "path": str(item), "kind": "directory" if item.is_dir() else "file", "enabled": True})
    return found
