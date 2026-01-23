"""
Dashboard Blueprint
Main dashboard with overview widgets and quick access
"""

from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.utils.decorators import login_required
from app.utils.database import get_medicines, get_patients, get_stores, get_consumption, get_low_stock_medicines

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard page - restricted for department users"""
    # Redirect department users to stores page instead of dashboard
    if session.get('role') == 'department_user':
        flash('Welcome! You have been redirected to your department store management.', 'info')
        return redirect(url_for('stores.index'))

    # Admin users can access the full dashboard
    # Get overview statistics
    medicines = get_medicines()
    patients = get_patients()
    stores = get_stores()
    consumption = get_consumption()
    
    # Calculate metrics
    total_medicines = len(medicines)
    total_patients = len(patients)
    low_stock_count = 0
    total_consumption_today = 0
    
    # Count low stock items
    user_department_id = session.get('department_id') if session.get('role') != 'admin' else None
    low_stock_medicines = get_low_stock_medicines(user_department_id)
    low_stock_count = len(low_stock_medicines)
    
    # Count today's consumption
    from datetime import datetime
    today = datetime.now().strftime('%Y-%m-%d')
    today_consumption = [c for c in consumption if c.get('date') == today]
    total_consumption_today = len(today_consumption)
    
    stats = {
        'total_medicines': total_medicines,
        'total_patients': total_patients,
        'low_stock_count': low_stock_count,
        'total_consumption_today': total_consumption_today
    }
    
    return render_template('dashboard/index.html', stats=stats)
