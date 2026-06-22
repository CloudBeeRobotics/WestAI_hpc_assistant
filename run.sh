#!/usr/bin/env bash
# Launch the rwth2125 HPC Assistant web app locally.
#   ./run.sh            -> http://localhost:8000
# Each user pastes their own Groq API key in the UI; nothing is stored on disk.
set -euo pipefail
cd "$(dirname "$0")/backend"

if [[ ! -d .venv ]]; then
  echo ">> creating virtualenv + installing deps (first run only)…"
  python3 -m venv .venv
  ./.venv/bin/pip install -q --upgrade pip
  ./.venv/bin/pip install -q -r requirements.txt
fi

echo ">> open http://localhost:${PORT:-8000}"
exec ./.venv/bin/python app.py
