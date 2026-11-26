import sys
import os
import random
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QAction, QActionGroup, QKeySequence, QIcon, QPixmap, QColor
from PySide6.QtMultimedia import QMediaDevices, QMediaMetaData
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QSlider, QFileDialog, QListWidget, QSplitter, QMessageBox, QComboBox,
    QDialog, QFormLayout, QDialogButtonBox, QGroupBox, QGridLayout, QFrame,
    QGraphicsDropShadowEffect,
    QInputDialog,
)

from .settings import Settings
from .player import NovaPlayer
from .playlist import read_m3u, write_m3u, is_network_url
from .subtitles import read_subtitles
from .metadata import audio_metadata
from .plugins import discover_plugins
from .pip_state import PlaybackState, handoff

MEDIA = {".mp3", ".flac", ".wav", ".aac", ".m4a", ".ogg", ".opus", ".wma",
         ".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"}
STYLE = """
QMainWindow, QWidget { background:#0b1020; color:#e7edf8; font-family:'Segoe UI'; font-size:10pt; }
QLabel { background:transparent; border:0; }
QMenuBar { background:#111a2c; padding:7px; }
QMenuBar::item:selected, QMenu::item:selected { background:#263a5b; }
QMenu { background:#111a2c; border:1px solid #293851; }
QFrame#Header { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(43,35,63,145), stop:0.45 rgba(18,20,36,118), stop:1 rgba(64,43,81,128)); border:1px solid rgba(222,199,255,58); border-top:1px solid rgba(255,255,255,92); border-radius:15px; }
QFrame#Sidebar { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(36,31,53,155), stop:1 rgba(17,20,35,138)); border:1px solid rgba(207,177,245,54); border-top:1px solid rgba(255,255,255,80); border-radius:16px; }
QFrame#Transport { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(63,49,80,154), stop:0.48 rgba(27,25,42,130), stop:1 rgba(56,40,73,145)); border:1px solid rgba(220,193,255,68); border-top:1px solid rgba(255,255,255,105); border-radius:15px; }
QFrame#VideoCard { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(20,18,33,240), stop:1 rgba(5,7,14,250)); border:1px solid rgba(215,190,248,45); border-radius:15px; }
QLabel#Brand { background:transparent; color:#f4f7ff; font-size:15pt; font-weight:650; }
QLabel#Version { color:#c7a7ff; font-size:9pt; font-weight:600; }
QLabel#Hint { color:#a99bbd; }
QPushButton { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(255,255,255,20), stop:1 rgba(210,180,245,7)); color:#eee8fa; border:1px solid rgba(220,195,250,48); border-radius:9px; padding:9px 14px; }
QPushButton:hover { background:rgba(181,140,230,38); border-color:rgba(206,172,245,100); }
QPushButton#Primary { background:rgba(142,100,200,175); color:#fff; font-weight:650; border:1px solid rgba(215,190,250,62); }
QPushButton#Primary:hover { background:rgba(167,124,221,240); }
QPushButton#CompactOpen { background:rgba(255,255,255,10); color:#ded1f0; border:1px solid rgba(205,176,240,40); border-radius:7px; padding:2px 6px; font-size:9pt; }
QPushButton#CompactOpen:hover { background:rgba(182,143,230,38); }
QListWidget { background:transparent; border:0; outline:0; padding:5px; }
QListWidget::item { padding:10px 9px; border-radius:7px; color:#bfcbdd; }
QListWidget::item:selected { color:#fff; background:#302541; border-left:3px solid #b68ce9; }
QSlider::groove:horizontal { height:4px; background:#393047; border-radius:2px; }
QSlider::sub-page:horizontal { background:#b28add; border-radius:2px; }
QSlider::handle:horizontal { background:#f5edff; width:12px; margin:-5px 0; border-radius:6px; }
QSlider::groove:vertical { width:5px; background:#393047; }
QSlider::handle:vertical { background:#b28add; height:13px; margin:0 -5px; border-radius:6px; }
QComboBox { background:#191522; border:1px solid #3a304d; border-radius:7px; padding:7px; }
QStatusBar { background:#111a2c; color:#92a1ba; }
"""
LIGHT_STYLE = """
QMainWindow, QWidget { background:#f3f5fb; color:#20263a; font-family:'Segoe UI'; font-size:10pt; }
QMenuBar { background:#ffffff; padding:7px; }
QMenuBar::item:selected, QMenu::item:selected { background:#eee8ff; }
QMenu { background:#fff; border:1px solid #dedbea; }
QLabel { background:transparent; border:0; }
QFrame#Header { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(255,255,255,214), stop:0.5 rgba(249,247,255,172), stop:1 rgba(233,224,249,175)); border:1px solid rgba(135,114,170,56); border-top:1px solid rgba(255,255,255,235); border-radius:15px; }
QFrame#Sidebar { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(255,255,255,220), stop:1 rgba(238,233,249,185)); border:1px solid rgba(135,114,170,58); border-top:1px solid rgba(255,255,255,240); border-radius:16px; }
QFrame#Transport { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(255,255,255,225), stop:0.48 rgba(250,247,255,185), stop:1 rgba(230,218,249,190)); border:1px solid rgba(135,114,170,68); border-top:1px solid rgba(255,255,255,245); border-radius:15px; }
QFrame#VideoCard { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(36,31,49,245), stop:1 rgba(13,12,23,250)); border:1px solid rgba(137,119,164,75); border-radius:15px; }
QLabel#Brand { background:transparent; color:#27223b; font-size:15pt; font-weight:650; }
QLabel#Version { color:#7953c8; font-size:9pt; font-weight:600; }
QLabel#Hint { color:#73788d; }
QPushButton { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 rgba(255,255,255,190), stop:1 rgba(244,238,252,145)); color:#302a43; border:1px solid rgba(123,98,160,62); border-radius:9px; padding:9px 14px; }
QPushButton:hover { background:rgba(204,187,235,105); border-color:rgba(123,98,160,115); }
QPushButton#Primary { background:rgba(120,85,200,180); color:#fff; font-weight:650; border:1px solid rgba(255,255,255,88); }
QPushButton#Primary:hover { background:rgba(138,105,213,245); }
QPushButton#CompactOpen { background:rgba(255,255,255,110); color:#514263; border:1px solid rgba(123,98,160,54); border-radius:7px; padding:2px 6px; font-size:9pt; }
QPushButton#CompactOpen:hover { background:rgba(204,187,235,115); }
QListWidget { background:transparent; border:0; outline:0; padding:5px; }
QListWidget::item { padding:10px 9px; border-radius:7px; color:#4a4c60; }
QListWidget::item:selected { color:#302148; background:#eee8ff; border-left:3px solid #9b7be0; }
QSlider::groove:horizontal { height:5px; background:#dedfea; border-radius:2px; }
QSlider::sub-page:horizontal { background:#8a69d5; border-radius:2px; }
QSlider::handle:horizontal { background:#fff; border:1px solid #c7b8e8; width:13px; margin:-5px 0; border-radius:6px; }
QSlider::groove:vertical { width:5px; background:#dedfea; }
QSlider::handle:vertical { background:#8a69d5; height:13px; margin:0 -5px; border-radius:6px; }
QComboBox { background:#fff; border:1px solid #ded9e9; border-radius:7px; padding:7px; }
QStatusBar { background:#fff; color:#73788d; }
"""

