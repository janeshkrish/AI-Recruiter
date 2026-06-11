# ==============================================================================
# AI Recruiter Brain — Multi-Stage Dockerfile
# ==============================================================================

# --- Base Stage ---
FROM python:3.11-slim as base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (FAISS cpu requires openmp/blas)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    libomp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

# --- API Stage ---
FROM base as api
COPY . .
# Pre-download the default embedding model into Docker image to avoid startup delay
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
CMD ["uvicorn", "recruiter_brain.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# --- UI Stage ---
FROM base as ui
COPY . .
CMD ["streamlit", "run", "recruiter_brain/ui/streamlit_app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
