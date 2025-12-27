#!/bin/bash
# Periodic GUI editor restart script
# Usage: ./scripts/gui_periodic.sh [interval_seconds] [port]
# Default: 60 seconds, port 5050

INTERVAL=${1:-60}
PORT=${2:-5050}
SCRIPT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
    echo -e "\nStopping server..."
    fuser -k "$PORT"/tcp 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting GUI editor on port ${PORT} with ${INTERVAL}s restart interval"
echo "Press Ctrl+C to stop"
echo ""

while true; do
    # Kill existing process
    fuser -k "$PORT"/tcp 2>/dev/null
    sleep 1

    # Start server in background
    cd "$SCRIPT_DIR" || exit 1
    python examples/demo_editor.py "$PORT" &
    SERVER_PID=$!

    echo "[$(date '+%H:%M:%S')] Server started (PID: $SERVER_PID)"

    # Wait for interval
    sleep "$INTERVAL"

    # Kill the server before restart
    kill $SERVER_PID 2>/dev/null
    wait $SERVER_PID 2>/dev/null

    echo "[$(date '+%H:%M:%S')] Restarting..."
done
