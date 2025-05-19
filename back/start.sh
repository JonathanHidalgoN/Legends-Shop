#!/bin/bash

set -e

echo "Running database migrations..."
alembic upgrade head

echo "Migrations complete. Starting application server..."
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} "$@"
