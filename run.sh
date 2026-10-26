#!/usr/bin/env bash
set -e
WORKSPACE="$(cd "$(dirname "$0")" && pwd)"
VENV="$WORKSPACE/.venv"
LOCK="$WORKSPACE/.venv.lock"

# pandas 3.0.x segfaults on Python 3.15 — prefer a known-good interpreter.
_pick_python() {
    for py in python3.13 python3.12 python3.11; do
        if command -v "$py" >/dev/null 2>&1; then
            echo "$py"
            return
        fi
    done
    if command -v uv >/dev/null 2>&1; then
        echo "uv"
        return
    fi
    echo "python3"
}

if [ ! -x "$VENV/bin/python" ]; then
    # Serialize bootstrap so parallel invocations don't race on venv creation.
    until mkdir "$LOCK" 2>/dev/null; do sleep 1; done
    trap 'rmdir "$LOCK" 2>/dev/null || true' EXIT
    if [ ! -x "$VENV/bin/python" ]; then
        echo "[B3Analysis] First run: setting up Python environment..." >&2
        PY="$(_pick_python)"
        if [ "$PY" = "uv" ]; then
            uv venv -q --python 3.13 "$VENV"
            uv pip install -q --python "$VENV/bin/python" -r "$WORKSPACE/requirements.txt"
        else
            "$PY" -m venv "$VENV"
            "$VENV/bin/pip" install -q -r "$WORKSPACE/requirements.txt"
        fi
        echo "[B3Analysis] Done." >&2
    fi
    rmdir "$LOCK" 2>/dev/null || true
    trap - EXIT
fi

exec "$VENV/bin/python" "$@"
