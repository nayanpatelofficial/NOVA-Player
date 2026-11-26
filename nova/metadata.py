from pathlib import Path

def audio_metadata(path):
    result = {"title": Path(path).stem, "artist": "", "album": "", "artwork": None, "duration": None}
    try:
        from tinytag import TinyTag
        audio = TinyTag.get(path, image=True)
        if audio:
            for key in ("title", "artist", "album"):
                value = getattr(audio, key, None)
                if value:
                    result[key] = str(value)
            result["duration"] = audio.duration
            image = getattr(getattr(audio, "images", None), "any", None)
            if image:
                result["artwork"] = image.data
    except Exception:
        pass
    return result
