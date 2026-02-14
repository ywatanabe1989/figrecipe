#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-15 00:30:00 (ywatanabe)"
# File: ./scripts/maintenance/test-dispatch.sh
#
# Dispatch pytest to HPC (default) or run locally.
# Usage: git commit ...                (HPC default)
#        PYTEST_LOCAL=1 git commit ...  (force local)

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ "$PYTEST_LOCAL" = "1" ]; then
    # Explicit local override
    exec python -m pytest tests/ -n auto --dist loadfile -x -q --tb=short
fi

# Try HPC first, fall back to local on failure
"${GIT_ROOT}/scripts/maintenance/test-hpc.sh"
EXIT=$?
if [ "$EXIT" -eq 255 ] || [ "$EXIT" -eq 127 ]; then
    # SSH/srun connectivity failure — fall back to local
    echo "HPC unavailable, running tests locally..."
    exec python -m pytest tests/ -n auto --dist loadfile -x -q --tb=short
fi
exit $EXIT

# EOF
