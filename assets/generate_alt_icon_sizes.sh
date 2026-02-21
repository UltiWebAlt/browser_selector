#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_ICON="$SCRIPT_DIR/browser-selector-icon-alt.svg"
OUT_DIR="$SCRIPT_DIR/png/alt"
SIZES=(16 24 32 48 64 128 256 512)

mkdir -p "$OUT_DIR"

for size in "${SIZES[@]}"; do
  rsvg-convert -w "$size" -h "$size" "$SRC_ICON" -o "$OUT_DIR/browser-selector-icon-alt-${size}.png"
done

echo "Generated ${#SIZES[@]} PNG files in: $OUT_DIR"
