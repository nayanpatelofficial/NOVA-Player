"""Small, dependency-free parser for external SRT and WebVTT subtitle files."""
from html import unescape
from pathlib import Path
import re


_TIMESTAMP = re.compile(
    r"(?:(?P<sh>\d{1,2}):)?(?P<sm>\d{2}):(?P<ss>\d{2})[,.](?P<sms>\d{1,3})"
    r"\s*-->\s*"
    r"(?:(?P<eh>\d{1,2}):)?(?P<em>\d{2}):(?P<es>\d{2})[,.](?P<ems>\d{1,3})"
)
_TAG = re.compile(r"<[^>]*>")


def _milliseconds(match, prefix):
    fraction = match.group(f"{prefix}ms").ljust(3, "0")[:3]
    hour = int(match.group(f"{prefix}h") or 0)
    return (((hour * 60 + int(match.group(f"{prefix}m"))) * 60
             + int(match.group(f"{prefix}s"))) * 1000 + int(fraction))


def read_subtitles(path):
    """Return sorted (start_ms, end_ms, text) cues from an SRT or VTT file."""
    path = Path(path)
    if path.suffix.lower() not in {".srt", ".vtt"}:
        raise ValueError("NOVA supports external .srt and .vtt subtitle files.")
    content = path.read_text(encoding="utf-8-sig", errors="replace")
    cues = []
    for block in re.split(r"\n\s*\n", content.replace("\r\n", "\n").replace("\r", "\n")):
        lines = block.splitlines()
        timing_index = next((i for i, line in enumerate(lines) if _TIMESTAMP.search(line)), None)
        if timing_index is None:
            continue
        match = _TIMESTAMP.search(lines[timing_index])
        start = _milliseconds(match, "s")
        end = _milliseconds(match, "e")
        text = "\n".join(_TAG.sub("", line).strip() for line in lines[timing_index + 1:]).strip()
        text = unescape(text)
        if text and end > start:
            cues.append((start, end, text))
    return sorted(cues, key=lambda cue: (cue[0], cue[1]))
