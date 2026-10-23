# Use official lightweight and secure Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and buffer stdout/stderr for real-time logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Copy dependency manifest first to leverage Docker layer caching
COPY requirements.txt /app/

# Install dependencies without caching wheels to minimize image layer size
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code and locations.csv dataset into container
COPY . /app/

# Expose FastAPI / Uvicorn server port (internal container port)
EXPOSE 4000

# Health check using standard Python urllib (no external curl dependency needed)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:4000/health')" || exit 1

# Start the application with Uvicorn on port 4000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "4000"]
