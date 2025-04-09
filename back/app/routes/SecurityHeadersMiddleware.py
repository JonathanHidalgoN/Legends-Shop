from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Prevents the browser from MIME-sniffing a response away from the declared content-type
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevents the page from being displayed in a frame, to avoid clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enables the cross-site scripting (XSS) filter built into most browsers
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Enforces HTTPS by telling the browser to only connect using HTTPS for the next year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
