# NOVA Player on Android

The Android build targets 64-bit ARM (`arm64-v8a`) phones and tablets. It uses the NOVA Qt Multimedia playback adapter and Android's media components. Format and codec support therefore depends on the Android version and device.

The Android layout uses a portrait-friendly player screen, a native media picker, and touch-sized playback controls. The desktop floating picture-in-picture window is not offered on Android. When a file is selected through Android's document picker, NOVA passes the returned content URI to the Android media backend.

## Install the APK

Download `NOVA-Player-Android-arm64.apk` from the GitHub Actions artifact or a GitHub Release, copy it to the Android device, and open it. Android may ask you to allow installation from the app you used to open the downloaded APK. This is a debug/sideload package and is not signed for Google Play distribution.

## Build locally

Build on Linux or macOS with Python 3.10–3.14, JDK 17+, Android SDK platform-tools, Android platform 35, build-tools 35.0.0, and NDK 28.2.13676358. Use the same PySide6 version as the desktop project:

```sh
python3 -m venv .venv-android
. .venv-android/bin/activate
python -m pip install -r requirements.txt
mkdir -p /tmp/nova-android-wheels
cd /tmp/nova-android-wheels
qtpip download 'PySide6==6.12.0' --android --arch aarch64
cd /path/to/NOVA-Player
PYSIDE_WHEEL=$(find /tmp/nova-android-wheels -maxdepth 1 -iname 'pyside6-*.whl' -print -quit)
SHIBOKEN_WHEEL=$(find /tmp/nova-android-wheels -maxdepth 1 -iname 'shiboken6-*.whl' -print -quit)
pyside6-android-deploy --force --name 'NOVA Player' \
  --wheel-pyside="$PYSIDE_WHEEL" \
  --wheel-shiboken="$SHIBOKEN_WHEEL" \
  --ndk-path="$ANDROID_HOME/ndk/28.2.13676358" \
  --sdk-path="$ANDROID_HOME"
```

The debug deployment mode produces an APK. Qt's Android deployment tool runs on Linux or macOS, not Windows. The GitHub Actions workflow uses the matching Linux build host and uploads the resulting APK.

## Validation status

The project can build an Android package through Qt for Python's Android deployment tool. A successful CI build only confirms packaging. It does not confirm installation, file-picker behavior, audio/video playback, subtitle rendering, or hardware decoding on a physical Android device. Those require device testing. See [Qt for Python's Android deployment guide](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-android-deploy.html).

