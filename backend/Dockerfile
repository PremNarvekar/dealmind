FROM python:3.12-slim

# ── System deps (required for psycopg binary wheel) ──────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Working directory ─────────────────────────────────────────────────────────
WORKDIR /app

# ── Install Python deps first (layer-cached unless requirements.txt changes) ──
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application source ───────────────────────────────────────────────────
# .dockerignore should exclude: .venv, .env, __pycache__, *.pyc, tests/
COPY . .

# ── Security: never copy .env into the image ──────────────────────────────────
# Secrets must be provided at runtime via environment variables or a secrets
# manager (e.g., AWS Secrets Manager, GCP Secret Manager, K8s Secrets).

# ── Runtime configuration ─────────────────────────────────────────────────────
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
# These are placeholders — override at runtime:
ENV GOOGLE_API_KEY=""
ENV TAVILY_API_KEY=""
ENV DATABASE_URL=""
ENV GEMINI_MODEL="gemini-2.0-flash"

EXPOSE 8000

# ── Health check for container orchestrators ──────────────────────────────────
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# ── Entrypoint ────────────────────────────────────────────────────────────────
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
