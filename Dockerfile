FROM node:20-slim AS frontend-builder
WORKDIR /src/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim AS python-builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
# Install the CPU-only PyTorch wheel first: the default PyPI build bundles
# CUDA/GPU libraries (several nvidia-*-cu12 packages, multiple GB combined)
# that are never used on this CPU-only deployment and blow past Render's
# free-tier image size limit. Once installed, the rest of requirements.txt
# (sentence-transformers only needs torch>=1.11.0) won't override it.
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app

# libgomp1 (OpenMP runtime) is needed by torch/faiss at runtime - it's normally
# pulled in transitively by build-essential, which the final image no longer has.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Only the installed packages and console scripts are copied in - not the
# build-essential toolchain used to compile them, keeping the final image lean.
COPY --from=python-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=python-builder /usr/local/bin /usr/local/bin

COPY backend/app ./app
COPY --from=frontend-builder /src/backend/app/static ./app/static

RUN mkdir -p data/faiss_index data/uploads

ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
