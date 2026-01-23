"""
Helper Functions and Decorators

This module now re-exports decorators from decorators.py for backward compatibility.
New code should import decorators directly from app.utils.decorators.
"""

from functools import wraps
from flask import session, redirect, url_for, flash, request
from datetime import datetime

# Import all decorators for backward compatibility
from .decorators import (
    login_required,
    admin_required,
    department_user_required,
    admin_or_department_user_required,
    restrict_department_user_action
)

# Re-export for backward compatibility
__all__ = [
    'login_required',
    'admin_required',
    'department_user_required',
    'admin_or_department_user_required',
    'restrict_department_user_action',
    'format_currency',
    'format_date',
    'get_stock_status'
]


def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"


def format_date(date_string):
    """Format date string"""
    try:
        date_obj = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date_obj.strftime('%Y-%m-%d')
    except:
        return date_string


def get_stock_status(current_stock, low_limit):
    """Get stock status and color"""
    if current_stock <= low_limit:
        return 'danger', 'Low Stock'
    elif current_stock <= low_limit * 1.5:
        return 'warning', 'Medium Stock'
    else:
        return 'success', 'Good Stock'
