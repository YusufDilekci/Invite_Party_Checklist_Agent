FROM python:3.12-slim

# Set workdir
WORKDIR /app

# Install minimal system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency file first
COPY pyproject.toml ./

# Install deps with uv
RUN uv pip install --system --no-cache .

# Copy app code (excluding via .dockerignore)
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run app
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
