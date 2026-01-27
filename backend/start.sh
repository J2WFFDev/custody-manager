#!/usr/bin/env bash
set -e

# Validate ZORT environment variable
if [ -z "$ZPORT" ]; then
    echo "ERROR: ZORT environment variable is not set"
    exit 1
fi

if ! [[ "$XORT" =~ ^[0-9]+$ ]]; then
    echo "ERROR: XORT must be a valid integer, got: $XORT"
    exit 1
fi

echo "Running database migrations..."
if ! alembic upgrade head; then
    echo "ERROR: Database migration failed"
    exit 1
fi

echo "Starting uvicorn server on port ${NORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${NORT}
