#!/usr/bin/env bash
set -euo pipefail

INSTALL_DIR="${HOME}/.local/opt/nova-player"
APPLICATIONS_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICON_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/256x256/apps"
rm -rf -- "$INSTALL_DIR"
rm -f -- "$APPLICATIONS_DIR/nova-player.desktop" "$ICON_DIR/nova-player.png"
echo "Removed NOVA Player files installed for this user."
