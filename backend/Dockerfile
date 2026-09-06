# Dockerfile for Digi-Chalk Backend
FROM python:3.11-slim

# Prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Create a non-root user
RUN useradd -m -s /bin/bash appuser
RUN chown -R appuser /app
USER appuser

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Start Daphne ASGI server
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]
