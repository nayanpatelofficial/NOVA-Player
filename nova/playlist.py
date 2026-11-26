import os
from pathlib import Path
from urllib.parse import urlsplit


NETWORK_SCHEMES = {"http", "https", "rtsp", "rtmp"}


def is_network_url(value):
    parsed = urlsplit(str(value).strip())
    return parsed.scheme.lower() in NETWORK_SCHEMES and bool(parsed.netloc)


def read_m3u(path):
    """Read M3U/M3U8 paths relative to the playlist and keep stream URLs intact."""
    path = Path(path)
    entries = []
    for raw in path.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if is_network_url(line):
            entries.append(line)
            continue
        item = Path(line)
        entries.append(str((path.parent / item).resolve() if not item.is_absolute() else item.resolve()))
    return entries


def write_m3u(path, entries):
    """Write portable relative paths where possible and preserve network URLs."""
    path = Path(path)
    playlist_path = path.absolute()
    playlist_dir = playlist_path.parent
    lines = ["#EXTM3U"]
    for entry in entries:
        value = str(entry).strip()
        if not value:
            continue
        if is_network_url(value):
            lines.append(value)
            continue
        media_path = Path(value).expanduser()
        if not media_path.is_absolute():
            media_path = Path.cwd() / media_path
        media_path = media_path.resolve(strict=False)
        try:
            stored_path = Path(os.path.relpath(media_path, playlist_dir))
        except ValueError:
            # Windows paths on different drives cannot be made relative.
            stored_path = media_path
        lines.append(stored_path.as_posix())
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
