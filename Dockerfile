# Web Testing Agent Dockerfile
FROM python:3.11-slim

# work dir
WORKDIR /app

# install dep
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy requirements.txt
COPY requirements.txt .

# install python dep
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# non-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# port
EXPOSE 7861

# health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7861/ || exit 1

# command
CMD ["python", "main.py"]