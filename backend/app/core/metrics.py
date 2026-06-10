from prometheus_client import Counter, Histogram

HTTP_REQUESTS = Counter(
    "ai_platform_http_requests_total",
    "Total HTTP requests to the platform API",
    ["method", "endpoint", "status"],
)

HTTP_LATENCY = Histogram(
    "ai_platform_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)

INFERENCE_REQUESTS = Counter(
    "ai_platform_inference_requests_total",
    "Total proxied inference requests",
    ["status"],
)

INFERENCE_LATENCY = Histogram(
    "ai_platform_inference_request_duration_seconds",
    "Inference proxy latency in seconds",
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0),
)
