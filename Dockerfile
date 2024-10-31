FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.meduzzen_backend.settings

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN apt-get update && apt-get install -y libpq-dev gcc python3-dev && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

RUN poetry install --no-root --no-dev

COPY . /app/
EXPOSE 8000

RUN chmod +x script.sh

ENTRYPOINT ["sh", "script.sh"]
