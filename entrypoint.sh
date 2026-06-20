#!/bin/sh
set -e

echo "Waiting for database to be ready..."
# The healthcheck in docker-compose handles this usually, but we can do a quick check
sleep 2

echo "Running Alembic migrations..."
alembic upgrade head

echo "Seeding initial data..."
python -m app.seed

echo "Starting application..."
exec "$@"
