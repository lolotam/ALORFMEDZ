FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .
RUN chown -R appuser:appuser /app/data/*.json 2>/dev/null || true

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/backups && \
    chown -R appuser:appuser /app/data /app/logs /app/backups

USER appuser

# Expose port 5001 to avoid conflicts
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5001/ || exit 1

# Set environment variable for Flask port
ENV FLASK_RUN_PORT=5001

# Run application on port 5001
CMD ["python", "-c", "from app import create_app; app = create_app(); app.run(debug=False, host='0.0.0.0', port=5001)"]
