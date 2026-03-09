#!/bin/bash
# Run all code quality checks

set -e
cd "$(dirname "$0")/.."

echo "=== Code Quality Checks ==="
echo ""

echo "1. Checking formatting (black)..."
if uv run black --check backend/ main.py 2>&1; then
    echo "   All files formatted correctly."
else
    echo ""
    echo "   Some files need formatting. Run: ./scripts/format.sh"
    exit 1
fi

echo ""
echo "=== All checks passed ==="
