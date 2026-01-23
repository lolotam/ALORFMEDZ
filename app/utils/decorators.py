"""
Authentication and Authorization Decorators

This module contains all decorators for authentication and authorization.
Separated from helpers.py for better code organization.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from time import perf_counter
import logging

logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        if session.get('role') != 'admin':
            flash('Admin access required for this page.', 'error')
            return redirect(url_for('dashboard.index'))

        return f(*args, **kwargs)
    return decorated_function


def department_user_required(f):
    """Decorator to require department user role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        if session.get('role') != 'department_user':
            flash('Department user access required for this page.', 'error')
            return redirect(url_for('dashboard.index'))

        return f(*args, **kwargs)
    return decorated_function


def admin_or_department_user_required(f):
    """Decorator to require admin or department user role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))

        if session.get('role') not in ['admin', 'department_user']:
            flash('Access denied. Admin or department user role required.', 'error')
            return redirect(url_for('auth.login'))

        return f(*args, **kwargs)
    return decorated_function


def restrict_department_user_action(action_name):
    """Decorator to restrict specific actions for department users"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))

            if session.get('role') == 'department_user':
                flash(f'Department users cannot perform {action_name} operations.', 'error')
                return redirect(request.referrer or url_for('dashboard.index'))

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def log_execution_time(f):
    """Decorator to log function execution time for performance monitoring"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = perf_counter()
        try:
            result = f(*args, **kwargs)
            execution_time = perf_counter() - start_time
            logger.debug(f"{f.__name__} executed in {execution_time:.4f}s")
            return result
        except Exception as e:
            execution_time = perf_counter() - start_time
            logger.error(f"{f.__name__} failed after {execution_time:.4f}s: {str(e)}")
            raise
    return decorated_function


def log_request(f):
    """Decorator to log incoming request details"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id', 'anonymous')
        logger.info(f"Request: {f.__name__} by user {user_id}")
        return f(*args, **kwargs)
    return decorated_function
