# Deal Mind Backend - Production Docker image

FROM python:3.12-slim

ENV PYTHONDONTWRITECODE=1 \
    PYTHONUNBFFRED=1 \
    PIP_NO_CACHE_DIR=1


RUN useradd \
    --create-home \
    --shell /usr/sbin/nologin \
    appuser

WORKDIR /app

COPY requirements.txt .

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK \
    --interval= \
    --timeout= \
    --start-interval=30s \
    --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health').read()"


CMD ["uvicorn", "main:app", "--host" , "0.0.0.0", "--port", "8000"]

