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

poetry run python -m core.manage runserver 0.0.0.0:8000

