from fastapi import FastAPI
from fastapi.responses import JSONResponse

from secondbrain.core.errors import domain_error_handler
from secondbrain.core.middleware import (
    BodySizeLimitMiddleware,
    RequestIdMiddleware,
    TimingMiddleware,
)
from secondbrain.core.telemetry import get_logger, setup_logging

logger = get_logger("secondbrain.api")

SERVER_VERSION = "0.1.0"
MIN_SUPPORTED_APP_VERSION = "0.1.0"


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="Second Brain API", version=SERVER_VERSION)

    app.add_middleware(BodySizeLimitMiddleware)
    app.add_middleware(TimingMiddleware)
    app.add_middleware(RequestIdMiddleware)

    app.add_exception_handler(Exception, domain_error_handler)

    @app.get("/healthz")
    async def healthz() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/readyz")
    async def readyz() -> JSONResponse:
        return JSONResponse({"status": "ok"})

    @app.get("/v1/meta")
    async def meta() -> JSONResponse:
        return JSONResponse(
            {
                "server_version": SERVER_VERSION,
                "min_supported_app_version": MIN_SUPPORTED_APP_VERSION,
            }
        )

    logger.info("api.started", version=SERVER_VERSION)
    return app
