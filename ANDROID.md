# NOVA Player on Android

The Android build targets 64-bit ARM (`arm64-v8a`) phones and tablets. It uses NOVA's Qt Multimedia playback adapter and Android media components, so format and codec support depends on the Android version and device.

The Android layout uses a portrait-friendly player screen, a native media picker, and touch-sized playback controls. Desktop floating picture-in-picture is not offered on Android. When a file is selected through Android's document picker, NOVA passes the returned `content://` URI to the Android media backend.

## Install the APK

Download `NOVA-Player-Android-arm64.apk` from the GitHub Actions artifact or a GitHub Release, copy it to the Android device, and open it. Android may ask you to allow installation from the app used to open the downloaded APK. This is a debug/sideload package and is not signed for Google Play distribution.

## Build locally

Build on Linux or macOS with Python 3.10–3.14, JDK 21, Android SDK platform-tools, Android platform 35, build-tools 35.0.0, and NDK 28.2.13676358. It uses the official public Qt 6.12.0 Android wheels and verifies their published SHA-256 hashes before packaging.

```sh
python3 -m venv .venv-android
. .venv-android/bin/activate
python -m pip install -r requirements.txt jinja2 pkginfo tqdm 'packaging==24.1'

WHEEL_DIR=/tmp/nova-android-wheels
mkdir -p "$WHEEL_DIR"
curl -fL --retry 3 \
  https://download.qt.io/official_releases/QtForPython/pyside6/pyside6-6.12.0-6.12.0-cp310-abi3-android_aarch64.whl \
  -o "$WHEEL_DIR/pyside6-android-aarch64.whl"
curl -fL --retry 3 \
  https://download.qt.io/official_releases/QtForPython/shiboken6/shiboken6-6.12.0-6.12.0-cp310-abi3-android_aarch64.whl \
  -o "$WHEEL_DIR/shiboken6-android-aarch64.whl"
printf '%s  %s\n%s  %s\n' \
  '2cb8352ae6cd091c9f5e11d7bc4ba3bf54088548f63cd804adfdffe5c97c5eb2' "$WHEEL_DIR/pyside6-android-aarch64.whl" \
  'dc5dc4ca86c88327575a9d338c678a8f81f859a25a4dc0e6a539e465ab881660' "$WHEEL_DIR/shiboken6-android-aarch64.whl" \
  | sha256sum --check

SDKMANAGER="$(find "$ANDROID_HOME/cmdline-tools" -type f -name sdkmanager -print -quit)"
mkdir -p "$ANDROID_HOME/tools/bin"
ln -sf "$SDKMANAGER" "$ANDROID_HOME/tools/bin/sdkmanager"

pyside6-android-deploy --force --name 'NOVA Player' \
  --wheel-pyside="$WHEEL_DIR/pyside6-android-aarch64.whl" \
  --wheel-shiboken="$WHEEL_DIR/shiboken6-android-aarch64.whl" \
  --ndk-path="$ANDROID_HOME/ndk/28.2.13676358" \
  --sdk-path="$ANDROID_HOME"
```

The debug deployment mode produces an APK. Qt's Android deployment tool runs on Linux or macOS, not Windows. The GitHub Actions workflow uses the same Linux build process and uploads the resulting APK.

## Validation status

A successful CI build confirms packaging only. It does not confirm installation, file-picker behavior, audio/video playback, subtitle rendering, or hardware decoding on a physical Android device. Those require device testing. See [Qt for Python's Android deployment guide](https://doc.qt.io/qtforpython-6/deployment/deployment-pyside6-android-deploy.html).

