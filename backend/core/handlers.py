import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.exceptions import EnterpriseAgentLabError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EnterpriseAgentLabError)
    async def application_error_handler(
        request: Request,
        exc: EnterpriseAgentLabError,
    ) -> JSONResponse:
        logger.error("application_error path=%s error=%s", request.url.path, exc)
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": {
                    "code": exc.__class__.__name__.upper(),
                    "message": str(exc),
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warning("validation_error path=%s error=%s", request.url.path, exc)
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed.",
                },
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        logger.exception("unexpected_error path=%s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred.",
                },
            },
        )
