import tempfile
import unittest
import sys
import types
from unittest.mock import patch
from pathlib import Path
from nova.settings import Settings, settings_path
from nova.playlist import read_m3u, write_m3u
from nova.pip_state import PlaybackState, handoff
from nova.plugins import discover_plugins
from nova.player import NovaPlayer
from nova.subtitles import read_subtitles

class CoreTests(unittest.TestCase):
    def test_tinytag_metadata_and_cover(self):
        from nova.metadata import audio_metadata
        tinytag = types.ModuleType("tinytag")
        class TinyTag:
            @staticmethod
            def get(path, image=False):
                class Image: data = b"cover-bytes"
                class Images: any = Image()
                class Tag:
                    title="Song"; artist="Artist"; album="Album"; duration=90.0; images=Images()
                return Tag()
        tinytag.TinyTag=TinyTag
        with patch.dict(sys.modules,{"tinytag":tinytag}):
            data=audio_metadata("track.mp3")
        self.assertEqual(data["title"],"Song")
        self.assertEqual(data["artwork"],b"cover-bytes")
        self.assertEqual(data["duration"],90.0)
    def test_settings_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            s=Settings(Path(d)/"settings.json"); s.set("theme","light"); self.assertEqual(Settings(s.path).get("theme"),"light")
    def test_theme_defaults_to_system(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(Settings(Path(d)/"settings.json").get("theme"),"system")
    def test_macos_settings_use_application_support(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("nova.settings.system", return_value="Darwin"), patch("nova.settings.Path.home", return_value=Path(d)):
                expected = Path(d) / "Library" / "Application Support" / "NOVA Player" / "settings.json"
                self.assertEqual(settings_path(), expected)
    def test_linux_settings_follow_xdg_config_home(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("nova.settings.system", return_value="Linux"), patch.dict("os.environ", {"XDG_CONFIG_HOME": d}):
                self.assertEqual(settings_path(), Path(d) / "NOVA Player" / "settings.json")
    def test_legacy_backend_settings_are_removed(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"settings.json"
            path.write_text('{"engine":"legacy", "hardware_acceleration":"off"}', encoding="utf-8")
            settings=Settings(path)
            self.assertNotIn("engine", settings.data)
            self.assertNotIn("hardware_acceleration", settings.data)
    def test_default_settings_migrate_from_old_product_folder(self):
        import os
        with tempfile.TemporaryDirectory() as d:
            old=Path(d)/"NOVA Media Player"/"settings.json"
            old.parent.mkdir()
            old.write_text('{"theme":"light"}',encoding="utf-8")
            with patch.dict(os.environ,{"APPDATA":d}), patch("nova.settings.system",return_value="Windows"):
                settings=Settings()
            self.assertEqual(settings.get("theme"),"light")
            self.assertEqual(settings.path.parent.name,"NOVA Player")
    def test_m3u_relative_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); media=root/"tracks"/"song with spaces.mp3"
            media.parent.mkdir(); media.write_bytes(b"")
            playlist=root/"playlists"/"list.m3u"
            write_m3u(playlist,[str(media)])
            self.assertIn("../tracks/song with spaces.mp3",playlist.read_text(encoding="utf-8"))
            self.assertEqual(read_m3u(playlist),[str(media.resolve())])
    def test_m3u_preserves_network_stream_urls(self):
        with tempfile.TemporaryDirectory() as d:
            playlist=Path(d)/"streams.m3u8"
            url="https://example.invalid/live/channel.m3u8?token=abc"
            write_m3u(playlist,[url])
            self.assertEqual(read_m3u(playlist),[url])
    def test_pip_handoff_copies_independent_snapshot(self):
        s=PlaybackState("a.mp4",14.5,True,42,"captions.srt",1.25); p=handoff(s,None); self.assertEqual(p,s); self.assertIsNot(p,s)
    def test_qt_state_uses_playback_state_api(self):
        qt_root=types.ModuleType("PySide6"); qt_root.__path__=[]
        qt_multimedia=types.ModuleType("PySide6.QtMultimedia")
        class MediaPlayer:
            class PlaybackState: PausedState=2
        qt_multimedia.QMediaPlayer=MediaPlayer
        player=NovaPlayer.__new__(NovaPlayer)
        class Player:
            def position(self): return 12500
            def playbackState(self): return 2
        player.player=Player()
        with patch.dict(sys.modules,{"PySide6":qt_root,"PySide6.QtMultimedia":qt_multimedia}):
            state=player.state()
        self.assertEqual(state["position"],12.5)
        self.assertTrue(state["paused"])
    def test_player_load_accepts_http_stream_urls(self):
        qt_root=types.ModuleType("PySide6"); qt_root.__path__=[]
        qt_core=types.ModuleType("PySide6.QtCore")
        class QUrl:
            def __init__(self, value): self.value=value
            def isValid(self): return True
            def __eq__(self, other): return isinstance(other, QUrl) and self.value == other.value
        qt_core.QUrl=QUrl
        player=NovaPlayer.__new__(NovaPlayer)
        class Backend:
            source=None
            started=False
            def setSource(self, source): self.source=source
            def play(self): self.started=True
        player.player=Backend()
        with patch.dict(sys.modules,{"PySide6":qt_root,"PySide6.QtCore":qt_core}):
            player.load("https://example.invalid/live")
        self.assertEqual(player.player.source,QUrl("https://example.invalid/live"))
        self.assertTrue(player.player.started)

    def test_player_load_accepts_android_content_uris(self):
        qt_root=types.ModuleType("PySide6"); qt_root.__path__=[]
        qt_core=types.ModuleType("PySide6.QtCore")
        class QUrl:
            def __init__(self, value): self.value=value
            def isValid(self): return True
            def __eq__(self, other): return isinstance(other, QUrl) and self.value == other.value
        qt_core.QUrl=QUrl
        player=NovaPlayer.__new__(NovaPlayer)
        class Backend:
            source=None
            started=False
            def setSource(self, source): self.source=source
            def play(self): self.started=True
        player.player=Backend()
        content_uri="content://com.android.providers.media.documents/document/video%3A42"
        with patch.dict(sys.modules,{"PySide6":qt_root,"PySide6.QtCore":qt_core}):
            player.load(content_uri)
        self.assertEqual(player.player.source,QUrl(content_uri))
        self.assertTrue(player.player.started)
    def test_srt_subtitles_parse_multiline_text_and_html_tags(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"captions.srt"
            path.write_text("1\n00:00:01,250 --> 00:00:03,500\n<b>Hello</b> &amp;\nworld\n", encoding="utf-8")
            self.assertEqual(read_subtitles(path), [(1250, 3500, "Hello &\nworld")])
    def test_vtt_subtitles_parse_cues_and_skip_header(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"captions.vtt"
            path.write_text("WEBVTT\n\nintro\n00:02.5 --> 00:04.000\nWelcome\n", encoding="utf-8")
            self.assertEqual(read_subtitles(path), [(2500, 4000, "Welcome")])
    def test_plugin_discovery(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,"codec").mkdir(); self.assertEqual(discover_plugins([d])[0]["name"],"codec")

if __name__=="__main__":unittest.main()

