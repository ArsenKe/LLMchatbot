FROM python:3.11-slim
ENV PYTHONPATH=/app

# Install system dependencies and clean up in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
#ENV PYTHONPATH=/app/src
ENV PORT=7860

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]