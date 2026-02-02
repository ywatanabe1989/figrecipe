#!/bin/bash
# -*- coding: utf-8 -*-
# File: ./examples/00_run_all.sh
# Run all figrecipe examples in sequence.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "FigRecipe Examples Runner"
echo "========================================"

# Skip patterns (interactive/special)
SKIP_PATTERNS="editor|gui|mcp"

# Find all numbered .py files
SCRIPTS=$(find . -maxdepth 1 -name '[0-9][0-9]_*.py' | sort)
TOTAL=$(echo "$SCRIPTS" | wc -l)
COUNT=0

for script in $SCRIPTS; do
    name=$(basename "$script")

    # Skip interactive examples
    if echo "$name" | grep -qiE "$SKIP_PATTERNS"; then
        echo "[SKIP] $name (interactive)"
        continue
    fi

    COUNT=$((COUNT + 1))
    echo ""
    echo "[$COUNT/$TOTAL] Running $name..."
    python "$name" || echo "[WARN] $name exited with error"
    echo "Done: $name"
done

echo ""
echo "========================================"
echo "Completed $COUNT examples"
echo "========================================"
echo "Output directories created: *_out/"
ls -d ./*_out 2>/dev/null || echo "(none)"
