#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-11 11:30:00 (ywatanabe)"
# File: ./scripts/maintenance/demo-gui-browser.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

PORT=${1:-5050}

echo_header "Starting editor and opening in browser on port $PORT"
cd "$GIT_ROOT"
python3 examples/demo_editor.py "$PORT" &
sleep 3

# Try various methods to open browser
cmd.exe /c start chrome "http://127.0.0.1:${PORT}" 2>/dev/null || \
"/mnt/c/Program Files/Google/Chrome/Application/chrome.exe" "http://127.0.0.1:${PORT}" 2>/dev/null || \
wslview "http://127.0.0.1:${PORT}" 2>/dev/null || \
echo_warning "Could not open browser. Please open http://127.0.0.1:${PORT} manually"

wait

# EOF
