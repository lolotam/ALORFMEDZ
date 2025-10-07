FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user FIRST
RUN adduser --disabled-password --gecos '' appuser

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories and fix ownership
RUN mkdir -p /app/data /app/logs /app/backups && \
    chown -R appuser:appuser /app

USER appuser

# Expose port 5045
EXPOSE 5045

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5045/ || exit 1

# Set environment variable for Flask port
ENV FLASK_RUN_PORT=5045

# Run application on port 5045
CMD ["python", "-c", "from app import create_app; app = create_app(); app.run(debug=False, host='0.0.0.0', port=5045)"]