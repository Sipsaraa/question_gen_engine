FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
# libpq-dev is required for building psycopg2 (even binary sometimes needs libs) 
# but psycopg2-binary usually includes it. 
# We add gcc and libpq-dev just in case we switch to psycopg2 source or have other native deps.
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src ./src
COPY scripts ./scripts
COPY docs ./docs
COPY mkdocs.yml .

# Build documentation
RUN mkdocs build

# Set PYTHONPATH
ENV PYTHONPATH=/app

# Default command (overridden by docker-compose)
CMD ["python", "--version"]
