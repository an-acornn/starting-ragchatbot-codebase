#!/bin/bash
# Format all Python files with black

set -e
cd "$(dirname "$0")/.."

echo "Running black formatter..."
uv run black backend/ main.py "$@"
echo "Formatting complete."
