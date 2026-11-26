#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_APP="$SCRIPT_DIR/NOVAPlayer"
INSTALL_DIR="${HOME}/.local/opt/nova-player"
APPLICATIONS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"

if [[ ! -x "$SOURCE_APP/NOVAPlayer" ]]; then
  echo "NOVA Player binary is missing from: $SOURCE_APP" >&2
  exit 1
fi

mkdir -p "$INSTALL_DIR" "$APPLICATIONS_DIR" "$ICON_DIR"
cp -a "$SOURCE_APP/." "$INSTALL_DIR/"
if [[ -f "$INSTALL_DIR/assets/store-logo.png" ]]; then
  cp "$INSTALL_DIR/assets/store-logo.png" "$ICON_DIR/nova-player.png"
  ICON_PATH="$ICON_DIR/nova-player.png"
else
  ICON_PATH="$INSTALL_DIR/NOVAPlayer"
fi

desktop_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/ /\\ /g' -e 's/"/\\"/g'
}

ESCAPED_EXE="$(desktop_escape "$INSTALL_DIR/NOVAPlayer")"
ESCAPED_ICON="$(desktop_escape "$ICON_PATH")"
cat > "$APPLICATIONS_DIR/nova-player.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=NOVA Player
Comment=Play music and video with NOVA Player
Exec=$ESCAPED_EXE %F
Icon=$ESCAPED_ICON
Terminal=false
Categories=AudioVideo;Player;Video;Audio;
MimeType=audio/mpeg;audio/flac;audio/ogg;video/mp4;video/x-matroska;video/webm;
EOF
chmod 644 "$APPLICATIONS_DIR/nova-player.desktop"
echo "Installed NOVA Player for this user. Launch it from the application menu or run: \"$INSTALL_DIR/NOVAPlayer\""
