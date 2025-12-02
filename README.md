# opencv-yolo-image-processing
This repo contains code to train and monitor opencv yolo image processing container applicaiton


# Using open telemetry to trace data
- Prometheus +Grafana
- ELK
- Jaeger
```
pip install opentelemetry-sdk \
            opentelemetry-exporter-otlp \
            opentelemetry-exporter-otlp-proto-grpc \
            opentelemetry-instrumentation \
            opentelemetry-instrumentation-logging \
            opentelemetry-instrumentation-requests \
            opentelemetry-instrumentation-urllib \
            opentelemetry-instrumentation-system-metrics

or uv add 
```

# pin specific python
```uv init project name
uv python pin 3.12

create specific version venv
uv venv for mormal
uv venv --python 3.12```


# run fastapi 
```
fastapi dev main.py
```