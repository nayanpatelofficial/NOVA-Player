# NOVA Player 1.10.0

NOVA Player is a desktop music and video player developed by **Nayan Patel**. It uses Qt Multimedia for playback. VLC and MPV are not included or used. Supported formats depend on the bundled Qt media components and the target operating system.

## Install on another computer

Download the matching package from **GitHub Releases**:

- **Windows 10/11, 64-bit:** run `NOVA-Player-Setup.exe`. Python is not required. The portable ZIP can be extracted and launched without installing.
- **Linux x64:** extract `NOVA-Player-v1.10.0-linux-x64.tar.gz`, enter the extracted folder, and run `bash ./install-linux.sh`. It installs for the current user under `~/.local/opt/nova-player`; administrator access is not required. Use `bash ./uninstall-linux.sh` from the same extracted folder to remove it.
- **macOS Intel or Apple silicon:** extract the matching ZIP and move `NOVAPlayer.app` into Applications. The app is not signed or notarized; macOS may require opening it through Finder's **Open** action.

Windows packages target 64-bit Windows 10/11. The Windows installer is not code-signed, so Windows may show an unknown-publisher or SmartScreen warning. This is a publisher-trust warning; users should not import a development certificate for the release package.

The Linux package is built on Ubuntu 24.04 for x64. It bundles NOVA and its Qt runtime, but Linux system graphics/audio/multimedia libraries can still vary by distribution. macOS builds are produced on separate Intel and Apple silicon runners. Try a package on the target computer before deploying it broadly.

## Run from source

Install 64-bit Python 3.13, extract the source archive, then run these commands in PowerShell from the project folder:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

On Linux or macOS, create a virtual environment with Python 3.13, install `requirements.txt`, and run `python main.py`. TinyTag reads supported audio metadata and embedded artwork. Playback format availability depends on media codecs in the operating system runtime.

## Build packages

PyInstaller builds for the operating system where it runs; it does not cross-compile. Build the Windows installer on Windows:

```powershell
python -m pip install -r requirements.txt -r requirements-build.txt
choco install innosetup --yes --no-progress
.\scripts\build_windows.ps1
```

Build a Linux or macOS package on that operating system:

```sh
python3 -m pip install -r requirements.txt -r requirements-build.txt
python3 scripts/build_portable.py
```

The GitHub Actions workflow runs unit tests, builds Windows x64, Linux x64, macOS Intel, and macOS Apple silicon packages, and uploads them as workflow artifacts. Pushing a `v*` tag also creates a GitHub Release with all packages attached.

## Features and controls

- Media library, multi-file/folder open, drag and drop, recent files, and network stream URLs
- M3U/M3U8 playlists, metadata and artwork, speed, repeat, shuffle, track/output selection, volume, and mute
- Embedded subtitle selection and external SRT/VTT subtitles
- Video fit/stretch, fullscreen, keyboard shortcuts, picture in picture, settings, themes, and plugin discovery
- Menus for Media, Playback, Audio, Video, Subtitle, Tools, View, and Help

An **M3U/M3U8 playlist is a small text file containing media paths or stream links**; it does not store or copy the songs/videos. Use **Media → Open playlist (.m3u / .m3u8)…** to load one, or **Media → Save current list as playlist…** to create one. Local paths are written relative to the playlist folder when possible, so the playlist can travel with its referenced media.

The current playback adapter does not provide disc playback, capture-device recording, media conversion, stream output, visualizations, or real-time equalizer processing. Those functions are not presented as working choices. Codec support, live playback, subtitle rendering on every video surface, and package installation require testing on each target operating system and are not claimed as validated here.

## Legal and validation notes

Third-party notices and license files are included in `THIRD_PARTY_NOTICES.md` and `licenses/`. Review the applicable Qt/PySide6 and FFmpeg terms before redistribution. No VLC or MPV libraries are part of this project. Codec patent obligations are separate from software licenses.

This repository intentionally has **no source-code license**, as requested. Public visibility on GitHub does not grant other users permission to reuse, modify, or redistribute the source beyond GitHub's default viewing rights. Third-party components retain their own license terms.

Unit tests cover settings, playlist parsing, subtitle parsing, playback state, metadata, and plugin discovery. This development environment is Windows; Linux and macOS packages are configured to build on their matching GitHub runners and have not been runtime-tested here. Real media playback, cross-PC installation, and Microsoft Store certification are not claimed as validated.
