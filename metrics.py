from prometheus_client import Counter, Histogram, Gauge, Info, Summary


REQUEST_COUNT=Counter(
    "llm_requests_total",
    "Total number of LLM requests",
    ["backend","model","status"]
)

REQUEST_LATENCY=Histogram(
    "llm_request_latency_seconds",
    "Request proccesing latency",
    ["backend","model"]
)

ACTIVE_REQUESTS=Gauge(
    "llm_active_requests",
    "Current procceessing LLM requests",
    ["backend","model"]
)

INPUT_TOKENS = Counter(
    "llm_input_tokens_total",
    "Total number of input tokens",
    ["backend","model"]
)

OUTPUT_TOKENS = Counter(
    "llm_output_tokens_total",
    "Total number of output tokens",
    ["backend","model"]
)
TOKENS_PER_SECOND = Gauge(
    "llm_tokens_per_second",
    "Tokens per second",
    ["backend","model"]
)

MODEL_INFO = Info(
    "llm_model_info",
    "Information about the LLM model",
    
)

#basic governance metrics
RATE_LIMIT_EXCEEDED = Counter(
    "llm_rate_limit_exceeded_total",
    "rate limit violations",
    ["user"]
)

USER_REQUEST_COUNT = Counter(
    "llm_user_request_count_total",
    "Total number of requests by user",
    ["user"]
)


# helper func
def record_request(backend: str, user: str, model: str, status: str, latency: float, tokens_in: int, tokens_out: int):
    REQUEST_COUNT.labels(backend=backend, model=model, status=status).inc()
    REQUEST_LATENCY.labels(backend=backend, model=model).observe(latency)
    if tokens_in > 0:
        INPUT_TOKENS.labels(backend=backend, model=model).inc(tokens_in)
    if tokens_out > 0:
        OUTPUT_TOKENS.labels(backend=backend, model=model).inc(tokens_out)
    MODEL_INFO.info({"model": model, "backend": backend})
    USER_REQUEST_COUNT.labels(user=user).inc()

def set_active_requests(backend: str, model: str, count: int):
    """Set the current number of active requests"""
    ACTIVE_REQUESTS.labels(backend=backend, model=model).set(count)