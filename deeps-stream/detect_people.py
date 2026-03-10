#!/usr/bin/env python3
"""
========================================================
  DEEPSTREAM PEOPLE DETECT TEST
  detect_people.py

  • Reads a video in an infinite loop
  • Runs YOLOv8 person detection on every frame
  • Aggregates counts over SEND_INTERVAL_SEC seconds
  • Publishes { timestamp, people_count, interval_sec }
    to a RabbitMQ queue
========================================================
"""

import os
import sys
import json
import time
import logging
import threading
from datetime import datetime, timezone
from collections import deque

import cv2
import numpy as np
import pika
from ultralytics import YOLO

# ── Logging ──────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("people-detect")

# ── Config from environment ───────────────────────────────────
VIDEO_PATH = os.environ.get("VIDEO_PATH", "/app/video/queue.mp4")
RABBITMQ_URL = os.environ.get("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
RABBITMQ_QUEUE = os.environ.get("RABBITMQ_QUEUE", "people_count")
SEND_INTERVAL_SEC = int(os.environ.get("SEND_INTERVAL_SEC", "5"))
CONF_THRESHOLD = float(os.environ.get("CONFIDENCE_THRESHOLD", "0.45"))
MODEL_PATH = os.environ.get("MODEL_PATH", "/app/models/yolov8n.pt")
PERSON_CLASS_ID = 0  # COCO class 0 = person


# ══════════════════════════════════════════════════════════════
#  RabbitMQ publisher (runs in its own thread)
# ══════════════════════════════════════════════════════════════
class RabbitMQPublisher:
    def __init__(self, url: str, queue: str):
        self.url = url
        self.queue = queue
        self._conn = None
        self._ch = None
        self._lock = threading.Lock()
        self._connect()

    # ── connection / channel ──────────────────────────────────
    def _connect(self):
        retry, max_retry = 0, 10
        while retry < max_retry:
            try:
                params = pika.URLParameters(self.url)
                params.heartbeat = 60
                params.blocked_connection_timeout = 30
                self._conn = pika.BlockingConnection(params)
                self._ch = self._conn.channel()
                self._ch.queue_declare(queue=self.queue, durable=True)
                log.info("✅  RabbitMQ connected  →  queue='%s'", self.queue)
                return
            except Exception as exc:
                retry += 1
                wait = min(2**retry, 30)
                log.warning(
                    "RabbitMQ connect failed (%s/%s): %s — retry in %ss",
                    retry,
                    max_retry,
                    exc,
                    wait,
                )
                time.sleep(wait)
        log.error("❌  Could not connect to RabbitMQ after %s attempts.", max_retry)

    def _ensure_connected(self):
        try:
            if self._conn and self._conn.is_open:
                return True
        except Exception:
            pass
        log.warning("RabbitMQ connection lost — reconnecting …")
        self._connect()
        return self._conn is not None

    # ── public publish ────────────────────────────────────────
    def publish(self, payload: dict):
        with self._lock:
            if not self._ensure_connected():
                log.error("Skipping publish — no RabbitMQ connection.")
                return
            try:
                body = json.dumps(payload)
                self._ch.basic_publish(
                    exchange="",
                    routing_key=self.queue,
                    body=body,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # persistent
                        content_type="application/json",
                    ),
                )
                log.info("📤  Published → %s", body)
            except Exception as exc:
                log.error("Publish error: %s", exc)
                self._conn = None  # force reconnect next time

    def close(self):
        try:
            if self._conn and self._conn.is_open:
                self._conn.close()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════
#  Main detection loop
# ══════════════════════════════════════════════════════════════
def run_detection():
    # ── sanity checks ─────────────────────────────────────────
    if not os.path.exists(VIDEO_PATH):
        log.error("Video not found: %s", VIDEO_PATH)
        sys.exit(1)

    if not os.path.exists(MODEL_PATH):
        log.error("Model not found: %s  — run download_model.py first", MODEL_PATH)
        sys.exit(1)

    log.info("═══════════════════════════════════════════")
    log.info("  DEEPSTREAM PEOPLE DETECT TEST")
    log.info("  Video    : %s", VIDEO_PATH)
    log.info("  RabbitMQ : %s  →  %s", RABBITMQ_URL, RABBITMQ_QUEUE)
    log.info("  Interval : %s s", SEND_INTERVAL_SEC)
    log.info("  Conf thr : %s", CONF_THRESHOLD)
    log.info("═══════════════════════════════════════════")

    # ── load model ────────────────────────────────────────────
    log.info("Loading YOLOv8 model …")
    model = YOLO(MODEL_PATH)
    model.fuse()
    log.info("Model loaded ✅")

    # ── RabbitMQ publisher ────────────────────────────────────
    publisher = RabbitMQPublisher(RABBITMQ_URL, RABBITMQ_QUEUE)

    # ── per-interval bookkeeping ──────────────────────────────
    interval_start = time.time()
    counts_in_window = []  # list of per-frame counts in current interval

    loop_count = 0

    try:
        while True:  # ← infinite video loop
            loop_count += 1
            cap = cv2.VideoCapture(VIDEO_PATH)

            if not cap.isOpened():
                log.error("Cannot open video: %s", VIDEO_PATH)
                time.sleep(2)
                continue

            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            total_frms = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            log.info(
                "▶  Loop #%d  |  %.1f fps  |  %d frames", loop_count, fps, total_frms
            )

            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break  # end of video → restart outer loop

                frame_idx += 1

                # ── YOLOv8 inference ──────────────────────────
                results = model.predict(
                    source=frame,
                    conf=CONF_THRESHOLD,
                    classes=[PERSON_CLASS_ID],
                    verbose=False,
                    device=0 if _cuda_available() else "cpu",
                )

                person_count = 0
                for r in results:
                    person_count += int((r.boxes.cls == PERSON_CLASS_ID).sum())

                counts_in_window.append(person_count)

                # ── interval boundary? → publish ──────────────
                now = time.time()
                if now - interval_start >= SEND_INTERVAL_SEC:
                    avg_count = (
                        round(sum(counts_in_window) / len(counts_in_window))
                        if counts_in_window
                        else 0
                    )
                    max_count = max(counts_in_window) if counts_in_window else 0

                    payload = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "interval_sec": SEND_INTERVAL_SEC,
                        "people_count": avg_count,  # average over interval
                        "people_max": max_count,  # peak in interval
                        "frames_sampled": len(counts_in_window),
                        "video_loop": loop_count,
                        "frame_index": frame_idx,
                    }
                    publisher.publish(payload)

                    # reset window
                    counts_in_window = []
                    interval_start = now

            cap.release()
            log.info("↩  Video ended — restarting loop …")

    except KeyboardInterrupt:
        log.info("Interrupted — shutting down.")
    finally:
        publisher.close()
        log.info("Goodbye.")


# ── helper ────────────────────────────────────────────────────
def _cuda_available() -> bool:
    try:
        import torch

        return torch.cuda.is_available()
    except ImportError:
        return False


if __name__ == "__main__":
    run_detection()
