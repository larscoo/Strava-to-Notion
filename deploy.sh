#!/usr/bin/env bash

set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="$PROJECT_DIR/.venv/bin/python"

cd "$PROJECT_DIR"

if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Python virtualenv fehlt: $VENV_PYTHON"
  exit 1
fi

if [[ ! -f ".env" ]]; then
  echo ".env fehlt in $PROJECT_DIR"
  exit 1
fi

if [[ ! -f "stravaToken.json" ]]; then
  echo "stravaToken.json fehlt in $PROJECT_DIR"
  exit 1
fi

git pull --ff-only
"$VENV_PYTHON" -m pip install -r requirements.txt
"$VENV_PYTHON" -m py_compile uploadToNotion.py monthlyReport.py config.py stravaTokenHandler.py

echo "Deploy erfolgreich."
