"""
Rate Limiting Utilities

This module provides rate limiting functionality to protect against
brute force attacks and API abuse.
"""

import time
import threading
from collections import defaultdict, deque
from flask import request, jsonify, session, g, current_app
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# In-memory storage for rate limiting (use Redis in production)
_rate_limits = defaultdict(deque)
_lock = threading.Lock()


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self._store = defaultdict(deque)
        self._lock = threading.Lock()

    def is_allowed(self, key, limit, window):
        """
        Check if a request is allowed within the rate limit.

        Args:
            key: Unique identifier (e.g., IP address, user ID)
            limit: Maximum number of requests allowed
            window: Time window in seconds

        Returns:
            bool: True if allowed, False if rate limited
        """
        with self._lock:
            now = time.time()
            requests = self._store[key]

            # Remove old requests outside the window
            while requests and now - requests[0] > window:
                requests.popleft()

            # Check if we're under the limit
            if len(requests) >= limit:
                logger.warning(f"Rate limit exceeded for key: {key}")
                return False

            # Add current request
            requests.append(now)
            return True

    def get_count(self, key):
        """Get current count for a key"""
        with self._lock:
            now = time.time()
            requests = self._store[key]

            # Remove old requests
            while requests and now - requests[0] > self.window:
                requests.popleft()

            return len(requests)

    def reset(self, key):
        """Reset rate limit for a key"""
        with self._lock:
            if key in self._store:
                del self._store[key]


# Global rate limiter instance
_rate_limiter = RateLimiter()


def get_client_identifier():
    """
    Get a unique identifier for the client.
    Uses session ID if available, otherwise falls back to IP address.
    """
    try:
        # Use session ID if available (more accurate for logged-in users)
        if 'user_id' in session:
            return f"user:{session['user_id']}"

        # Fall back to IP address
        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        if ip:
            # Take first IP if multiple are present
            ip = ip.split(',')[0].strip()
        return f"ip:{ip}"
    except RuntimeError:
        # request context not available (e.g., during app initialization)
        return "system:init"


def rate_limit(limit, window, key_func=None):
    """
    Decorator to apply rate limiting to an endpoint.

    Args:
        limit: Maximum number of requests allowed
        window: Time window in seconds
        key_func: Function to generate the key (defaults to get_client_identifier)

    Usage:
        @rate_limit(5, 300)  # 5 requests per 5 minutes
        @rate_limit(100, 3600)  # 100 requests per hour
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key_func_local = key_func or get_client_identifier
            key = key_func_local()

            if not _rate_limiter.is_allowed(key, limit, window):
                response_data = {
                    'success': False,
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again later.',
                    'retry_after': window
                }

                # Create response with headers
                response = jsonify(response_data)
                response.headers['X-RateLimit-Limit'] = str(limit)
                response.headers['X-RateLimit-Remaining'] = '0'
                response.headers['X-RateLimit-Reset'] = str(int(time.time()) + window)
                response.headers['Retry-After'] = str(window)

                return response, 429

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_rate_limit_status(limit, window, key_func=None):
    """
    Get the current rate limit status for a client.

    Returns:
        dict: Contains current count, limit, and reset time
    """
    key_func_local = key_func or get_client_identifier
    key = key_func_local()

    with _rate_limiter._lock:
        now = time.time()
        requests = _rate_limiter._store[key]

        # Remove old requests
        while requests and now - requests[0] > window:
            requests.popleft()

        current_count = len(requests)
        remaining = max(0, limit - current_count)
        reset_time = int(now + window)

        return {
            'limit': limit,
            'window': window,
            'current': current_count,
            'remaining': remaining,
            'reset_time': reset_time
        }


# Predefined rate limiters for common use cases
login_rate_limit = rate_limit(5, 900)  # 5 login attempts per 15 minutes
api_rate_limit = rate_limit(100, 3600)  # 100 API requests per hour
upload_rate_limit = rate_limit(10, 60)  # 10 uploads per minute
general_rate_limit = rate_limit(200, 3600)  # 200 requests per hour


class RateLimitError(Exception):
    """Exception raised when rate limit is exceeded"""
    pass
