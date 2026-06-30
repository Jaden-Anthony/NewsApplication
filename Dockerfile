# Use the official Python slim image
FROM python:3.13-slim

# Prevent .pyc files and buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default to SQLite so the image works without an external DB
ENV DB_ENGINE=sqlite3
ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=localhost 127.0.0.1 0.0.0.0 [::1]

WORKDIR /app

# Install system dependencies required by mysqlclient (kept so MySQL works too)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies (includes gunicorn from requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source
COPY . .

# Make entrypoint executable
RUN chmod +x entrypoint.sh

EXPOSE 8000

# Lightweight healthcheck — verifies the app responds on port 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/').read()" || exit 1

ENTRYPOINT ["./entrypoint.sh"]
