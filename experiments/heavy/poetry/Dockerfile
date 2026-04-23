FROM python:3.11-slim

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/tmp/poetry_cache

RUN pip install --no-cache-dir "poetry==2.3.2"

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --only main && rm -rf $POETRY_CACHE_DIR
