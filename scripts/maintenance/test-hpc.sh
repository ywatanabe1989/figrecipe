#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-08 09:30:00 (ywatanabe)"
# File: ./scripts/maintenance/test-hpc.sh

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
echo >"$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
PROJECT="$(basename "$GIT_ROOT")"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }

# Configurable
HPC_HOST="${HPC_HOST:-spartan}"
HPC_CPUS="${HPC_CPUS:-8}"
HPC_PARTITION="${HPC_PARTITION:-sapphire}"
HPC_TIME="${HPC_TIME:-00:10:00}"
HPC_MEM="${HPC_MEM:-8G}"
REMOTE_BASE="${REMOTE_BASE:-~/proj}"

# -----------------------------------------------
echo_header "Syncing to ${HPC_HOST}:${REMOTE_BASE}/${PROJECT}/"

rsync -az --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.eggs' \
    --exclude='*.egg-info' \
    --exclude='dist' \
    --exclude='build' \
    --exclude='docs/sphinx/_build' \
    --exclude='.tox' \
    --exclude='.mypy_cache' \
    --exclude='.pytest_cache' \
    --exclude='*_out' \
    --exclude='GITIGNORED' \
    "$GIT_ROOT/" "${HPC_HOST}:${REMOTE_BASE}/${PROJECT}/" 2>&1 | tee -a "$LOG_PATH"

if [ "${PIPESTATUS[0]}" -ne 0 ]; then
    echo_error "rsync failed"
    exit 1
fi
echo_success "Sync complete"

# -----------------------------------------------
echo_header "Running pytest on ${HPC_HOST} (srun: ${HPC_CPUS} CPUs, ${HPC_PARTITION})"

# shellcheck disable=SC2029  # Intentional client-side expansion
ssh "${HPC_HOST}" "srun \
    --partition=${HPC_PARTITION} \
    --cpus-per-task=${HPC_CPUS} \
    --time=${HPC_TIME} \
    --mem=${HPC_MEM} \
    --job-name=pytest-${PROJECT} \
    bash -lc 'cd ${REMOTE_BASE}/${PROJECT} && pip install -e . -q 2>/dev/null && python -m pytest tests/ -n ${HPC_CPUS} --dist loadfile -x -q --tb=short'" 2>&1 | tee -a "$LOG_PATH"

EXIT_CODE=${PIPESTATUS[0]}

if [ "$EXIT_CODE" -eq 0 ]; then
    echo_success "All tests passed on ${HPC_HOST}"
else
    echo_error "Tests failed on ${HPC_HOST} (exit code: ${EXIT_CODE})"
fi

exit "$EXIT_CODE"

# EOF
