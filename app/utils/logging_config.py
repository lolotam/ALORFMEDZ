"""
Logging Configuration

This module configures structured logging for the application.
"""

import logging
import logging.handlers
import os
from datetime import datetime
from typing import Dict, Any


def setup_logging(app):
    """
    Configure logging for the Flask application.

    Args:
        app: Flask application instance
    """
    # Ensure log directory exists
    log_dir = app.config.get('LOG_DIR', 'logs')
    os.makedirs(log_dir, exist_ok=True)

    # Get log level from config
    log_level = app.config.get('LOG_LEVEL', 'INFO')
    log_format = app.config.get('LOG_FORMAT',
                                 '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s')

    # Create formatters
    detailed_formatter = logging.Formatter(
        log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Create handlers
    handlers = []

    # File handler for all logs
    all_logs_file = os.path.join(log_dir, 'app.log')
    all_logs_handler = logging.handlers.RotatingFileHandler(
        all_logs_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    all_logs_handler.setFormatter(detailed_formatter)
    handlers.append(all_logs_handler)

    # Separate error log file
    error_logs_file = os.path.join(log_dir, 'errors.log')
    error_logs_handler = logging.handlers.RotatingFileHandler(
        error_logs_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    error_logs_handler.setFormatter(detailed_formatter)
    error_logs_handler.setLevel(logging.ERROR)
    handlers.append(error_logs_handler)

    # Separate security log file
    security_logs_file = os.path.join(log_dir, 'security.log')
    security_logs_handler = logging.handlers.RotatingFileHandler(
        security_logs_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    security_logs_handler.setFormatter(detailed_formatter)
    security_logs_handler.setLevel(logging.INFO)
    handlers.append(security_logs_handler)

    # Separate performance log file
    performance_logs_file = os.path.join(log_dir, 'performance.log')
    performance_logs_handler = logging.handlers.RotatingFileHandler(
        performance_logs_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    performance_logs_handler.setFormatter(detailed_formatter)
    performance_logs_handler.setLevel(logging.INFO)
    handlers.append(performance_logs_handler)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        handlers=handlers,
        format=log_format,
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Get Flask logger
    app.logger.setLevel(getattr(logging, log_level.upper()))

    # Add file handlers to Flask logger
    for handler in handlers:
        app.logger.addHandler(handler)

    # Disable Flask's default console handler in production
    if not app.debug and not app.testing:
        app.logger.handlers.clear()

    app.logger.info(f"Logging configured - Level: {log_level}, Directory: {log_dir}")


class SecurityLogger:
    """Specialized logger for security events"""

    def __init__(self, name='security'):
        self.logger = logging.getLogger(name)

    def log_login_attempt(self, username: str, success: bool, ip_address: str,
                         user_agent: str = None, details: Dict[str, Any] = None):
        """Log login attempt"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Login {status} - Username: {username}, IP: {ip_address}"

        if user_agent:
            message += f", User-Agent: {user_agent}"

        if details:
            message += f", Details: {details}"

        self.logger.info(message)

    def log_logout(self, username: str, ip_address: str, details: Dict[str, Any] = None):
        """Log logout event"""
        message = f"Logout - Username: {username}, IP: {ip_address}"

        if details:
            message += f", Details: {details}"

        self.logger.info(message)

    def log_csrf_violation(self, ip_address: str, user_agent: str, details: Dict[str, Any] = None):
        """Log CSRF validation failure"""
        message = f"CSRF Violation - IP: {ip_address}, User-Agent: {user_agent}"

        if details:
            message += f", Details: {details}"

        self.logger.warning(message)

    def log_rate_limit_exceeded(self, identifier: str, limit: int, window: int,
                               ip_address: str, details: Dict[str, Any] = None):
        """Log rate limit violation"""
        message = f"Rate Limit Exceeded - ID: {identifier}, Limit: {limit}/{window}s, IP: {ip_address}"

        if details:
            message += f", Details: {details}"

        self.logger.warning(message)

    def log_unauthorized_access(self, username: str, resource: str, ip_address: str,
                                details: Dict[str, Any] = None):
        """Log unauthorized access attempt"""
        message = f"Unauthorized Access - User: {username}, Resource: {resource}, IP: {ip_address}"

        if details:
            message += f", Details: {details}"

        self.logger.warning(message)

    def log_password_change(self, username: str, ip_address: str, success: bool,
                           details: Dict[str, Any] = None):
        """Log password change event"""
        status = "SUCCESS" if success else "FAILED"
        message = f"Password Change {status} - Username: {username}, IP: {ip_address}"

        if details:
            message += f", Details: {details}"

        self.logger.info(message)


class PerformanceLogger:
    """Specialized logger for performance metrics"""

    def __init__(self, name='performance'):
        self.logger = logging.getLogger(name)

    def log_slow_query(self, query: str, execution_time: float, threshold: float = 1.0,
                      details: Dict[str, Any] = None):
        """Log slow database query"""
        message = f"Slow Query - Time: {execution_time:.4f}s (threshold: {threshold}s), Query: {query}"

        if details:
            message += f", Details: {details}"

        self.logger.warning(message)

    def log_slow_request(self, endpoint: str, method: str, execution_time: float,
                        threshold: float = 2.0, details: Dict[str, Any] = None):
        """Log slow HTTP request"""
        message = f"Slow Request - {method} {endpoint}, Time: {execution_time:.4f}s (threshold: {threshold}s)"

        if details:
            message += f", Details: {details}"

        self.logger.warning(message)

    def log_cache_hit(self, cache_key: str):
        """Log cache hit"""
        self.logger.debug(f"Cache Hit - Key: {cache_key}")

    def log_cache_miss(self, cache_key: str):
        """Log cache miss"""
        self.logger.debug(f"Cache Miss - Key: {cache_key}")

    def log_memory_usage(self, usage_mb: float, threshold_mb: float = 500):
        """Log memory usage"""
        if usage_mb > threshold_mb:
            self.logger.warning(f"High Memory Usage - {usage_mb:.2f} MB (threshold: {threshold_mb} MB)")
        else:
            self.logger.info(f"Memory Usage - {usage_mb:.2f} MB")


# Create specialized loggers
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()
