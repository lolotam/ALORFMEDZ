"""
Helper Functions and Decorators
"""

from functools import wraps
from flask import session, redirect, url_for, flash

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

def format_currency(amount):
    """Format amount as currency"""
    return f"${amount:,.2f}"

def format_date(date_string):
    """Format date string"""
    from datetime import datetime
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
