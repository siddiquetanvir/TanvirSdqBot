#!/bin/bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

if [ ! -d "$DIR/venv" ] || [ ! -f "$DIR/venv/bin/pywikibot" ]; then
    echo "Setting up Python virtual environment..."
    python3 -m venv "$DIR/venv"
    "$DIR/venv/bin/pip" install --upgrade pip
    "$DIR/venv/bin/pip" install pywikibot requests
fi

echo "Starting TanvirSdqBot Welcome service..."
exec "$DIR/venv/bin/python3" "$DIR/Welcome/main.py"
