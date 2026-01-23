"""
Blueprint Response Helpers

Standardized response helpers for Flask blueprints.
Provides consistent API response format across all modules.
"""

from flask import jsonify, redirect, url_for, flash


def success_response(message, data=None, status=200):
    """Return a successful JSON response

    Args:
        message: Success message string
        data: Optional data dictionary to include in response
        status: HTTP status code (default: 200)

    Returns:
        Tuple of (jsonify response, status code)
    """
    response = {
        'success': True,
        'message': message
    }
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def error_response(message, status=400):
    """Return an error JSON response

    Args:
        message: Error message string
        status: HTTP status code (default: 400)

    Returns:
        Tuple of (jsonify response, status code)
    """
    return jsonify({
        'success': False,
        'message': message
    }), status


def validation_response(errors):
    """Return a validation error response

    Args:
        errors: Dictionary of field errors or list of error messages

    Returns:
        Tuple of (jsonify response, status code 422)
    """
    return jsonify({
        'success': False,
        'message': 'Validation failed',
        'errors': errors
    }), 422


def redirect_response(endpoint, **kwargs):
    """Return a redirect response to a named endpoint

    Args:
        endpoint: Flask endpoint name
        **kwargs: Arguments to pass to url_for

    Returns:
        Flask redirect response
    """
    return redirect(url_for(endpoint, **kwargs))


def flash_success(message, redirect_endpoint=None, **kwargs):
    """Flash success message and optionally redirect

    Args:
        message: Success message
        redirect_endpoint: Optional endpoint to redirect to
        **kwargs: Arguments to pass to url_for if redirecting

    Returns:
        None if no redirect, otherwise redirect response
    """
    flash(message, 'success')
    if redirect_endpoint:
        return redirect_response(redirect_endpoint, **kwargs)
    return None


def flash_error(message, redirect_endpoint=None, **kwargs):
    """Flash error message and optionally redirect

    Args:
        message: Error message
        redirect_endpoint: Optional endpoint to redirect to
        **kwargs: Arguments to pass to url_for if redirecting

    Returns:
        None if no redirect, otherwise redirect response
    """
    flash(message, 'error')
    if redirect_endpoint:
        return redirect_response(redirect_endpoint, **kwargs)
    return None


def flash_warning(message, redirect_endpoint=None, **kwargs):
    """Flash warning message and optionally redirect

    Args:
        message: Warning message
        redirect_endpoint: Optional endpoint to redirect to
        **kwargs: Arguments to pass to url_for if redirecting

    Returns:
        None if no redirect, otherwise redirect response
    """
    flash(message, 'warning')
    if redirect_endpoint:
        return redirect_response(redirect_endpoint, **kwargs)
    return None


def flash_info(message, redirect_endpoint=None, **kwargs):
    """Flash info message and optionally redirect

    Args:
        message: Info message
        redirect_endpoint: Optional endpoint to redirect to
        **kwargs: Arguments to pass to url_for if redirecting

    Returns:
        None if no redirect, otherwise redirect response
    """
    flash(message, 'info')
    if redirect_endpoint:
        return redirect_response(redirect_endpoint, **kwargs)
    return None
