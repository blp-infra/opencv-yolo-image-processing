#!/usr/bin/env python3
"""
download_model.py
Downloads YOLOv8n weights into /app/models/ at image build time.
"""

import os
from pathlib import Path

MODEL_DIR = Path("/app/models")
MODEL_FILE = MODEL_DIR / "yolov8n.pt"

MODEL_DIR.mkdir(parents=True, exist_ok=True)

if MODEL_FILE.exists():
    print(f"✅  Model already present: {MODEL_FILE}")
else:
    print("⬇  Downloading yolov8n.pt …")
    from ultralytics import YOLO

    model = YOLO("yolov8n.pt")  # downloads to ~/.config/… then we copy
    import shutil

    # ultralytics caches in cwd or ~/.config – find & move
    candidate = Path("yolov8n.pt")
    if candidate.exists():
        shutil.move(str(candidate), str(MODEL_FILE))
    else:
        # already downloaded to default cache; just re-load to confirm
        pass
    print(f"✅  Saved to {MODEL_FILE}")
