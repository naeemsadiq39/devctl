#!/usr/bin/env bash
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_BIN="/usr/local/bin/devctl"

echo "Installing devctl from $REPO_DIR to $TARGET_BIN"

if [ -e "$TARGET_BIN" ]; then
  echo "Existing devctl found at $TARGET_BIN, overwriting..."
fi

ln -sf "$REPO_DIR/devctl" "$TARGET_BIN"
chmod +x "$REPO_DIR/devctl" "$TARGET_BIN"

echo "Done. Try: devctl --version"
