#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-02-08 09:30:00 (ywatanabe)"
# File: ./scripts/maintenance/test-dispatch.sh
#
# Dispatch pytest to HPC or run locally based on PYTEST_HPC env var.
# Usage: PYTEST_HPC=1 git commit ...  (remote)
#        git commit ...                (local, default)

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

if [ "$PYTEST_HPC" = "1" ]; then
    exec "${GIT_ROOT}/scripts/maintenance/test-hpc.sh"
else
    exec python -m pytest tests/ -n auto --dist loadfile -x -q --tb=short
fi

# EOF
