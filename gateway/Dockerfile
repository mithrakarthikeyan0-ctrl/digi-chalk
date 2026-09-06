# Dockerfile for Digi-Chalk Gateway Service
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

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
EXPOSE 8001

# Start Uvicorn ASGI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
