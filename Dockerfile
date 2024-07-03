FROM python:3.10-buster

RUN pip install poetry==1.8.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY pyrorisks ./pyrorisks
COPY app ./app
COPY pyproject.toml poetry.lock README.md ./

RUN poetry install
