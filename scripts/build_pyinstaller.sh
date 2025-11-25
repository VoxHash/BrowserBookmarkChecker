#!/bin/bash
# Build script for PyInstaller (fallback)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

# Detect OS
OS="$(uname -s)"
case "$OS" in
    Linux*)     PLATFORM="linux" ;;
    Darwin*)    PLATFORM="macos" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows" ;;
    *)          echo "Unknown OS: $OS"; exit 1 ;;
esac

echo "Building for platform: $PLATFORM with PyInstaller"

# Icon handling
ICON_ARG=""
if [ "$PLATFORM" = "windows" ]; then
    if [ -f "assets/icon.ico" ]; then
        ICON_ARG="--icon=assets/icon.ico"
    fi
elif [ "$PLATFORM" = "macos" ]; then
    if [ -f "assets/icon.icns" ]; then
        ICON_ARG="--icon=assets/icon.icns"
    fi
fi

# Build command
pyinstaller \
    --onefile \
    --windowed \
    --name=BrowserBookmarkChecker \
    --add-data "assets:assets" \
    --add-data "bookmark_checker/i18n:bookmark_checker/i18n" \
    --hidden-import=PyQt6 \
    --hidden-import=rapidfuzz \
    --hidden-import=bs4 \
    $ICON_ARG \
    bookmark_checker/__main__.py

echo "Build complete! Output in dist/"

