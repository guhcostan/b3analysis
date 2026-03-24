#!/usr/bin/env bash
set -e
WORKSPACE="$(cd "$(dirname "$0")" && pwd)"
VENV="$WORKSPACE/.venv"

if [ ! -x "$VENV/bin/python" ]; then
    echo "[B3Analysis] First run: setting up Python environment..." >&2
    python3 -m venv "$VENV"
    "$VENV/bin/pip" install -q -r "$WORKSPACE/requirements.txt"
    echo "[B3Analysis] Done." >&2
fi

exec "$VENV/bin/python" "$@"
