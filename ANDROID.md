# NOVA Player on Android

The Android build targets 64-bit ARM (`arm64-v8a`) phones and tablets. It uses NOVA's Qt Multimedia playback adapter and Android media components, so format and codec support depends on the Android version and device.

The Android layout uses a portrait-friendly player screen, a native media picker, and touch-sized playback controls. Desktop floating picture-in-picture is not offered on Android. When a file is selected through Android's document picker, NOVA passes the returned `content://` URI to the Android media backend.

## Install the APK

Download `NOVA-Player-Android-arm64.apk` from the GitHub Actions artifact or a GitHub Release, copy it to the Android device, and open it. Android may ask you to allow installation from the app used to open the downloaded APK. This is a debug/sideload package and is not signed for Google Play distribution.

## Build locally

Build on Linux or macOS with Python 3.10–3.14, JDK 21, Android SDK platform-tools, Android platform 35, build-tools 35.0.0, and NDK 28.2.13676358. The workflow builds community Qt/PySide6 Android wheels from source, so it does not need Qt commercial account credentials. It uses Qt 6.12.0 for both host and Android.

```sh
python3 -m venv .venv-android
. .venv-android/bin/activate
python -m pip install -r requirements.txt
python -m pip install "git+https://github.com/miurahr/aqtinstall.git@8e4ea786f8a4f9dc578516738a137dec80a0362c"

QT_ROOT="$HOME/Qt"
python -m aqt install-qt linux desktop 6.12.0 gcc_64 -O "$QT_ROOT" -m qtmultimedia
python -m aqt install-qt all_os android 6.12.0 android_arm64_v8a -O "$QT_ROOT" -m qtmultimedia

git clone --depth 1 --branch 6.12 https://github.com/pyside/pyside-setup.git /tmp/pyside-setup
cd /tmp/pyside-setup
python -m pip install -r requirements.txt -r tools/cross_compile_android/requirements.txt
python tools/cross_compile_android/main.py --plat-name=aarch64 \
  --qt-install-path="$QT_ROOT/6.12.0" \
  --ndk-path="$ANDROID_HOME/ndk/28.2.13676358" \
  --sdk-path="$ANDROID_HOME" --auto-accept-license --skip-update

cd /path/to/NOVA-Player
PYSIDE_WHEEL="$(find /tmp/pyside-setup/dist_android -maxdepth 1 -iname 'pyside6-*.whl' -print -quit)"
SHIBOKEN_WHEEL="$(find /tmp/pyside-setup/dist_android -maxdepth 1 -iname 'shiboken6-*.whl' -print -quit)"
pyside6-android-deploy --force --name 'NOVA Player' \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --ndk-path="$ANDROID_HOME/ndk/28.2.13676358" \
  --sdk-path="$ANDROID_HOME"
```

The debug deployment mode produces an APK. Qt's Android deployment tool runs on Linux or macOS, not Windows. The GitHub Actions workflow uses the same Linux build process and uploads the resulting APK.

## Validation status

A successful CI build confirms packaging only. It does not confirm installation, file-picker behavior, audio/video playback, subtitle rendering, or hardware decoding on a physical Android device. Those require device testing. See [Qt for Python's Android deployment guide](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-android-deploy.html).

