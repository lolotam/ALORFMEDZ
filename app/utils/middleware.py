"""
Middleware for request/response logging and performance monitoring
"""

import time
import logging
from flask import request, g, session, jsonify, current_app
from functools import wraps
from .logging_config import performance_logger, security_logger


def setup_middleware(app):
    """
    Setup middleware for the Flask application.

    Args:
        app: Flask application instance
    """
    # Request timing middleware
    @app.before_request
    def before_request():
        """Record start time for request"""
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Log request and response details"""
        # Calculate response time
        if hasattr(g, 'start_time'):
            response_time = time.time() - g.start_time

            # Log slow requests (>2 seconds)
            if response_time > 2.0:
                try:
                    performance_logger.log_slow_request(
                        endpoint=request.path,
                        method=request.method,
                        execution_time=response_time,
                        threshold=2.0
                    )
                except RuntimeError:
                    # Request context not available
                    pass

        # Add security headers in production
        if not app.debug and app.config.get('SECURITY_HEADERS_ENABLED'):
            # HSTS Header
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

            # Content Type Options
            response.headers['X-Content-Type-Options'] = 'nosniff'

            # Frame Options
            response.headers['X-Frame-Options'] = 'DENY'

            # XSS Protection
            response.headers['X-XSS-Protection'] = '1; mode=block'

            # Content Security Policy
            response.headers['Content-Security-Policy'] = "default-src 'self'"

            # Referrer Policy
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Add CORS headers for API endpoints
        try:
            if request.path.startswith('/api/'):
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
                response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRF-Token'
        except RuntimeError:
            # Request context not available
            pass

        # Add custom headers
        response.headers['X-Content-Type-Options'] = 'nosniff'

        return response

    # Error handler middleware
    @app.errorhandler(Exception)
    def handle_exception(e):
        """Global exception handler"""
        # Log the error
        logging.exception("Unhandled exception occurred")

        # Return JSON response for API requests
        try:
            if request.is_json or request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': 'Internal server error',
                    'message': 'An unexpected error occurred. Please try again later.'
                }), 500
        except RuntimeError:
            # Request context not available
            pass

        # Return HTML for regular requests
        raise e


def monitor_performance(threshold: float = 1.0):
    """
    Decorator to monitor function performance.

    Args:
        threshold: Time threshold in seconds (default: 1.0)

    Usage:
        @monitor_performance(threshold=0.5)
        def expensive_function():
            pass
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                execution_time = time.time() - start_time

                if execution_time > threshold:
                    performance_logger.log_slow_query(
                        query=f.__name__,
                        execution_time=execution_time,
                        threshold=threshold
                    )

                return result
            except Exception as e:
                execution_time = time.time() - start_time
                performance_logger.log_slow_query(
                    query=f"{f.__name__} (failed)",
                    execution_time=execution_time,
                    threshold=threshold
                )
                raise
        return decorated_function
    return decorator


def log_activity(activity_type: str, entity_type: str = None, entity_id: str = None,
                 details: dict = None):
    """
    Log user activity.

    Args:
        activity_type: Type of activity (LOGIN, LOGOUT, CREATE, UPDATE, DELETE, etc.)
        entity_type: Type of entity (user, patient, medicine, etc.)
        entity_id: ID of the entity
        details: Additional details
    """
    logger = logging.getLogger('activity')
    logger.setLevel(logging.INFO)

    # Get current user info
    user_id = session.get('user_id', 'anonymous')
    username = session.get('username', 'unknown')
    try:
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    except RuntimeError:
        # Request context not available
        ip_address = 'unknown'

    # Build message
    message = f"Activity - User: {username} (ID: {user_id}), Type: {activity_type}"

    if entity_type:
        message += f", Entity: {entity_type}"

    if entity_id:
        message += f", ID: {entity_id}"

    if ip_address:
        message += f", IP: {ip_address}"

    if details:
        message += f", Details: {details}"

    logger.info(message)
