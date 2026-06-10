import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(
        self,
        message: str,
        code: str,
        status_code: int = 400,
        hint: str | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.hint = hint
        super().__init__(message)


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _error_body(
    request: Request,
    *,
    detail: str,
    code: str,
    hint: str | None = None,
    errors: list | None = None,
) -> dict:
    body: dict = {"detail": detail, "code": code}
    request_id = _request_id(request)
    if request_id:
        body["request_id"] = request_id
    if hint:
        body["hint"] = hint
    if errors is not None:
        body["errors"] = errors
    return body


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        logger.warning(
            "app_error request_id=%s code=%s status=%s detail=%s",
            _request_id(request),
            exc.code,
            exc.status_code,
            exc.message,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(request, detail=exc.message, code=exc.code, hint=exc.hint),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.info(
            "validation_error request_id=%s errors=%s",
            _request_id(request),
            exc.errors(),
        )
        return JSONResponse(
            status_code=422,
            content=_error_body(
                request,
                detail="Request validation failed. Check the errors field for details.",
                code="VALIDATION_ERROR",
                hint="See /docs for the expected request schema.",
                errors=exc.errors(),
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(request, detail=detail, code="HTTP_ERROR"),
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("unhandled_error request_id=%s", _request_id(request))
        return JSONResponse(
            status_code=500,
            content=_error_body(
                request,
                detail="An unexpected error occurred. Please try again or contact support.",
                code="INTERNAL_ERROR",
                hint="Retry the request. If the problem persists, check server logs with the request_id.",
            ),
        )
