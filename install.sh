#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="$HOME/.local/bin/browser-selector"
SCRIPT_PATH="$INSTALL_DIR/browser_selector.py"
VENV_PATH="$INSTALL_DIR/.venv"
LAUNCHER_PATH="$VENV_PATH/bin/browser-selector"
DESKTOP_INSTALLER="$PROJECT_ROOT/desktop/install_desktop_entry.sh"

mkdir -p "$INSTALL_DIR"
install -m 755 "$PROJECT_ROOT/browser_selector.py" "$SCRIPT_PATH"
python3 -m venv "$VENV_PATH"
"$VENV_PATH/bin/python" -m pip install PyQt5 pyxdg
printf '#!/usr/bin/env bash\nexec %q %q "$@"\n' \
  "$VENV_PATH/bin/python" "$SCRIPT_PATH" > "$LAUNCHER_PATH"
chmod +x "$LAUNCHER_PATH"

if [[ "${SKIP_DESKTOP_SETUP:-0}" != "1" && -x "$DESKTOP_INSTALLER" ]]; then
  BROWSER_SELECTOR_LAUNCHER="$LAUNCHER_PATH" "$DESKTOP_INSTALLER"
fi

cat <<EOF
Installation complete.

Run with:
  $LAUNCHER_PATH

Skip desktop integration with:
  SKIP_DESKTOP_SETUP=1 ./install.sh
EOF
