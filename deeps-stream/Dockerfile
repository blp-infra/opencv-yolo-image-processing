# ============================================================
#   DEEPSTREAM PEOPLE DETECT TEST
#   Base: nvcr.io/nvidia/deepstream:6.3-gc-triton-devel
# ============================================================
FROM nvcr.io/nvidia/deepstream:6.3-gc-triton-devel

LABEL maintainer="deepstream-people-detect-test"
LABEL description="DeepStream People Detection with YOLOv8 + RabbitMQ"

# ── System deps ──────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    python3-gi \
    python3-gi-cairo \
    gir1.2-glib-2.0 \
    libglib2.0-dev \
    libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly \
    libcairo2-dev \
    pkg-config \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# ── Python packages ──────────────────────────────────────────
RUN pip3 install --upgrade pip

RUN pip3 install \
    ultralytics==8.2.0 \
    opencv-python-headless==4.9.0.80 \
    numpy==1.24.4 \
    pika==1.3.2 \
    PyGObject \
    torch \
    torchvision \
    --extra-index-url https://download.pytorch.org/whl/cu118

# ── DeepStream Python bindings ───────────────────────────────
# pyds is pre-installed in the DeepStream image at this path:
ENV PYTHONPATH="/opt/nvidia/deepstream/deepstream/lib:${PYTHONPATH}"

# ── App directory ─────────────────────────────────────────────
WORKDIR /app

# ── Copy video file(s) ────────────────────────────────────────
# Place your queue video file(s) next to this Dockerfile
COPY video/ /app/video/

# ── Copy application code ────────────────────────────────────
COPY detect_people.py       /app/detect_people.py
COPY download_model.py      /app/download_model.py
COPY entrypoint.sh          /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

# ── Pre-download YOLOv8n weights at build time ───────────────
RUN python3 /app/download_model.py

# ── Environment – override at `docker run` time ──────────────
ENV VIDEO_PATH="/app/video/queue.mp4"
ENV RABBITMQ_URL="amqp://guest:guest@rabbitmq:5672/"
ENV RABBITMQ_QUEUE="people_count"
ENV SEND_INTERVAL_SEC="5"
ENV CONFIDENCE_THRESHOLD="0.45"

ENTRYPOINT ["/app/entrypoint.sh"]
