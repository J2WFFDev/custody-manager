# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (PostgreSQL client for migrations)
RUN apt-get update && \
    apt-get install -y --no-install-recommends postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Railway will set $PORT)
EXPOSE 8000

# Start command - use shell form for variable expansion
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
