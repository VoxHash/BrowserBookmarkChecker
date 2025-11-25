#!/bin/bash
# Build script for Nuitka (cross-platform)

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

echo "Building for platform: $PLATFORM"

# Icon handling
ICON_ARG=""
if [ "$PLATFORM" = "windows" ]; then
    if [ -f "assets/icon.ico" ]; then
        ICON_ARG="--windows-icon-from-ico=assets/icon.ico"
    fi
elif [ "$PLATFORM" = "macos" ]; then
    if [ -f "assets/icon.icns" ]; then
        ICON_ARG="--macos-app-icon=assets/icon.icns"
    fi
fi

# Build command
python -m nuitka \
    --standalone \
    --onefile \
    --enable-plugin=pyqt6 \
    --include-data-dir=assets=assets \
    --include-data-dir=bookmark_checker/i18n=bookmark_checker/i18n \
    --output-dir=dist \
    --output-filename=BrowserBookmarkChecker \
    $ICON_ARG \
    bookmark_checker/__main__.py

echo "Build complete! Output in dist/"

