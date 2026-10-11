#!/usr/bin/env bash
# Free Art Stack installer — venv + apt, no paid anything.
# System pip is debian-managed, so everything Python lives in .venv/.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"

echo "== python venv =="
if [ ! -x "$HERE/.venv/bin/python" ]; then
  python3 -m venv "$HERE/.venv"
fi
"$HERE/.venv/bin/pip" install --quiet --upgrade pip
"$HERE/.venv/bin/pip" install --quiet \
  rembg opencv-python-headless onnxruntime pillow numpy vtracer
"$HERE/.venv/bin/pip" freeze > "$HERE/venv-requirements.txt"
echo "venv ready: $HERE/.venv (manifest: venv-requirements.txt)"

echo "== system packages (potrace, imagemagick) =="
if command -v sudo >/dev/null && sudo -n true 2>/dev/null; then
  sudo apt-get update -qq || true
  sudo apt-get install -y -qq potrace imagemagick || true
else
  echo "no sudo — install potrace/imagemagick manually if needed"
fi
command -v potrace >/dev/null && echo "potrace OK" || echo "potrace MISSING (vectorize.py needs it)"

echo "== pre-download default rembg model (u2net, ~170MB) =="
"$HERE/.venv/bin/python" -c \
  "from rembg import new_session; new_session('u2net'); print('u2net cached')" \
  2>/dev/null || echo "model download skipped (fetches on first run)"

echo "INSTALL DONE — use ./run.sh <script> <args...> to run with the venv"
