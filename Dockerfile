# ==============================================================================
# AI Recruiter Brain — Multi-Stage Dockerfile
# ==============================================================================

# --- Base Stage ---
FROM python:3.11-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Pre-download embedding model (cached in image)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-large-en-v1.5')" || true

# --- API Service ---
FROM base AS api

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

CMD ["uvicorn", "recruiter_brain.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- Streamlit Service ---
FROM base AS streamlit

EXPOSE 8501

CMD ["streamlit", "run", "recruiter_brain/ui/streamlit_app.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true"]

# --- GPU Variant ---
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04 AS gpu-base

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3-pip python3.11-venv curl build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

EXPOSE 8000

CMD ["uvicorn", "recruiter_brain.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