LOGO_FILE = Path(__file__).resolve().parent.parent / "assets" / "nova_logo_light_dark.png"

def logo_pixmap(theme, size=42):
    source = QPixmap(str(LOGO_FILE))
    if source.isNull():
        return QPixmap()
    half = source.width() // 2
    logo = source.copy(half if theme == "dark" else 0, int(source.height() * .30),
                       half, int(source.height() * .40))
    return logo.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                       Qt.TransformationMode.SmoothTransformation)


class VideoSurface(QVideoWidget):
    doubleClicked = Signal()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.subtitle_label = QLabel(self)
        self.subtitle_label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.subtitle_label.setStyleSheet(
            "QLabel { color:white; background:rgba(0,0,0,175); border-radius:5px; "
            "padding:5px 10px; font-size:12pt; font-weight:600; }"
        )
        self.subtitle_label.hide()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width = max(0, self.width() - 36)
        height = min(82, max(42, self.height() // 4))
        self.subtitle_label.setGeometry(18, max(0, self.height() - height - 10), width, height)
        self.subtitle_label.raise_()
    def mousePressEvent(self, event):
        if getattr(self.window(), "pip", False) and event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.window().frameGeometry().topLeft()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (getattr(self.window(), "pip", False) and event.buttons() & Qt.MouseButton.LeftButton
                and hasattr(self, "_drag_offset")):
            self.window().move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.doubleClicked.emit()
        super().mouseDoubleClickEvent(event)


class PlayerWindow(QMainWindow):
    def __init__(self, settings=None, pip=False):
        super().__init__()
        self.settings = settings or Settings()
        self.pip = pip
        self.nova_player = None
        self.files = []
        self.current = None
        self.paused = False
        self._pip_owner = None
        self._pip_window = None
        self._closing = False
        self._switching_media = False
        self._fullscreen = False
        self.external_subtitles = []
        self.external_subtitle_path = None
        self.active_theme = self.effective_theme()
        self.setWindowTitle("NOVA Player")
        self.resize(1120 if not pip else 480, 720 if not pip else 300)
        self.setMinimumSize(860, 560) if not pip else None
        self.setAcceptDrops(True)

        if pip:
            self.build_pip_ui()
            self.init_nova_player()
            self.apply_shortcuts()
            self.apply_theme()
            return

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        self.outer_layout = outer
        outer.setContentsMargins(18, 15, 18, 12)
        outer.setSpacing(13)

        self.header = QFrame(objectName="Header")
        self.header.setFixedHeight(52)
        header_row = QHBoxLayout(self.header)
        header_row.setContentsMargins(11, 4, 12, 4)
        header_row.setSpacing(9)
        self.brand_icon = QLabel()
        self.brand_icon.setFixedSize(32, 32)
        header_row.addWidget(self.brand_icon)
        brand = QLabel("NOVA Player")
        brand.setObjectName("Brand")
        header_row.addWidget(brand)
        header_row.addStretch(1)
        self.playback_badge = QLabel("NOVA Playback")
        self.playback_badge.setObjectName("Hint")
        header_row.addWidget(self.playback_badge)
        outer.addWidget(self.header)

        body = QSplitter(Qt.Orientation.Horizontal)
        body.setChildrenCollapsible(False)
        video_card = QFrame(objectName="VideoCard")
        self.video_card = video_card
        video_layout = QVBoxLayout(video_card)
        video_layout.setContentsMargins(0, 0, 0, 0)
        self.video = VideoSurface()
        self.video.doubleClicked.connect(self.fullscreen)
        self.video.setMinimumSize(500, 300)
        video_layout.addWidget(self.video)
        body.addWidget(video_card)

        if not pip:
            self.sidebar = QFrame(objectName="Sidebar")
            side_layout = QVBoxLayout(self.sidebar)
            side_layout.setContentsMargins(12, 12, 12, 12)
            side_heading = QHBoxLayout()
            side_title = QLabel("YOUR LIBRARY")
            side_title.setObjectName("Version")
            side_heading.addWidget(side_title)
            side_heading.addStretch(1)
            open_button = QPushButton("＋ Add")
            open_button.setObjectName("CompactOpen")
            open_button.setToolTip("Open media files")
            open_button.clicked.connect(self.open_files)
            open_button.setFixedSize(68, 28)
            side_heading.addWidget(open_button)
            side_layout.addLayout(side_heading)
            self.library = QListWidget()
            self.library.itemDoubleClicked.connect(lambda item: self.play_index(self.library.row(item)))
            side_layout.addWidget(self.library)
            self.library_hint = QLabel("Open files or drop a folder here")
            self.library_hint.setObjectName("Hint")
            side_layout.addWidget(self.library_hint)
            body.addWidget(self.sidebar)
            body.setSizes([780, 280])
        else:
            self.library = None
            self.sidebar = None
        outer.addWidget(body, 1)

        self.transport = QFrame(objectName="Transport")
        controls = QVBoxLayout(self.transport)
        controls.setContentsMargins(14, 11, 14, 11)
        seek_row = QHBoxLayout()
        self.elapsed = QLabel("00:00")
        self.elapsed.setObjectName("Hint")
        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setRange(0, 0)
        self.seek.sliderReleased.connect(self.seek_to_slider)
        self.total = QLabel("00:00")
        self.total.setObjectName("Hint")
        seek_row.addWidget(self.elapsed)
        seek_row.addWidget(self.seek, 1)
        seek_row.addWidget(self.total)
        controls.addLayout(seek_row)

        buttons = QHBoxLayout()
        self.play_button = QPushButton("▶  Play")
        self.play_button.setObjectName("Primary")
        self.play_button.clicked.connect(self.toggle)
        buttons.addWidget(self.play_button)
        subtitle = QPushButton("Subtitles")
        subtitle.clicked.connect(self.open_subtitle)
        buttons.addWidget(subtitle)
        if not pip:
            pip_button = QPushButton("Picture in Picture")
            pip_button.clicked.connect(self.open_pip)
            buttons.addWidget(pip_button)
        full_button = QPushButton("Fullscreen")
        full_button.clicked.connect(self.fullscreen)
        buttons.addWidget(full_button)
        buttons.addStretch(1)
        buttons.addWidget(QLabel("Volume"))
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setFixedWidth(150)
        self.volume.setValue(int(self.settings.get("volume", 70)))
        self.volume.valueChanged.connect(self.set_volume)
        buttons.addWidget(self.volume)
        controls.addLayout(buttons)
        outer.addWidget(self.transport)

        self.statusBar().showMessage("Ready — open a video or drag media into NOVA")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_playback_position)
        self.timer.start(400)
        self.init_nova_player()
        if not pip:
            self.add_paths(self.settings.get("recent_files", []), autoplay=False)
            self.make_menu()
        self.apply_shortcuts()
        self.apply_theme()
        hints = QApplication.styleHints()
        if hasattr(hints, "colorSchemeChanged"):
            hints.colorSchemeChanged.connect(self.on_system_theme_changed)
        self.theme_timer = QTimer(self)
        self.theme_timer.timeout.connect(self.on_system_theme_changed)
        self.theme_timer.start(2500)

    def build_pip_ui(self):
        self.library = None
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(390, 230)
        self.setMinimumSize(340, 195)
        shell = QFrame(objectName="PipShell")
        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(2, 2, 2, 2)
        shell_layout.setSpacing(1)

        self.video_card = QFrame(objectName="PipVideoCard")
        video_layout = QVBoxLayout(self.video_card)
        video_layout.setContentsMargins(0, 0, 0, 0)
        self.video = VideoSurface()
        video_layout.addWidget(self.video)
        shell_layout.addWidget(self.video_card, 1)

        self.transport = QFrame(objectName="PipTransport")
        row = QHBoxLayout(self.transport)
        row.setContentsMargins(6, 2, 6, 2)
        row.setSpacing(3)
        self.back_button = QPushButton("↶15")
        self.back_button.setToolTip("Back 15 seconds (←)")
        self.back_button.setObjectName("PipTransportButton")
        self.back_button.setFixedSize(36, 27)
        self.back_button.clicked.connect(lambda: self.seek_relative(-15))
        row.addWidget(self.back_button)
        self.play_button = QPushButton("▶")
        self.play_button.setObjectName("PipPlayButton")
        self.play_button.setFixedSize(30, 27)
        self.play_button.clicked.connect(self.toggle)
        row.addWidget(self.play_button)
        self.forward_button = QPushButton("15↷")
        self.forward_button.setToolTip("Forward 15 seconds (→)")
        self.forward_button.setObjectName("PipTransportButton")
        self.forward_button.setFixedSize(36, 27)
        self.forward_button.clicked.connect(lambda: self.seek_relative(15))
        row.addWidget(self.forward_button)
        self.elapsed = QLabel("00:00")
        self.elapsed.setObjectName("Hint")
        self.elapsed.setMinimumWidth(36)
        self.elapsed.setMaximumWidth(40)
        row.addWidget(self.elapsed)
        self.seek = QSlider(Qt.Orientation.Horizontal)
        self.seek.setRange(0, 0)
        self.seek.sliderReleased.connect(self.seek_to_slider)
        row.addWidget(self.seek, 1)
        self.total = QLabel("00:00")
        self.total.setObjectName("Hint")
        self.total.setMinimumWidth(36)
        self.total.setMaximumWidth(40)
        row.addWidget(self.total)
        row.addWidget(QLabel("♪"))
        self.volume = QSlider(Qt.Orientation.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setFixedWidth(42)
        self.volume.setValue(int(self.settings.get("volume", 70)))
        self.volume.valueChanged.connect(self.set_volume)
        row.addWidget(self.volume)
        self.return_button = QPushButton("↗")
        self.return_button.setToolTip("Return to NOVA")
        self.return_button.setObjectName("PipIconButton")
        self.return_button.setFixedSize(22, 27)
        self.return_button.clicked.connect(self.close)
        row.addWidget(self.return_button)
        close_button = QPushButton("×")
        close_button.setToolTip("Close mini player and return to NOVA")
        close_button.setObjectName("PipIconButton")
        close_button.setFixedSize(22, 27)
        close_button.clicked.connect(self.close)
        row.addWidget(close_button)
        shell_layout.addWidget(self.transport)

        self.setCentralWidget(shell)
        self.apply_glass_effects([shell])
        self.playback_badge = QLabel("NOVA Playback")
        self.statusBar().hide()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_playback_position)
        self.timer.start(400)

    def effective_theme(self):
        choice = self.settings.get("theme", "system")
        if choice in ("light", "dark"):
            return choice
        if os.name == "nt":
            try:
                import winreg
                key_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                    try:
                        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                    except OSError:
                        value, _ = winreg.QueryValueEx(key, "SystemUsesLightTheme")
                    return "light" if value else "dark"
            except (OSError, ImportError):
                pass
        try:
            scheme = QApplication.styleHints().colorScheme()
            return "dark" if scheme == Qt.ColorScheme.Dark else "light"
        except Exception:
            return "dark"

    def apply_glass_effects(self, widgets):
        """Give the translucent cards a soft, theme-aware floating edge."""
        color = QColor(128, 88, 182, 38) if self.active_theme == "dark" else QColor(95, 70, 145, 25)
        for widget in widgets:
            if widget is None:
                continue
            shadow = QGraphicsDropShadowEffect(widget)
            shadow.setBlurRadius(24 if self.pip else 30)
            shadow.setOffset(0, 5)
            shadow.setColor(color)
            widget.setGraphicsEffect(shadow)

    def apply_theme(self):
        self.active_theme = self.effective_theme()
        stylesheet = STYLE if self.active_theme == "dark" else LIGHT_STYLE
        if self.pip:
            stylesheet += self.build_pip_styles()
        self.setStyleSheet(stylesheet)
        if self.pip:
            self.apply_glass_effects([self.centralWidget()])
        else:
            self.apply_glass_effects([self.header, self.video_card, self.sidebar, self.transport])
        logo = logo_pixmap(self.active_theme, 32 if not self.pip else 28)
        self.setWindowIcon(QIcon(logo))
        if not self.pip:
            self.brand_icon.setPixmap(logo)

    def on_system_theme_changed(self, *_):
        if self.settings.get("theme", "system") == "system" and self.effective_theme() != self.active_theme:
            self.apply_theme()
            if self._pip_window:
                self._pip_window.settings.data["theme"] = "system"
                self._pip_window.apply_theme()

    def build_pip_styles(self):
        if self.active_theme == "light":
            return """
            QFrame#PipShell { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(255,255,255,232), stop:1 rgba(242,237,250,220)); border:1px solid rgba(130,105,168,80); border-radius:9px; }
            QFrame#PipTransport { background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 rgba(255,255,255,170), stop:1 rgba(238,231,249,205)); border:0; border-radius:7px; }
            QPushButton#PipIconButton { padding:0; border:0; background:transparent; color:#53476e; font-size:12pt; }
            QPushButton#PipIconButton:hover { background:rgba(160,130,205,35); }
            QPushButton#PipTransportButton { background:rgba(255,255,255,95); border:1px solid rgba(123,98,160,48); padding:0; color:#514263; border-radius:7px; }
            QPushButton#PipTransportButton:hover, QPushButton#PipIconButton:hover { background:rgba(190,170,220,90); }
            QPushButton#PipPlayButton { background:rgba(132,91,195,225); color:white; border:1px solid rgba(255,255,255,115); border-radius:7px; padding:0; }
            QPushButton#PipPlayButton:hover { background:rgba(151,112,210,245); }
            QFrame#PipVideoCard { background:#000; border:0; }
            """
        return """
        QFrame#PipShell { background:qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 rgba(31,24,43,225), stop:0.5 rgba(15,13,22,218), stop:1 rgba(38,28,51,225)); border:1px solid rgba(194,158,238,75); border-radius:9px; }
        QFrame#PipTransport { background:qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 rgba(39,31,53,196), stop:1 rgba(21,18,30,205)); border:0; border-radius:7px; }
        QPushButton#PipIconButton { padding:0; border:0; background:transparent; color:#e0d3f0; font-size:12pt; }
        QPushButton#PipIconButton:hover { background:rgba(185,145,230,34); }
        QPushButton#PipTransportButton { background:rgba(255,255,255,12); border:1px solid rgba(210,180,245,46); padding:0; color:#e0d3f0; border-radius:7px; }
        QPushButton#PipTransportButton:hover, QPushButton#PipIconButton:hover { background:rgba(180,140,225,42); }
        QPushButton#PipPlayButton { background:rgba(142,100,200,220); color:white; border:1px solid rgba(220,195,250,85); border-radius:7px; padding:0; }
        QPushButton#PipPlayButton:hover { background:rgba(167,124,221,240); }
        QSlider::groove:horizontal { height:3px; background:rgba(224,210,242,64); border-radius:2px; }
        QSlider::sub-page:horizontal { background:#b28add; border-radius:2px; }
        QSlider::handle:horizontal { background:#f6f0ff; width:10px; margin:-4px 0; border-radius:5px; }
        QFrame#PipVideoCard { background:#000; border:0; }
        """

    def init_nova_player(self):
        try:
            self.nova_player = NovaPlayer(self.video)
            self.nova_player.set_volume(self.volume.value())
            self.nova_player.set_muted(self.settings.get("muted", False))
            self.nova_player.set_playback_rate(self.settings.get("playback_rate", 1.0))
            saved_device = self.settings.get("audio_device_id")
            if saved_device:
                self.set_audio_device_by_id(saved_device, persist=False)
            self.playback_badge.setText("●  NOVA Playback ready")
            self.statusBar().showMessage("NOVA Playback ready")
            player = getattr(self.nova_player, "player", None)
            if player is not None and hasattr(player, "errorOccurred"):
                player.errorOccurred.connect(lambda *_: self.show_playback_error())
            if player is not None and hasattr(player, "positionChanged"):
                player.positionChanged.connect(self.on_position_changed)
                player.durationChanged.connect(self.on_duration_changed)
                player.mediaStatusChanged.connect(self.on_media_status_changed)
        except Exception as exc:
            self.nova_player = None
            self.playback_badge.setText("●  NOVA Playback unavailable")
            self.statusBar().showMessage("NOVA Playback could not start. Check your media setup and restart the player.")

    def show_playback_error(self):
        player = getattr(self.nova_player, "player", None)
        message = player.errorString() if player and hasattr(player, "errorString") else "Unsupported format or missing codec"
        self.statusBar().showMessage(f"Could not play this file: {message}")
        self.playback_badge.setText("●  NOVA Playback error")

    def on_position_changed(self, milliseconds):
        seconds = max(0, int(milliseconds / 1000))
        if not self.seek.isSliderDown():
            self.seek.setValue(seconds)
        self.elapsed.setText(self.format_time(seconds))

    def on_duration_changed(self, milliseconds):
        seconds = max(0, int(milliseconds / 1000))
        self.seek.setRange(0, seconds)
        self.total.setText(self.format_time(seconds))

    def on_media_status_changed(self, status):
        from PySide6.QtMultimedia import QMediaPlayer
        if status in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
            self.playback_badge.setText("●  NOVA Playback · ready")
            self.statusBar().showMessage(f"Playing: {self.media_title(self.current)}" if self.current else "Ready")
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            owner = self._pip_owner if self.pip and self._pip_owner else self
            owner.advance_after_end()
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            self.show_playback_error()

    def make_menu(self):
        media_menu = self.menuBar().addMenu("&Media")
        self._save_playlist_action = None
        for title, callback in (
            ("Open media files…", self.open_files),
            ("Open folder or removable media…", self.open_folder),
            ("Open network stream…", self.open_network_stream),
        ):
            self._add_menu_action(media_menu, title, callback)
        media_menu.addSeparator()
        self._add_menu_action(media_menu, "Open playlist (.m3u / .m3u8)…", self.open_playlist)
        self._save_playlist_action = self._add_menu_action(
            media_menu, "Save current list as playlist…", self.save_playlist)
        media_menu.addSeparator()
        self._add_menu_action(media_menu, "Quit", self.close)

        playback = self.menuBar().addMenu("&Playback")
        self._add_menu_action(playback, "Play / Pause", self.toggle).setShortcut(QKeySequence("Space"))
        self._stop_menu_action = self._add_menu_action(playback, "Stop", self.stop_playback)
        playback.addSeparator()
        self._previous_menu_action = self._add_menu_action(playback, "Previous item", self.previous_media)
        self._next_menu_action = self._add_menu_action(playback, "Next item", self.next_media)
        playback.addSeparator()
        self._add_menu_action(playback, "Skip backward 15 seconds", lambda: self.seek_relative(-15)).setShortcut(
            QKeySequence("Left"))
        self._add_menu_action(playback, "Skip forward 15 seconds", lambda: self.seek_relative(15)).setShortcut(
            QKeySequence("Right"))
        speed_menu = playback.addMenu("Playback speed")
        self._speed_group = QActionGroup(self)
        self._speed_group.setExclusive(True)
        for rate in (0.5, 0.75, 1.0, 1.25, 1.5, 2.0):
            action = QAction(f"{rate:g}×", self)
            action.setCheckable(True)
            action.setChecked(float(self.settings.get("playback_rate", 1.0)) == rate)
            action.triggered.connect(lambda checked=False, value=rate: self.set_playback_rate(value))
            self._speed_group.addAction(action)
            speed_menu.addAction(action)
        playback.addSeparator()
        repeat_menu = playback.addMenu("Repeat")
        self._repeat_group = QActionGroup(self)
        self._repeat_group.setExclusive(True)
        for mode, title in (("off", "Off"), ("one", "Repeat current item"), ("all", "Repeat playlist")):
            action = QAction(title, self)
            action.setCheckable(True)
            action.setChecked(self.settings.get("repeat_mode", "off") == mode)
            action.triggered.connect(lambda checked=False, value=mode: self.set_repeat_mode(value))
            self._repeat_group.addAction(action)
            repeat_menu.addAction(action)
        self._shuffle_action = QAction("Shuffle playlist", self)
        self._shuffle_action.setCheckable(True)
        self._shuffle_action.setChecked(bool(self.settings.get("shuffle", False)))
        self._shuffle_action.triggered.connect(self.set_shuffle)
        playback.addAction(self._shuffle_action)
        self._quit_after_action = QAction("Quit after playlist", self)
        self._quit_after_action.setCheckable(True)
        self._quit_after_action.setChecked(bool(self.settings.get("quit_after_playlist", False)))
        self._quit_after_action.triggered.connect(self.set_quit_after_playlist)
        playback.addAction(self._quit_after_action)

        audio = self.menuBar().addMenu("&Audio")
        self._audio_tracks_menu = audio.addMenu("Audio track")
        self._audio_devices_menu = audio.addMenu("Output device")
        audio.addSeparator()
        self._mute_action = QAction("Mute", self)
        self._mute_action.setCheckable(True)
        self._mute_action.triggered.connect(self.toggle_mute)
        audio.addAction(self._mute_action)
        self._add_menu_action(audio, "Volume up", lambda: self.volume.setValue(min(100, self.volume.value() + 5)))
        self._add_menu_action(audio, "Volume down", lambda: self.volume.setValue(max(0, self.volume.value() - 5)))
        self._add_menu_action(audio, "Set volume to 100%", lambda: self.volume.setValue(100))
        audio.aboutToShow.connect(self.refresh_audio_menus)

        video = self.menuBar().addMenu("&Video")
        self._add_menu_action(video, "Fullscreen", self.fullscreen)
        video.addSeparator()
        self._video_tracks_menu = video.addMenu("Video track")
        video.aboutToShow.connect(self.refresh_video_menu)
        video.addSeparator()
        self._aspect_group = QActionGroup(self)
        self._aspect_group.setExclusive(True)
        for title, mode in (
            ("Fit video (keep proportions)", Qt.AspectRatioMode.KeepAspectRatio),
            ("Stretch video to fill", Qt.AspectRatioMode.IgnoreAspectRatio),
        ):
            action = QAction(title, self)
            action.setCheckable(True)
            action.setChecked(self.video.aspectRatioMode() == mode)
            action.triggered.connect(lambda checked=False, value=mode: self.video.setAspectRatioMode(value))
            self._aspect_group.addAction(action)
            video.addAction(action)

        subtitles = self.menuBar().addMenu("&Subtitle")
        self._add_menu_action(subtitles, "Load subtitle file…", self.open_subtitle)
        self._clear_external_subtitles_action = self._add_menu_action(
            subtitles, "Turn off external subtitles", self.clear_external_subtitles)
        self._subtitle_tracks_menu = subtitles.addMenu("Embedded subtitle track")
        subtitles.aboutToShow.connect(self.refresh_subtitle_menu)

        tools = self.menuBar().addMenu("&Tools")
        self._add_menu_action(tools, "Settings…", self.show_settings)
        self._add_menu_action(tools, "Plugin manager…", self.show_plugins)
        self.equalizer_info_action = self._add_menu_action(
            tools, "Equalizer (not available)", lambda: None)
        self.equalizer_info_action.setEnabled(False)
        self.equalizer_info_action.setToolTip(
            "The current NOVA playback adapter does not provide audio equalizer processing.")

        view = self.menuBar().addMenu("&View")
        self._pip_menu_action = self._add_menu_action(view, "Picture in Picture", self.open_pip)
        self._add_menu_action(view, "Fullscreen", self.fullscreen)

        help_menu = self.menuBar().addMenu("&Help")
        self._add_menu_action(help_menu, "About NOVA Player", self.show_about)
        self._add_menu_action(help_menu, "Keyboard shortcuts", self.show_shortcuts)
        self._refresh_menu_states()

    def _add_menu_action(self, menu, title, callback):
        action = QAction(title, self)
        action.triggered.connect(callback)
        menu.addAction(action)
        return action

    def _refresh_menu_states(self):
        has_media = bool(self.files)
        for name in ("_pip_menu_action",):
            action = getattr(self, name, None)
            if action:
                action.setEnabled(has_media and not self.pip)
        for name in ("_save_playlist_action", "_stop_menu_action", "_previous_menu_action", "_next_menu_action",
                     "_shuffle_action", "_repeat_group", "_quit_after_action"):
            action = getattr(self, name, None)
            if action:
                if isinstance(action, QActionGroup):
                    for item in action.actions():
                        item.setEnabled(has_media)
                else:
                    action.setEnabled(has_media)
        clear_action = getattr(self, "_clear_external_subtitles_action", None)
        if clear_action:
            clear_action.setEnabled(bool(self.external_subtitles))

    def _active_engine(self):
        if not self.pip and self._pip_window:
            return self._pip_window.nova_player
        return self.nova_player

    def refresh_audio_menus(self):
        engine = self._active_engine()
        self._audio_tracks_menu.clear()
        qt_player = getattr(engine, "player", None)
        tracks = qt_player.audioTracks() if qt_player and hasattr(qt_player, "audioTracks") else []
        if tracks:
            active = qt_player.activeAudioTrack()
            for index, metadata in enumerate(tracks):
                title = metadata.stringValue(QMediaMetaData.Key.Title)
                language = metadata.stringValue(QMediaMetaData.Key.Language)
                label = " — ".join(value for value in (title, language) if value) or f"Audio track {index + 1}"
                action = QAction(label, self)
                action.setCheckable(True)
                action.setChecked(index == active)
                action.triggered.connect(lambda checked=False, track=index: self.select_audio_track(track))
                self._audio_tracks_menu.addAction(action)
        else:
            action = self._audio_tracks_menu.addAction("No audio tracks available")
            action.setEnabled(False)

        self._audio_devices_menu.clear()
        devices = QMediaDevices.audioOutputs()
        current_device = engine.audio.device() if engine and hasattr(engine, "audio") else None
        if devices:
            group = QActionGroup(self)
            group.setExclusive(True)
            for device in devices:
                action = QAction(device.description(), self)
                action.setCheckable(True)
                action.setChecked(current_device is not None and bytes(device.id()) == bytes(current_device.id()))
                device_id = bytes(device.id()).decode("utf-8", errors="replace")
                action.triggered.connect(lambda checked=False, value=device_id: self.set_audio_device_by_id(value))
                group.addAction(action)
                self._audio_devices_menu.addAction(action)
        else:
            action = self._audio_devices_menu.addAction("No output devices available")
            action.setEnabled(False)
        self._mute_action.setChecked(bool(engine and engine.is_muted()))

    def refresh_video_menu(self):
        self._video_tracks_menu.clear()
        engine = self._active_engine()
        qt_player = getattr(engine, "player", None)
        tracks = qt_player.videoTracks() if qt_player and hasattr(qt_player, "videoTracks") else []
        if not tracks:
            action = self._video_tracks_menu.addAction("No selectable video tracks")
            action.setEnabled(False)
            return
        active = qt_player.activeVideoTrack()
        group = QActionGroup(self)
        group.setExclusive(True)
        for index, metadata in enumerate(tracks):
            title = metadata.stringValue(QMediaMetaData.Key.Title)
            language = metadata.stringValue(QMediaMetaData.Key.Language)
            label = " — ".join(value for value in (title, language) if value) or f"Video track {index + 1}"
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(index == active)
            action.triggered.connect(lambda checked=False, track=index: self.select_video_track(track))
            group.addAction(action)
            self._video_tracks_menu.addAction(action)

    def select_video_track(self, index):
        engine = self._active_engine()
        qt_player = getattr(engine, "player", None)
        if qt_player and hasattr(qt_player, "setActiveVideoTrack"):
            qt_player.setActiveVideoTrack(index)

    def select_audio_track(self, index):
        engine = self._active_engine()
        qt_player = getattr(engine, "player", None)
        if qt_player and hasattr(qt_player, "setActiveAudioTrack"):
            qt_player.setActiveAudioTrack(index)

    def refresh_subtitle_menu(self):
        self._subtitle_tracks_menu.clear()
        engine = self._active_engine()
        qt_player = getattr(engine, "player", None)
        tracks = qt_player.subtitleTracks() if qt_player and hasattr(qt_player, "subtitleTracks") else []
        disable = self._subtitle_tracks_menu.addAction("Disable subtitles")
        disable.triggered.connect(lambda: qt_player and qt_player.setActiveSubtitleTrack(-1))
        if not tracks:
            action = self._subtitle_tracks_menu.addAction("No embedded subtitles")
            action.setEnabled(False)
            return
        active = qt_player.activeSubtitleTrack()
        for index, metadata in enumerate(tracks):
            title = metadata.stringValue(QMediaMetaData.Key.Title)
            language = metadata.stringValue(QMediaMetaData.Key.Language)
            label = " — ".join(value for value in (title, language) if value) or f"Subtitle track {index + 1}"
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(index == active)
            action.triggered.connect(lambda checked=False, track=index: self.select_subtitle_track(track))
            self._subtitle_tracks_menu.addAction(action)

    def select_subtitle_track(self, index):
        engine = self._active_engine()
        qt_player = getattr(engine, "player", None)
        if qt_player and hasattr(qt_player, "setActiveSubtitleTrack"):
            qt_player.setActiveSubtitleTrack(index)

    def set_audio_device_by_id(self, device_id, persist=True):
        device = next((item for item in QMediaDevices.audioOutputs()
                       if bytes(item.id()).decode("utf-8", errors="replace") == device_id), None)
        if device is None:
            return False
        targets = [self.nova_player]
        if self._pip_window:
            targets.append(self._pip_window.nova_player)
        for engine in targets:
            if engine and hasattr(engine, "set_audio_device"):
                engine.set_audio_device(device)
        if persist and not self.pip:
            self.settings.set("audio_device_id", device_id)
        return True

    def toggle_mute(self, muted):
        engine = self._active_engine()
        if engine:
            engine.set_muted(muted)
            if not self.pip:
                self.settings.set("muted", muted)

    def show_about(self):
        from . import __version__
        QMessageBox.about(
            self,
            "About NOVA Player",
            f"NOVA Player {__version__}\n"
            "Developed by Nayan Patel\n\n"
            "About playlists\n"
            "M3U and M3U8 are small text playlist files. They list the locations of songs, videos, or stream URLs; "
            "they do not contain or copy the media itself. Open playlist loads that list into NOVA. "
            "Save current list as playlist creates a file you can reopen or share with the media it references.\n\n"
            "Playback and controls\n"
            "NOVA Playback uses the media components available with the app and operating system. Supported formats vary by device. "
            "The menus include play/stop, next/previous, seeking, speed, repeat, shuffle, audio/video track selection, "
            "output device, volume, subtitles, fullscreen, and picture in picture.\n\n"
            "Keyboard: Space = play/pause; Left/Right = seek 15 seconds; Up/Down = change volume; "
            "F = fullscreen; P = picture in picture.\n\n"
            "Disc playback, media conversion, stream output, visualizations, and real-time equalizer processing "
            "are not available in this build. Third-party notices and license files are beside the app.",
        )

    def show_shortcuts(self):
        QMessageBox.information(
            self, "NOVA Player keyboard shortcuts",
            "Space  Play / pause\n"
            "Left / Right  Seek backward / forward 15 seconds\n"
            "Up / Down  Volume up / down\n"
            "F  Fullscreen\n"
            "P  Picture in picture\n"
            "Escape  Leave fullscreen",
        )

    def apply_shortcuts(self):
        shortcuts = self.settings.get("shortcuts", {})
        bindings = [("play_pause", self.toggle, "Space"),
                    ("seek_forward", lambda: self.seek_relative(15), "Right"),
                    ("seek_backward", lambda: self.seek_relative(-15), "Left"),
                    ("volume_up", lambda: self.volume.setValue(min(100, self.volume.value() + 5)), "Up"),
                    ("volume_down", lambda: self.volume.setValue(max(0, self.volume.value() - 5)), "Down")]
        if not self.pip:
            bindings += [("fullscreen", self.fullscreen, "F"), ("pip", self.open_pip, "P")]
        for key, fn, default in bindings:
            action = QAction(self)
            action.setShortcut(QKeySequence(shortcuts.get(key, default)))
            action.setShortcutContext(Qt.ShortcutContext.WindowShortcut)
            action.triggered.connect(fn)
            self.addAction(action)

    def seek_relative(self, seconds):
        target_player = self._pip_window.nova_player if not self.pip and self._pip_window else self.nova_player
        if not target_player or not self.current or not hasattr(target_player, "seek"):
            return
        try:
            state = target_player.state()
            target = max(0, int(state.get("position", 0)) + seconds)
            duration = target_player.duration() if hasattr(target_player, "duration") else 0
            if duration:
                target = min(duration, target)
            target_player.seek(target)
            self.statusBar().showMessage(f"Seeked to {self.format_time(target)}")
        except Exception as exc:
            self.statusBar().showMessage(f"Seek failed: {exc}")

    def open_files(self):
        patterns = " ".join(f"*{extension}" for extension in sorted(MEDIA))
        files, _ = QFileDialog.getOpenFileNames(
            self, "Open media files", "", f"Media files ({patterns});;All files (*)")
        self.add_paths(files)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Open folder")
        if folder:
            self.add_paths([folder])

    def open_network_stream(self):
        value, accepted = QInputDialog.getText(
            self, "Open network stream", "Stream URL (HTTP, HTTPS, RTSP, or RTMP):")
        if not accepted or not value.strip():
            return
        if not is_network_url(value):
            QMessageBox.warning(self, "Network stream", "Enter a valid HTTP, HTTPS, RTSP, or RTMP URL.")
            return
        self.add_paths([value.strip()])

    @staticmethod
    def media_title(location):
        if is_network_url(location):
            from urllib.parse import urlsplit
            parsed = urlsplit(str(location))
            return Path(parsed.path).name or parsed.hostname or str(location)
        return Path(location).name

    def add_paths(self, paths, autoplay=True):
        added = []
        for raw in paths:
            value = str(raw).strip()
            if not value:
                continue
            if is_network_url(value):
                batch = [value]
            else:
                p = Path(value).expanduser()
                batch = ([x for x in p.rglob("*") if x.is_file() and x.suffix.lower() in MEDIA]
                         if p.is_dir() else ([p] if p.is_file() and p.suffix.lower() in MEDIA else []))
            for item in batch:
                full = item if isinstance(item, str) else str(item.resolve())
                if full not in self.files:
                    self.files.append(full)
                    added.append(full)
                    if self.library:
                        title = self.media_title(full) if is_network_url(full) else audio_metadata(full)["title"]
                        self.library.addItem(title)
        if self.library and self.files:
            self.library_hint.setText(f"{len(self.files)} items")
        if not self.pip:
            self.settings.set("recent_files", self.files[-500:])
        if added and not self.pip and autoplay:
            self.play_index(self.files.index(added[0]))
        self._refresh_menu_states()

    def play_index(self, index):
        if not 0 <= index < len(self.files):
            return
        if not self.pip and self._pip_window:
            self._switching_media = True
            self._pip_window.close()
            self._switching_media = False
        self.current = self.files[index]
        self.external_subtitles = []
        self.external_subtitle_path = None
        self.video.subtitle_label.clear()
        self.video.subtitle_label.hide()
        self._refresh_menu_states()
        if self.library:
            self.library.setCurrentRow(index)
        if not self.nova_player:
            self.statusBar().showMessage("NOVA Playback could not start. Check your media setup and try again.")
            return
        try:
            self.nova_player.load(self.current)
            self.paused = False
            self.play_button.setText("Ⅱ" if self.pip else "Ⅱ  Pause")
            self.statusBar().showMessage(f"Opening: {self.media_title(self.current)}")
            self.playback_badge.setText("●  NOVA Playback · loading")
            self.set_volume(self.volume.value())
        except Exception as exc:
            self.statusBar().showMessage(f"Could not play {self.media_title(self.current)}: {exc}")
            self.playback_badge.setText("●  NOVA Playback error")

    def toggle(self):
        if not self.pip and self._pip_window:
            self._pip_window.toggle()
            return
        if not self.nova_player or not self.current:
            if self.files:
                self.play_index(self.files.index(self.current) if self.current in self.files else 0)
            else:
                self.open_files()
            return
        self.paused = not self.paused
        self.nova_player.pause(self.paused)
        self.play_button.setText(("▶" if self.paused else "Ⅱ") if self.pip else ("▶  Play" if self.paused else "Ⅱ  Pause"))
        self.statusBar().showMessage("Paused" if self.paused else f"Playing: {self.media_title(self.current)}")

    def stop_playback(self):
        engine = self._active_engine()
        if engine:
            engine.stop()
            self.paused = True
            self.play_button.setText("▶" if self.pip else "▶  Play")
            self.statusBar().showMessage("Stopped")

    def previous_media(self):
        if not self.files:
            return
        index = self.files.index(self.current) if self.current in self.files else 0
        if index == 0 and self.settings.get("repeat_mode", "off") == "all":
            index = len(self.files) - 1
        else:
            index = max(0, index - 1)
        self.play_index(index)

    def next_media(self):
        if not self.files:
            return
        index = self.files.index(self.current) if self.current in self.files else -1
        if index + 1 < len(self.files):
            self.play_index(index + 1)
        elif self.settings.get("repeat_mode", "off") == "all":
            self.play_index(0)

    def set_repeat_mode(self, mode):
        if mode not in {"off", "one", "all"}:
            return
        self.settings.set("repeat_mode", mode)
        self.statusBar().showMessage({
            "off": "Repeat off", "one": "Repeating current item", "all": "Repeating playlist",
        }[mode])

    def set_shuffle(self, enabled):
        self.settings.set("shuffle", bool(enabled))
        self.statusBar().showMessage("Shuffle on" if enabled else "Shuffle off")

    def set_quit_after_playlist(self, enabled):
        self.settings.set("quit_after_playlist", bool(enabled))
        self.statusBar().showMessage("Will quit after playlist" if enabled else "Quit after playlist off")

    def advance_after_end(self):
        if not self.files or self.current not in self.files:
            return
        index = self.files.index(self.current)
        repeat_mode = self.settings.get("repeat_mode", "off")
        if repeat_mode == "one":
            self.play_index(index)
            return
        if self.settings.get("shuffle", False) and len(self.files) > 1:
            choices = [item for item in range(len(self.files)) if item != index]
            self.play_index(random.choice(choices))
            return
        if index + 1 < len(self.files):
            self.play_index(index + 1)
        elif repeat_mode == "all":
            self.play_index(0)
        elif self.settings.get("quit_after_playlist", False):
            self.close()
        else:
            self.paused = True
            self.play_button.setText("▶" if self.pip else "▶  Play")
            self.playback_badge.setText("●  NOVA Playback · playlist finished")
            self.statusBar().showMessage("Playlist finished")

    def set_playback_rate(self, rate):
        engine = self._active_engine()
        if engine:
            try:
                engine.set_playback_rate(rate)
                if not self.pip:
                    self.settings.set("playback_rate", float(rate))
                self.statusBar().showMessage(f"Playback speed: {rate:g}×")
            except Exception as exc:
                self.statusBar().showMessage(f"Could not set playback speed: {exc}")

    def set_volume(self, value):
        target = self._pip_window.nova_player if not self.pip and self._pip_window else self.nova_player
        if target:
            try:
                target.set_volume(value)
            except Exception:
                pass
        if not self.pip:
            self.settings.set("volume", value)

    def refresh_playback_position(self):
        if not self.nova_player or not self.current:
            return
        try:
            state = self.nova_player.state()
            position = max(0, int(state.get("position", 0)))
            if not self.seek.isSliderDown():
                self.seek.setValue(position)
            self.elapsed.setText(self.format_time(position))
            duration = self.nova_player.duration() if hasattr(self.nova_player, "duration") else 0
            self.total.setText(self.format_time(duration))
            if duration:
                self.seek.setRange(0, duration)
            self.playback_badge.setText(f"●  NOVA Playback · {'paused' if state.get('paused') else 'playing'}")
            self.update_external_subtitle(position * 1000)
        except Exception:
            pass

    def update_external_subtitle(self, position_ms):
        text = next((cue[2] for cue in self.external_subtitles
                     if cue[0] <= position_ms < cue[1]), "")
        if text:
            self.video.subtitle_label.setText(text)
            self.video.subtitle_label.show()
            self.video.subtitle_label.raise_()
        else:
            self.video.subtitle_label.clear()
            self.video.subtitle_label.hide()

    @staticmethod
    def format_time(seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 3600:02d}:{(seconds // 60) % 60:02d}:{seconds % 60:02d}" if seconds >= 3600 else f"{seconds // 60:02d}:{seconds % 60:02d}"

    def seek_to_slider(self):
        target = self._pip_window.nova_player if not self.pip and self._pip_window else self.nova_player
        if target and hasattr(target, "seek"):
            target.seek(self.seek.value())

    def open_subtitle(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load subtitles", "", "Subtitles (*.srt *.vtt);;All files (*)")
        if path and self.current:
            try:
                cues = read_subtitles(path)
                if not cues:
                    raise ValueError("No readable subtitle cues were found in this file.")
                target = self._pip_window if not self.pip and self._pip_window else self
                target.external_subtitles = cues
                target.external_subtitle_path = path
                self.settings.set("last_subtitle", path)
                self.statusBar().showMessage(f"Loaded subtitles: {Path(path).name}")
                self._refresh_menu_states()
            except Exception as exc:
                QMessageBox.warning(self, "Subtitles", str(exc))

    def clear_external_subtitles(self):
        self.external_subtitles = []
        self.external_subtitle_path = None
        self.video.subtitle_label.clear()
        self.video.subtitle_label.hide()
        self._refresh_menu_states()
        if not self.pip and self._pip_window:
            self._pip_window.clear_external_subtitles()
        self.statusBar().showMessage("External subtitles turned off")

    def show_equalizer(self):
        QMessageBox.information(
            self, "Equalizer unavailable",
            "This NOVA playback build does not expose real-time audio equalizer processing.")

    def apply_eq(self, _value):
        return None

    def fullscreen(self):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self.outer_layout.setContentsMargins(0, 0, 0, 0)
            self.outer_layout.setSpacing(0)
            self.header.hide()
            self.transport.hide()
            if self.sidebar: self.sidebar.hide()
            self.menuBar().hide()
            self.statusBar().hide()
            self.video_card.setStyleSheet("QFrame#VideoCard { background:#000; border:0; border-radius:0; }")
            self.video.setStyleSheet("border:0; border-radius:0; background:#000;")
            self.showFullScreen()
        else:
            self.showNormal()
            self.outer_layout.setContentsMargins(18, 15, 18, 12)
            self.outer_layout.setSpacing(13)
            self.header.show()
            self.transport.show()
            if self.sidebar: self.sidebar.show()
            self.menuBar().show()
            self.statusBar().show()
            self.video_card.setStyleSheet("")
            self.video.setStyleSheet("")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape and self._fullscreen:
            self.fullscreen()
            event.accept()
            return
        super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        self.add_paths([url.toLocalFile() if url.isLocalFile() else url.toString()
                        for url in event.mimeData().urls()])

    def open_playlist(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open playlist", "", "Playlist files (*.m3u *.m3u8);;All files (*)")
        if path:
            try:
                entries = read_m3u(path)
                if not entries:
                    self.statusBar().showMessage("The selected playlist has no media entries.")
                    return
                self.files.clear()
                if self.library:
                    self.library.clear()
                self.current = None
                self.add_paths(entries)
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, "Open playlist", str(exc))

    def save_playlist(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save playlist", "NOVA playlist.m3u",
            "Playlist files (*.m3u *.m3u8);;All files (*)")
        if path:
            if not Path(path).suffix:
                path += ".m3u"
            write_m3u(path, self.files)
            self.statusBar().showMessage(f"Playlist saved: {Path(path).name}")

    def show_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        form = QFormLayout(dialog)
        theme = QComboBox()
        theme.addItem("System", "system")
        theme.addItem("Light", "light")
        theme.addItem("Dark", "dark")
        current_theme = self.settings.get("theme", "system")
        theme.setCurrentIndex(max(0, theme.findData(current_theme)))
        form.addRow("Appearance", theme)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec():
            self.settings.data["theme"] = theme.currentData()
            self.settings.save()
            self.apply_theme()
            if self._pip_window:
                self._pip_window.settings.data["theme"] = theme.currentData()
                self._pip_window.apply_theme()
    def show_plugins(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Plugin manager")
        form = QVBoxLayout(dialog)
        rows = QListWidget()
        form.addWidget(rows)

        def refresh():
            rows.clear()
            for item in discover_plugins(self.settings.get("plugin_paths", [])):
                rows.addItem(f"{item['name']} — {item['kind']} — {item['path']}")

        actions = QHBoxLayout()
        add = QPushButton("Add directory…")
        remove = QPushButton("Remove selected")
        actions.addWidget(add)
        actions.addWidget(remove)
        form.addLayout(actions)

        def add_path():
            path = QFileDialog.getExistingDirectory(dialog, "Add plugin directory")
            if path:
                paths = self.settings.get("plugin_paths", [])
                if path not in paths:
                    paths.append(path)
                    self.settings.set("plugin_paths", paths)
                refresh()

        def remove_path():
            selected = rows.currentItem()
            if selected:
                candidate = Path(selected.text().split(" — ")[-1])
                paths = self.settings.get("plugin_paths", [])
                self.settings.set("plugin_paths", [p for p in paths if Path(p) not in (candidate, candidate.parent)])
                refresh()

        add.clicked.connect(add_path)
        remove.clicked.connect(remove_path)
        refresh()
        dialog.exec()

    def open_pip(self):
        if self.pip or not self.current:
            return
        if self._pip_window:
            self._pip_window.show()
            self._pip_window.raise_()
            self._pip_window.activateWindow()
            return
        raw = self.nova_player.state() if self.nova_player and hasattr(self.nova_player, "state") else {}
        state = PlaybackState(self.current, raw.get("position", 0), raw.get("paused", False),
                              self.volume.value(), raw.get("subtitle"), raw.get("subtitle_offset", 0))
        if self.nova_player:
            try:
                self.nova_player.pause(True)
                self.paused = True
                self.play_button.setText("▶  Play")
            except Exception:
                pass
        pip = PlayerWindow(Settings(), pip=True)
        pip._pip_owner = self
        pip.files = [self.current]
        pip.current = self.current
        snapshot = handoff(state, pip)
        pip.play_index(0)
        pip.external_subtitles = list(self.external_subtitles)
        pip.external_subtitle_path = self.external_subtitle_path
        pip.update_external_subtitle(snapshot.position * 1000)
        if not pip.nova_player:
            pip._pip_owner = None
            pip.close()
            try:
                self.nova_player.seek(snapshot.position)
                self.nova_player.pause(snapshot.paused)
            except Exception:
                pass
            self.paused = snapshot.paused
            self.play_button.setText("▶  Play" if self.paused else "Ⅱ  Pause")
            self.statusBar().showMessage("Mini-player could not start; continuing in NOVA")
            return
        try:
            pip.nova_player.seek(snapshot.position)
            pip.nova_player.pause(snapshot.paused)
        except Exception:
            pass
        pip.volume.setValue(snapshot.volume)
        pip.show()
        pip.raise_()
        pip.activateWindow()
        self._pip_window = pip
        self.hide()

    def on_pip_closed(self, state):
        self._pip_window = None
        if self._closing or self._switching_media or not self.nova_player or not self.current:
            return
        try:
            self.nova_player.seek(max(0, state.get("position", 0)))
            self.nova_player.pause(bool(state.get("paused", False)))
            self.paused = bool(state.get("paused", False))
            self.play_button.setText("▶  Play" if self.paused else "Ⅱ  Pause")
            self.statusBar().showMessage("Returned to NOVA playback")
            self.showNormal()
            self.raise_()
            self.activateWindow()
        except Exception as exc:
            self.statusBar().showMessage(f"Could not return playback: {exc}")

    def closeEvent(self, event):
        if not self.pip:
            self._closing = True
            if self._pip_window:
                self._pip_window.close()
                self._pip_window = None
        elif self._pip_owner:
            state = self.nova_player.state() if self.nova_player and hasattr(self.nova_player, "state") else {}
            if self.nova_player:
                try:
                    self.nova_player.pause(True)
                except Exception:
                    pass
            self._pip_owner.on_pip_closed(state)
        if self.nova_player:
            try:
                self.nova_player.close()
            except Exception:
                pass
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NOVA Player")
    app.setStyle("Fusion")
    window = PlayerWindow()
    window.show()
    return app.exec()
