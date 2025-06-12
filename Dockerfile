# Use Python 3.10 slim image as base for Raspberry Pi compatibility
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5009

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY trainova_feedback_network/requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port for Flask API
EXPOSE 5009

# Set Python path to include the project
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Command to run the production server
CMD ["python", "run_production.py"]