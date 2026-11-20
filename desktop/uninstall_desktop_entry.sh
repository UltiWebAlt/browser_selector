#!/usr/bin/env bash
set -euo pipefail

DESKTOP_OUT="$HOME/.local/share/applications/browser-selector.desktop"
ICON_OUT="$HOME/.local/share/icons/hicolor/256x256/apps/browser-selector-icon-alt.png"

# Remove only the files installed by install_desktop_entry.sh.
if [[ -f "$DESKTOP_OUT" ]]; then
  rm -- "$DESKTOP_OUT"
fi
if [[ -f "$ICON_OUT" ]]; then
  rm -- "$ICON_OUT"
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
fi

# Clear the scheme defaults only when they point to our desktop entry.
if command -v xdg-mime >/dev/null 2>&1; then
  for scheme in http https; do
    handler="$(xdg-mime query default "x-scheme-handler/$scheme" 2>/dev/null || true)"
    if [[ "$handler" == "browser-selector.desktop" ]]; then
      xdg-mime default "" "x-scheme-handler/$scheme" 2>/dev/null || true
    fi
  done
fi

printf 'Removed Browser Selector desktop entry and icon.\n'
printf 'Any HTTP/HTTPS defaults pointing to this entry were cleared.\n'
