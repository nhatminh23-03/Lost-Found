#!/usr/bin/env bash
set -e

# Load .env if present (dev convenience)
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
fi

# Dev: python run.py  |  Prod: gunicorn
if [ "${FLASK_ENV:-production}" = "development" ]; then
  python run.py
else
  gunicorn "run:app" --bind "0.0.0.0:${PORT:-5000}" --workers 2
fi
