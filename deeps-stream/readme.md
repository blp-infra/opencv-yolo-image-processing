# DEEPSTREAM PEOPLE DETECT TEST

Detects people in a looping queue video using **YOLOv8** inside an NVIDIA
DeepStream container and publishes per-interval counts to **RabbitMQ**.

---

## Project structure

```
.
├── Dockerfile            ← Extends deepstream:6.3-gc-triton-devel
├── docker-compose.yml    ← Spins up RabbitMQ + detector together
├── detect_people.py      ← Main detection + publishing loop
├── download_model.py     ← Downloads yolov8n.pt at build time
├── entrypoint.sh         ← Container entry point
└── video/
    └── queue.mp4         ← ⚠ Place your queue video here
```

---

## Quick start

### 1 — Place your video

```bash
mkdir -p video
cp /path/to/your/queue_video.mp4 video/queue.mp4
```

### 2 — Build & run (GPU host with Docker Compose)

```bash
docker compose up --build
```

The detector waits for RabbitMQ to be healthy before starting.

### 3 — Watch the queue

Open the RabbitMQ management UI:  
**http://localhost:15672** (user: `guest` / pass: `guest`)  
→ Queues → `people_count`

---

## Run with a custom RabbitMQ URL

```bash
docker compose run --rm \
  -e RABBITMQ_URL="amqp://user:pass@my-broker:5672/" \
  -e SEND_INTERVAL_SEC=10 \
  people-detector
```

---

## Environment variables

| Variable               | Default                                  | Description                                    |
|------------------------|------------------------------------------|------------------------------------------------|
| `VIDEO_PATH`           | `/app/video/queue.mp4`                   | Path to video inside container                 |
| `RABBITMQ_URL`         | `amqp://guest:guest@rabbitmq:5672/`      | Full AMQP URL                                  |
| `RABBITMQ_QUEUE`       | `people_count`                           | Queue name                                     |
| `SEND_INTERVAL_SEC`    | `5`                                      | Seconds between each RabbitMQ publish          |
| `CONFIDENCE_THRESHOLD` | `0.45`                                   | YOLOv8 detection confidence threshold          |
| `MODEL_PATH`           | `/app/models/yolov8n.pt`                 | Path to YOLO weights inside container          |

---

## RabbitMQ message format

Each message published to the queue is a JSON object:

```json
{
  "timestamp":      "2024-06-01T12:00:05.123456+00:00",
  "interval_sec":   5,
  "people_count":   7,
  "people_max":     9,
  "frames_sampled": 124,
  "video_loop":     3,
  "frame_index":    872
}
```

| Field            | Meaning                                             |
|------------------|-----------------------------------------------------|
| `people_count`   | **Average** number of persons detected per frame over the interval |
| `people_max`     | **Peak** count in the interval                      |
| `frames_sampled` | How many frames were processed in the interval      |
| `video_loop`     | Which iteration of the looping video we are on      |

---

## Build image only (no Compose)

```bash
docker build -t deepstream-people-detect-test .

docker run --rm --gpus all \
  -e RABBITMQ_URL="amqp://guest:guest@<your-host>:5672/" \
  -v $(pwd)/video/queue.mp4:/app/video/queue.mp4:ro \
  deepstream-people-detect-test
```

---

## Prerequisites on host

- NVIDIA GPU + driver ≥ 525
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)
- Docker ≥ 20.10 with Compose v2
