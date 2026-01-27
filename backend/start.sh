#!/usr/bin/env bash
set -e

# Validate PORT environment variable
if [ -z "$PORT" ]; then
    echo "ERROR: PORT environment variable is not set"
    exit 1
fi

if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "ERROR: PORT must be a valid integer, got: $PORT"
    exit 1
fi

echo "Running database migrations..."
if ! alembic upgrade head; then
    echo "ERROR: Database migration failed"
    exit 1
fi

echo "Starting uvicorn server on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
