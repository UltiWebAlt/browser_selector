#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

DESKTOP_SRC="$SCRIPT_DIR/browser-selector.desktop"
DESKTOP_OUT="$HOME/.local/share/applications/browser-selector.desktop"
ICON_SRC="$PROJECT_ROOT/assets/png/alt/browser-selector-icon-alt-256.png"
ICON_OUT="$HOME/.local/share/icons/hicolor/256x256/apps/browser-selector-icon-alt.png"

mkdir -p "$(dirname "$DESKTOP_OUT")"
mkdir -p "$(dirname "$ICON_OUT")"

cp "$ICON_SRC" "$ICON_OUT"
cp "$DESKTOP_SRC" "$DESKTOP_OUT"

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi

if command -v xdg-mime >/dev/null 2>&1; then
  xdg-mime default browser-selector.desktop x-scheme-handler/http
  xdg-mime default browser-selector.desktop x-scheme-handler/https
fi

cat <<'EOF'
Installed desktop launcher:
  ~/.local/share/applications/browser-selector.desktop

Installed icon:
  ~/.local/share/icons/hicolor/256x256/apps/browser-selector-icon-alt.png

If `browser-selector` is not in your PATH, either:
1) Install with pipx (`pipx install .`), or
2) Edit Exec= in the desktop file to an absolute path (for example, /path/to/repo/.venv/bin/browser-selector %U).
EOF
