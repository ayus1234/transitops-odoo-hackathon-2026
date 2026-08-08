"""
Structured JSON Logging System using Structlog.
Provides JSON formatting in production, colored development formatting, and request-id correlation.
"""
import logging
import sys
import os
import time
import uuid
try:
    import structlog
except ImportError:
    structlog = None

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


def setup_logging():
    """Configure structlog processors based on ENVIRONMENT setting."""
    if not structlog:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        return
    environment = os.getenv("ENVIRONMENT", "development").lower()
    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if environment == "production":
        # Production: Clean JSON Output
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Development: Human-readable Colored Output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )


def get_logger(name: str = "transitops"):
    """Get a configured structlog logger instance."""
    if structlog:
        return structlog.get_logger(name)
    return logging.getLogger(name)


class LoggingMiddleware(BaseHTTPMiddleware):
    """HTTP Middleware injecting request_id correlation IDs and measuring request duration."""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
        if structlog is not None:
            structlog.contextvars.clear_contextvars()
            structlog.contextvars.bind_contextvars(
                request_id=request_id,
                method=request.method,
                path=request.url.path,
                client_ip=request.client.host if request.client else "unknown",
            )

        start_time = time.perf_counter()
        logger = get_logger("http_request")

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            
            if structlog is not None:
                logger.info(
                    "http_request_finished",
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                )
            else:
                logger.info(f"http_request_finished status_code={response.status_code} duration_ms={duration_ms}")
            response.headers["x-request-id"] = request_id
            return response
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            if structlog is not None:
                logger.error(
                    "http_request_exception",
                    error=str(exc),
                    duration_ms=duration_ms,
                )
            else:
                logger.error(f"http_request_exception error={exc} duration_ms={duration_ms}")
            raise exc
