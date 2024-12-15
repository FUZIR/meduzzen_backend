#!/bin/sh

if poetry run python -m core.manage makemigrations; then
    echo "Migrations made"
else
    echo "Failed to make migrations"
    exit 1
fi

if poetry run python -m core.manage migrate; then
    echo "Migrations added"
else
    echo "Failed to add migrations"
    exit 1
fi

if poetry run celery -A core.meduzzen_backend worker --loglevel=info & then
    echo "Celery Worker started successfully"
else
    echo "Error while starting Celery Worker"
    exit 1
fi

if poetry run celery -A core.meduzzen_backend beat --loglevel=info & then
    echo "Celery Beat started successfully"
else
    echo "Error while starting Celery Beat"
    exit 1
fi
poetry run daphne -b 0.0.0.0 -p 8000 core.meduzzen_backend.asgi:application
