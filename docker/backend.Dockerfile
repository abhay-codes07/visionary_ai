FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md ./
COPY app ./app
COPY yolov8n.pt ./yolov8n.pt
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir .
RUN pip uninstall -y opencv-python || true \
    && pip install --no-cache-dir --force-reinstall --no-deps opencv-python-headless==4.10.0.84

RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
