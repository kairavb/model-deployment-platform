import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.metrics import HTTP_LATENCY, HTTP_REQUESTS

logger = logging.getLogger("app.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id

        start = time.perf_counter()
        method = request.method
        path = request.url.path

        logger.info("request_started request_id=%s method=%s path=%s", request_id, method, path)

        try:
            response = await call_next(request)
        except Exception:
            duration = time.perf_counter() - start
            endpoint = _endpoint_label(request)
            HTTP_REQUESTS.labels(method=method, endpoint=endpoint, status="500").inc()
            HTTP_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
            logger.exception(
                "request_failed request_id=%s method=%s path=%s duration_ms=%.1f",
                request_id,
                method,
                path,
                duration * 1000,
            )
            raise

        duration = time.perf_counter() - start
        endpoint = _endpoint_label(request)
        status = str(response.status_code)
        HTTP_REQUESTS.labels(method=method, endpoint=endpoint, status=status).inc()
        HTTP_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed request_id=%s method=%s path=%s status=%s duration_ms=%.1f",
            request_id,
            method,
            path,
            status,
            duration * 1000,
        )
        return response


def _endpoint_label(request: Request) -> str:
    route = request.scope.get("route")
    if route is not None and hasattr(route, "path"):
        return route.path
    return request.url.path
