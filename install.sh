#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$PROJECT_ROOT/.venv"
LAUNCHER_PATH="$VENV_PATH/bin/browser-selector"
DESKTOP_INSTALLER="$PROJECT_ROOT/desktop/install_desktop_entry.sh"

python3 -m venv "$VENV_PATH"
"$VENV_PATH/bin/pip" install PyQt5 pyxdg
ln -sf "$PROJECT_ROOT/browser_selector.py" "$LAUNCHER_PATH"

if [[ "${SKIP_DESKTOP_SETUP:-0}" != "1" && -x "$DESKTOP_INSTALLER" ]]; then
  "$DESKTOP_INSTALLER"
fi

cat <<'EOF'
Installation complete.

Run with:
  ./.venv/bin/browser-selector

Skip desktop integration with:
  SKIP_DESKTOP_SETUP=1 ./install.sh
EOF
