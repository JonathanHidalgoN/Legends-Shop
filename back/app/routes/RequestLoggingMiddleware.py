import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from starlette.requests import Request
from app.logger import logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        start_time = time.time()

        client_host = (
            request.client.host
            if hasattr(request, "client") and request.client
            else "unknown"
        )
        logger.info(
            f"Request {request_id}: {request.method} {request.url} from {client_host}"
        )

        try:
            response = await call_next(request)

            duration = time.time() - start_time

            logger.info(
                f"Response {request_id}: {response.status_code} for {request.method} {request.url} completed in {duration:.4f}s"
            )

            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {str(e)}")
            raise
