FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY config ./config
COPY prompts ./prompts
COPY scripts ./scripts
COPY seed ./seed

RUN useradd --create-home appuser \
    && mkdir -p /app/data \
    && chown appuser /app/data
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)"

CMD ["sh", "-c", "python -m scripts.seed_db && exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000"]
