#!/bin/bash
set -e

echo "Waiting for database..."
sleep 2

echo "Running database migrations..."
flask db upgrade

echo "Starting server..."
exec "$@"

