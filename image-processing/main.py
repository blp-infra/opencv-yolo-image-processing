import time
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.logs import LoggingHandler

# ---- Resource (Tags) ----
resource = Resource(attributes={
    "service.name": "job-worker",
    "service.instance.id": "worker-1",
})

# ---- Tracing ----
trace_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(trace_provider)
span_exporter = OTLPSpanExporter(endpoint="http://otel-collector:4317")
trace_provider.add_span_processor(BatchSpanProcessor(span_exporter))
tracer = trace.get_tracer(__name__)

# ---- Metrics ----
metric_exporter = OTLPMetricExporter(endpoint="http://otel-collector:4317")
reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=5000)
metric_provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(metric_provider)
meter = metrics.get_meter(__name__)

# ---- Metric Instruments ----
job_counter = meter.create_counter("job_runs")
job_latency = meter.create_histogram("job_latency")

# ---- Logging ----
logging.basicConfig(level=logging.INFO)
handler = LoggingHandler()  # integrates with OTel logs
logger = logging.getLogger("job-logger")
logger.addHandler(handler)

# ---- Job Logic ----
with tracer.start_as_current_span("job_execution") as span:
    start = time.time()

    logger.info("Job started")
    time.sleep(1.4)  # simulate work
    logger.info("Job completed")

    job_counter.add(1)
    job_latency.record(time.time() - start)

print("DONE")
