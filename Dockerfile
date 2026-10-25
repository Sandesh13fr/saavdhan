FROM node:22-bookworm-slim AS frontend
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 SAAVDHAN_DATA_DIR=/app/data \
    SAAVDHAN_OCR_ENABLED=true SAAVDHAN_OCR_LANGS=eng+hin+mar
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends tesseract-ocr tesseract-ocr-eng tesseract-ocr-hin tesseract-ocr-mar fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
COPY requirements.lock.txt ./
RUN pip install --no-cache-dir -r requirements.lock.txt && useradd --uid 10001 --create-home saavdhan
COPY backend/ ./backend/
COPY scripts/backup.py ./scripts/backup.py
COPY --from=frontend /build/dist ./frontend/dist/
RUN mkdir /app/data && chown -R saavdhan:saavdhan /app
USER saavdhan
# Hosts like Render set PORT; default 8000 for local Docker/compose.
ENV PORT=8000
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s CMD python -c "import os,urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/api/health',timeout=3)"
# Real client IPs for rate limiting / login throttling come from the reverse proxy.
# Narrow FORWARDED_ALLOW_IPS to the proxy address when the host allows it.
ENV FORWARDED_ALLOW_IPS="*"
CMD ["sh", "-c", "exec uvicorn backend.main:app --host 0.0.0.0 --port \"$PORT\" --workers 1 --no-access-log --proxy-headers"]
