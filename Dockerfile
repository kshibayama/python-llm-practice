FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY pyproject.toml uv.lock* /app/
# uvを使う例。poetry/pipでもOK
RUN pip install -U uv && uv sync --frozen || true

COPY . /app
RUN mkdir -p /app/data && chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]

