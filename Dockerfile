FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl && \
    pip install --upgrade pip && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get remove -y curl && apt-get clean

ENV POETRY_VIRTUALENVS_CREATE=false \
    PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev

RUN mkdir -p /app/logs
COPY alembic /app/alembic
COPY alembic.ini /app/
COPY config /app/config
COPY simpleone /app/simpleone
COPY src /app/src
COPY fetch_simpleone.py sla_checker.py /app/

CMD ["sh", "-c", "alembic upgrade head && poetry run python fetch_simpleone.py --groups 'config/our_groups.json' --req_params 'config/req_params.json' & poetry run python sla_checker.py & wait"]
