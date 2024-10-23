FROM python:3.11-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=core.meduzzen_backend.settings

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN pip install poetry

RUN poetry install --no-root --no-dev

COPY . /app/
EXPOSE 8000
RUN chmod +x script.sh

CMD ["sh", "script.sh"]
