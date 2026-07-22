FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml ./

RUN poetry install --no-root --only dev --no-interaction

COPY . ./

CMD ["poetry", "run", "python", "-c", "print('Enterprise Agent Lab backend scaffold ready')"]
