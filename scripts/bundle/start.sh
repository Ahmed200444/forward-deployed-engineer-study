#!/bin/sh
# Mac and Linux: serves this folder at http://localhost:8765/ and opens it. Needs python3 (built into macOS
# once the Command Line Tools are installed, and into most Linux systems). Press Ctrl+C to stop.
cd "$(dirname "$0")" || exit 1
URL="http://localhost:8765/"
if command -v open >/dev/null 2>&1; then (sleep 1; open "$URL") &
elif command -v xdg-open >/dev/null 2>&1; then (sleep 1; xdg-open "$URL") & fi
echo "FDE Study is running at $URL  (Ctrl+C to stop)"
exec python3 -m http.server 8765 --bind 127.0.0.1
