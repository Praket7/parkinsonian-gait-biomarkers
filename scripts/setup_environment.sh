#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3.11 >/dev/null 2>&1; then
  printf '%s\n' "Python 3.11 is required. Install it, then run this script again."
  exit 1
fi

python3.11 -c 'import venv; venv.create(".venv", with_pip=True)'
source .venv/bin/activate
python -m pip install --requirement requirements-lock.txt pytest
python -m pip install --editable . --no-deps
