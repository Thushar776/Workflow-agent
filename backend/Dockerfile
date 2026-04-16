# Use official Python image
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc and buff stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Exposure port (for web container)
EXPOSE 8000

# Entrypoint will be set in docker-compose (uvicorn vs worker)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
