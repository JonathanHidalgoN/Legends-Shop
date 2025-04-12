from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.types import ASGIApp

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
# X-Content-Type-Options: nosniff
# What it does:
# Tells the browser: “Do not try to guess the type of content — trust the Content-Type header only.”
#
# Why it's important:
# Attackers might upload malicious scripts (like .js) disguised as other types (like .jpg). Some browsers try to sniff and guess what a file really is, and may execute it. This header prevents that behavior.
#
# Analogy:
# Like saying, "Don’t trust a file that looks like food if it says it’s poison."
        response.headers["X-Content-Type-Options"] = "nosniff"
        
# X-Frame-Options: DENY
# What it does:
# Tells the browser: “Never allow this page to be embedded in an iframe.”
#
# Why it's important:
# Prevents clickjacking — a trick where attackers load your page in an invisible iframe and get the user to click buttons unknowingly (like "Send money").
#
# Analogy:
# You’re saying, “Don’t let my page live inside someone else’s picture frame.”
        response.headers["X-Frame-Options"] = "DENY"
        
# X-XSS-Protection: 1; mode=block
# What it does:
# Tells the browser: “If you detect a cross-site scripting (XSS) attack, block the page completely.”
#
# Why it's important:
# Old browsers had basic XSS filters. This header activates them and tells the browser to stop rendering if it sees something sketchy.
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
# Strict-Transport-Security: max-age=31536000; includeSubDomains
# What it does:
# Tells the browser: “Only talk to me using HTTPS — forever (or at least for a year).”
#
# Why it's important:
# Prevents downgrade attacks. Without this, someone can trick a user into visiting your site via http://, and then sniff or tamper with data.
#
# Analogy:
# It’s like telling your friend, “Only talk to me on encrypted calls from now on.”
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
