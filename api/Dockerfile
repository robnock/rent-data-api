# Build context: repo root OR `api/` only — Railway should use Root Directory = `api`.
FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD sh -c 'exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}'
