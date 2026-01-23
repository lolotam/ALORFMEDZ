"""
CSRF Protection Utilities

This module provides CSRF protection utilities for the Flask application.
While Flask-WTF provides CSRF protection, this module provides additional
helper functions for manual CSRF token generation and validation.
"""

import secrets
from functools import wraps
import logging
from flask import session, request, jsonify, current_app, redirect, url_for, flash

logger = logging.getLogger(__name__)

# CSRF token session key
CSRF_TOKEN_KEY = 'csrf_token'
CSRF_TOKEN_HEADER = 'X-CSRF-Token'
CSRF_FORM_KEY = 'csrf_token'


def generate_csrf_token():
    """Generate a CSRF token and store it in the session"""
    token = secrets.token_urlsafe(32)
    session[CSRF_TOKEN_KEY] = token
    return token


def validate_csrf_token(token):
    """Validate a CSRF token against the session"""
    if not token:
        return False

    session_token = session.get(CSRF_TOKEN_KEY)
    if not session_token:
        return False

    # Use constant-time comparison to prevent timing attacks
    return secrets.compare_digest(token, session_token)


def csrf_protect(f):
    """Decorator to protect endpoints with CSRF validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip CSRF check for GET, HEAD, OPTIONS requests
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return f(*args, **kwargs)

        # For AJAX requests, check the header
        token = request.headers.get(CSRF_TOKEN_HEADER)

        # For form requests, check the form data
        if not token:
            token = request.form.get(CSRF_FORM_KEY)

        # For JSON requests, check the JSON data
        if not token:
            try:
                if request.is_json:
                    data = request.get_json()
                    if data:
                        token = data.get(CSRF_FORM_KEY)
            except Exception:
                pass

        if not validate_csrf_token(token):
            logger.warning(f"CSRF validation failed for {request.method} {request.url}")
            
            # Log reason for debugging
            if not token:
                logger.warning("CSRF failure: No token provided in request")
            elif not session.get(CSRF_TOKEN_KEY):
                logger.warning("CSRF failure: No token found in session (session expired or cookie missing)")
            else:
                logger.warning("CSRF failure: Token mismatch")

            if request.is_json or is_ajax_request():
                return jsonify({
                    'success': False,
                    'error': 'CSRF token validation failed',
                    'message': 'Invalid or missing CSRF token'
                }), 403
            else:
                # For standard form requests, flash error and redirect back
                flash('Your session has expired or the security token is invalid. Please try again.', 'error')
                return redirect(request.referrer or url_for('auth.login'))

        return f(*args, **kwargs)

    return decorated_function


def get_csrf_token():
    """Get or generate a CSRF token for the current session"""
    return generate_csrf_token()


def get_csrf_token_for_ajax():
    """Get CSRF token in a format suitable for AJAX requests"""
    token = get_csrf_token()
    return {
        'csrf_token': token,
        'header_name': CSRF_TOKEN_HEADER,
        'form_name': CSRF_FORM_KEY
    }


def is_ajax_request():
    """Check if the current request is an AJAX request"""
    return (request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Accept', '').startswith('application/json') or
            request.path.startswith('/api/'))


def require_csrf_token():
    """Ensure a CSRF token exists in the session (for JavaScript to retrieve)"""
    if CSRF_TOKEN_KEY not in session:
        generate_csrf_token()


class CSRFError(Exception):
    """Exception raised when CSRF validation fails"""
    pass


def handle_csrf_error(error):
    """Error handler for CSRF validation errors"""
    logger.error(f"CSRF Error: {str(error)}")
    if request.is_json or is_ajax_request():
        return jsonify({
            'success': False,
            'error': 'CSRF validation failed',
            'message': 'Invalid or missing CSRF token. Please refresh the page and try again.'
        }), 403
    else:
        return jsonify({
            'success': False,
            'error': 'Security error',
            'message': 'Your session may have expired. Please refresh and try again.'
        }), 403
