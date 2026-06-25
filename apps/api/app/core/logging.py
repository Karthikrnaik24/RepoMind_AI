"""Structured logging configuration.

Logging is intentionally centralized so request middleware, services, workers,
and infrastructure adapters emit consistent JSON records without including
secrets or sensitive payloads.
"""

import json
import logging
import logging.config
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from app.config.settings import Settings

request_id_context: ContextVar[str | None] = ContextVar("request_id", default=None)
_STANDARD_LOG_RECORD_KEYS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


def set_request_id(request_id: str | None) -> None:
    """Store the current request ID for log enrichment."""

    request_id_context.set(request_id)


def get_request_id() -> str | None:
    """Return the current request ID when available."""

    return request_id_context.get()


class RequestIdFilter(logging.Filter):
    """Attach request_id to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonLogFormatter(logging.Formatter):
    """Format log records as compact JSON for production ingestion."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", None),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_RECORD_KEYS and key not in payload:
                payload[key] = value
        return json.dumps(payload, default=str, separators=(",", ":"))


def build_logging_config(settings: Settings) -> dict[str, Any]:
    """Build a dictConfig payload from validated settings."""

    formatter_name = "json" if settings.log_json else "standard"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {"()": RequestIdFilter},
        },
        "formatters": {
            "json": {"()": JsonLogFormatter},
            "standard": {
                "format": "%(asctime)s %(levelname)s [%(request_id)s] %(name)s: %(message)s",
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": formatter_name,
                "filters": ["request_id"],
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["default"],
        },
    }


def configure_logging(settings: Settings) -> None:
    """Configure Python logging for the current process."""

    logging.config.dictConfig(build_logging_config(settings))


def get_logger(name: str = "repomind") -> logging.Logger:
    """Return a named structured logger."""

    return logging.getLogger(name)
