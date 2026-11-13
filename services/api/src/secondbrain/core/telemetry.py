import logging
from typing import Any

import structlog

REDACT_KEYS = {"password", "token", "authorization", "email", "text"}


def redact_values(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    for key in list(event_dict.keys()):
        if key.lower() in REDACT_KEYS:
            event_dict[key] = "[REDACTED]"
    return event_dict


def setup_logging() -> None:
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            redact_values,  # type: ignore[list-item]
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name)  # type: ignore[no-any-return]
