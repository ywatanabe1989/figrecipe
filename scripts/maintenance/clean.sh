#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-11 11:30:00 (ywatanabe)"
# File: ./scripts/maintenance/clean.sh

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

echo_header "Cleaning build artifacts and outputs"
cd "$GIT_ROOT"

# Clean outputs first
"$THIS_DIR/clean-outputs.sh"

# Clean build artifacts
echo_info "Removing build directories..."
rm -rf build/
rm -rf dist/
rm -rf *.egg-info/
rm -rf src/*.egg-info/
rm -rf .pytest_cache/
rm -rf .coverage
rm -rf htmlcov/

echo_info "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo_success "Build artifacts cleaned"

# EOF
