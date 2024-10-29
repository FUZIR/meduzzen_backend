FROM python:3.11-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.meduzzen_backend.settings

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN apk update && apk add --no-cache postgresql-dev gcc python3-dev musl-dev

RUN pip install poetry

RUN poetry install --no-root --no-dev

COPY . /app/
EXPOSE 8000

RUN chmod +x script.sh

ENTRYPOINT ["sh", "script.sh"]
