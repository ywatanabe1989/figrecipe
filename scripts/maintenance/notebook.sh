#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-11 11:30:00 (ywatanabe)"
# File: ./scripts/maintenance/notebook.sh

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

echo_header "Executing demo notebook"
cd "$GIT_ROOT"
python3 -m jupyter nbconvert --to notebook --execute --inplace examples/figrecipe_demo.ipynb --ExecutePreprocessor.timeout=120 2>&1 | tee -a "$LOG_PATH"
if [ ${PIPESTATUS[0]} -eq 0 ]; then
    echo_success "Notebook executed successfully"
else
    echo_error "Notebook execution failed"
    exit 1
fi

# EOF
