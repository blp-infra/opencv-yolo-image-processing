from fastapi import FastAPI, Request
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app
import logging
from pythonjsonlogger import jsonlogger
import time

# Configure JSON logging for ELK
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(name)s %(levelname)s %(message)s',
    rename_fields={
        "asctime": "@timestamp",
        "levelname": "level",
        "name": "logger"
    }
)
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# Define service resource
resource = Resource.create({
    "service.name": "fastapi-test-app",
    "service.version": "1.0.0",
    "deployment.environment": "development"
})

# Setup Tracing (exports to Jaeger via OTLP)
trace_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://localhost:4317",  # Jaeger OTLP gRPC endpoint
    insecure=True
)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(__name__)

# Setup Metrics (exports to Prometheus)
prometheus_reader = PrometheusMetricReader()
metrics_provider = MeterProvider(
    resource=resource,
    metric_readers=[prometheus_reader]
)
metrics.set_meter_provider(metrics_provider)
meter = metrics.get_meter(__name__)

# Create custom metrics
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

request_duration = meter.create_histogram(
    name="http_request_duration_seconds",
    description="HTTP request duration in seconds",
    unit="s"
)

# Create FastAPI app
app = FastAPI(title="Observability Test App")

# Instrument FastAPI with OpenTelemetry
FastAPIInstrumentor.instrument_app(app)

# Add middleware for logging and metrics
@app.middleware("http")
async def log_and_metric_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Log request
    logger.info(
        "Incoming request",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_host": request.client.host if request.client else None
        }
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Record metrics
    request_counter.add(
        1,
        {
            "method": request.method,
            "endpoint": request.url.path,
            "status_code": response.status_code
        }
    )
    
    request_duration.record(
        duration,
        {
            "method": request.method,
            "endpoint": request.url.path,
            "status_code": response.status_code
        }
    )
    
    # Log response
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_seconds": duration
        }
    )
    
    return response

# Mount Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Processing root endpoint")
    with tracer.start_as_current_span("root_handler") as span:
        span.set_attribute("custom.attribute", "hello-world")
        return {"message": "Hello World", "status": "ok"}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get user by ID"""
    logger.info(f"Fetching user", extra={"user_id": user_id})
    with tracer.start_as_current_span("get_user") as span:
        span.set_attribute("user.id", user_id)
        # Simulate some work
        time.sleep(0.1)
        return {"user_id": user_id, "name": f"User {user_id}"}

@app.post("/data")
async def create_data(payload: dict):
    """Create data endpoint"""
    logger.info("Creating data", extra={"payload_keys": list(payload.keys())})
    with tracer.start_as_current_span("create_data") as span:
        span.set_attribute("data.size", len(payload))
        return {"status": "created", "data": payload}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)