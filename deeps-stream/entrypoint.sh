#!/bin/bash
# ============================================================
#   DEEPSTREAM PEOPLE DETECT TEST  —  entrypoint
# ============================================================
set -e

echo "========================================================"
echo "   DEEPSTREAM PEOPLE DETECT TEST"
echo "   $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo "========================================================"
echo "  VIDEO_PATH        : ${VIDEO_PATH}"
echo "  RABBITMQ_URL      : ${RABBITMQ_URL}"
echo "  RABBITMQ_QUEUE    : ${RABBITMQ_QUEUE}"
echo "  SEND_INTERVAL_SEC : ${SEND_INTERVAL_SEC}"
echo "  CONF_THRESHOLD    : ${CONFIDENCE_THRESHOLD}"
echo "========================================================"

# Ensure model weights exist (no-op if already downloaded at build)
python3 /app/download_model.py

# Start detection
exec python3 /app/detect_people.py
