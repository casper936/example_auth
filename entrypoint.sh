#!/bin/sh

echo "Apply migrations"

alembic -c src/models/migrations/alembic.ini upgrade head


echo "Start API..."

gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000