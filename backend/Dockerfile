FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl \
  && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/dev.txt requirements/
RUN pip install -r requirements/dev.txt

COPY . .

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
# Use `sh` explicitly so a volume-mounted entrypoint.sh without the
# executable bit (common on Windows / WSL hosts) still runs.
ENTRYPOINT ["sh", "/app/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
