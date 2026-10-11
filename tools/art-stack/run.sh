#!/usr/bin/env bash
# Run an art-stack script with the stack venv: ./run.sh bg_remove.py in.jpg out.png
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
exec "$HERE/.venv/bin/python" "$HERE/$1" "${@:2}"
