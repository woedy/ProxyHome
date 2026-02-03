FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy proxy fetcher scripts
COPY premium_proxy_fetcher.py .
COPY public_proxy_fetcher.py .
COPY basic_proxy_fetcher.py .

# Create directories
RUN mkdir -p /app/proxy_data /app/logs /app/static /app/media

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Default command
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120", "proxyplatform.wsgi:application"]