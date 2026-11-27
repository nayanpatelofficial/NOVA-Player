"""NOVA's single playback interface using the Windows media stack."""
from pathlib import Path
from urllib.parse import urlsplit


class NovaPlaybackError(RuntimeError):
    """Raised when NOVA cannot load or control media."""


class NovaPlayer:
    name = "NOVA Player"

    def __init__(self, widget=None):
        try:
            from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
            self.player = QMediaPlayer()
            self.audio = QAudioOutput()
            self.player.setAudioOutput(self.audio)
            if widget is not None:
                self.player.setVideoOutput(widget)
            self._pending_seek = None
            self._pending_pause = None
            self.player.mediaStatusChanged.connect(self._media_status_changed)
        except Exception as exc:
            raise NovaPlaybackError(f"NOVA playback could not initialize: {exc}") from exc

    def _media_status_changed(self, status):
        from PySide6.QtMultimedia import QMediaPlayer
        if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
            if self._pending_seek is not None:
                self.player.setPosition(self._pending_seek)
                self._pending_seek = None
            if self._pending_pause is not None:
                should_pause = self._pending_pause
                self._pending_pause = None
                self.player.pause() if should_pause else self.player.play()

    def load(self, path):
        from PySide6.QtCore import QUrl
        value = str(path).strip()
        parsed = urlsplit(value)
        if ((parsed.scheme.lower() in {"http", "https", "rtsp", "rtmp"} and parsed.netloc)
                or parsed.scheme.lower() == "content"):
            source = QUrl(value)
            if not source.isValid():
                raise NovaPlaybackError("The network stream URL is invalid.")
        else:
            file_path = Path(value).expanduser()
            if not file_path.is_file():
                raise NovaPlaybackError(f"File not found: {file_path}")
            source = QUrl.fromLocalFile(str(file_path.resolve()))
        self.player.setSource(source)
        self.player.play()

    def stop(self):
        self.player.stop()

    def set_playback_rate(self, rate):
        self.player.setPlaybackRate(float(rate))

    def set_audio_device(self, device):
        self.audio.setDevice(device)

    def set_muted(self, muted):
        self.audio.setMuted(bool(muted))

    def is_muted(self):
        return self.audio.isMuted()

    def pause(self, value=True):
        from PySide6.QtMultimedia import QMediaPlayer
        if self.player.mediaStatus() in (QMediaPlayer.MediaStatus.LoadingMedia, QMediaPlayer.MediaStatus.NoMedia):
            self._pending_pause = value
        else:
            self.player.pause() if value else self.player.play()

    def seek(self, seconds):
        from PySide6.QtMultimedia import QMediaPlayer
        if self.player.mediaStatus() in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
            self.player.setPosition(int(seconds * 1000))
        else:
            self._pending_seek = int(seconds * 1000)

    def set_volume(self, value):
        self.audio.setVolume(max(0.0, min(1.0, value / 100)))

    def add_subtitle(self, path):
        raise NovaPlaybackError("External subtitles are not available in this NOVA build")

    def state(self):
        from PySide6.QtMultimedia import QMediaPlayer
        paused = self.player.playbackState() == QMediaPlayer.PlaybackState.PausedState
        return {"position": self.player.position() / 1000, "paused": paused,
                "subtitle": None, "subtitle_offset": 0.0}

    def duration(self):
        return max(0, self.player.duration() // 1000)

    def close(self):
        self.player.stop()

