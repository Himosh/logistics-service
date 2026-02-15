#!/usr/bin/env bash
set -e

# Apply DB migrations
alembic upgrade head

# Start API
uvicorn app.main:app --host 0.0.0.0 --port 8000
