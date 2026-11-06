FROM python:3.11-slim

WORKDIR /app

# Set environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install CPU-only PyTorch to strictly stay under 2GB limit (avoids bulky CUDA libraries)
RUN pip install --no-cache-dir torch==2.5.1 --index-url https://download.pytorch.org/whl/cpu

# Install pinned service requirements
COPY service/requirements.txt /app/service/requirements.txt
RUN pip install --no-cache-dir -r /app/service/requirements.txt

# Copy service application code (model weights are retrieved at startup from S3)
COPY service/ /app/service/

EXPOSE 8000

# Default environment configuration
ENV MODEL_URI=models/v1 \
    MODEL_VERSION=v1 \
    S3_ENDPOINT=http://seaweedfs-s3.data.svc.cluster.local:8333 \
    MAX_NEW_TOKENS=64 \
    FAULT_INJECT=0

CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000"]
