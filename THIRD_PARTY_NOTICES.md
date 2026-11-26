# NOVA Player v1.10.0 - third-party component inventory

NOVA's app code is separate from these components. This build configuration uses:

- Qt for Python / PySide6 6.12.0 (Essentials, Addons and Shiboken6), distributed under the component-specific LGPLv3/GPLv3 or Qt Commercial terms. Select and comply with the applicable license before distribution. Keep the exact Qt license files and third-party notices from the installed wheels with the packaged app.
- TinyTag 2.3.0 for reading audio metadata and embedded cover images, under the MIT license. The wheel's LICENSE file must be included in binary distributions.
- Python 3.13 and PyInstaller 6.x are used by the reproducible release workflow; include the exact Python and PyInstaller notices/licenses in the packaged distribution.
- Qt Multimedia 6.12.0's FFmpeg 9.0.1 media backend is present in the tested Windows package (`ffmpegmediaplugin.dll`, `avcodec-63.dll`, `avformat-63.dll`, and `avutil-61.dll`). Qt's Windows FFmpeg build is LGPLv2.1-or-later and uses additional BSD, ISC, MIT, and MPL-2.0 licensed components. Review Qt's [Qt Multimedia 6.12 license and attribution page](https://doc.qt.io/qt-6.12/qtmultimedia-index.html), [FFmpeg 9.0.1 attribution](https://doc.qt.io/qt-6.12/qtmultimedia-attribution-ffmpeg.html), and [Qt third-party component list](https://doc.qt.io/qt-6/licenses-used-in-qt.html) for the exact component notices and sources.

No VLC or MPV components are used or packaged by this project. Qt Multimedia uses Qt's platform media backend and may bundle FFmpeg components on Windows; this is disclosed here rather than represented as an in-house codec engine.

This inventory is a packaging aid, not a complete legal opinion or proof of license compliance. The exact license files and corresponding source must match the binary artifact you submit. Review Qt's LGPL/GPL or commercial terms and the specific FFmpeg notices before publishing. Applicable codec patent obligations are separate from these software licenses. See [Qt for Python commercial-use guidance](https://doc.qt.io/qtforpython-6/commercial/index.html) and TinyTag's included MIT LICENSE.
