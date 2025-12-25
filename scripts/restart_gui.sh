#!/bin/bash
# Restart GUI editor - kills old process and starts fresh
# Usage: ./scripts/restart_gui.sh

PORT=5050

echo "Stopping existing server on port $PORT..."
fuser -k $PORT/tcp 2>/dev/null || lsof -ti :$PORT | xargs -r kill -9 2>/dev/null
sleep 1

echo "Starting GUI editor..."
cd "$(dirname "$0")/.." || exit 1
python examples/demo_editor.py
