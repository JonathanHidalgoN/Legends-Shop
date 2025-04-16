from slowapi import Limiter
from slowapi.util import get_remote_address

#This means per client
limiter = Limiter(key_func=get_remote_address)


def authRateLimiter():
    """Rate limit for authentication endpoints"""
    return limiter.limit("5/minute")


def apiRateLimit():
    """Rate limit for general API endpoints"""
    return limiter.limit("60/minute")


def sensitiveRateLimit():
    """Rate limit for sensitive operations"""
    return limiter.limit("3/minute")
