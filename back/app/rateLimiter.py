from slowapi import Limiter
from slowapi.util import get_remote_address
from app.envVariables import TESTING

#This means per client
limiter = Limiter(key_func=get_remote_address)


def authRateLimiter():
    """Rate limit for authentication endpoints"""
    limit : int = 5
    if TESTING:
        limit = 99999
    return limiter.limit(f"{limit}/minute")


def apiRateLimit():
    """Rate limit for general API endpoints"""
    limit : int = 60 
    if TESTING:
        limit = 99999
    return limiter.limit(f"{limit}/minute")


def sensitiveRateLimit():
    """Rate limit for sensitive operations"""
    limit : int = 3 
    if TESTING:
        limit = 99999
    return limiter.limit(f"{limit}/minute")
