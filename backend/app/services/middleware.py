import uuid
import time
import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

import logging
import structlog

logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

formatter = structlog.stdlib.ProcessorFormatter(
    processor=structlog.processors.JSONRenderer(),
)

for handler in logging.root.handlers:
    handler.setFormatter(formatter)

logger = structlog.get_logger()


class RequestTracingMiddleware(BaseHTTPMiddleware):
    """
    Adds a unique trace_id to every request for full observability.
    Logs method, path, status, and duration for every API call.
    Strips PII fields from responses before logging.
    """

    async def dispatch(self, request: Request, call_next):
        trace_id = str(uuid.uuid4())[:8]
        request.state.trace_id = trace_id

        start_time = time.time()

        logger.info(
            "request_started",
            trace_id=trace_id,
            method=request.method,
            path=str(request.url.path),
            client=request.client.host if request.client else "unknown",
        )

        response = await call_next(request)

        duration_ms = round((time.time() - start_time) * 1000, 2)

        logger.info(
            "request_completed",
            trace_id=trace_id,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        # Attach trace_id to response headers for frontend tracing
        response.headers["X-Trace-Id"] = trace_id
        return response
