"""
Reports System Blueprint
"""

from flask import Blueprint, render_template, request, jsonify
from app.utils.decorators import login_required
from app.utils.database import get_consumption, get_purchases, get_stores, get_medicines, get_patients, get_suppliers, get_departments, get_low_stock_medicines, get_medicine_stock
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/')
@login_required
def index():
    """Reports dashboard"""
    # Get statistics for dashboard
    medicines = get_medicines()
    patients = get_patients()
    purchases = get_purchases()
    consumption = get_consumption()

    stats = {
        'total_medicines': len(medicines),
        'total_patients': len(patients),
        'total_purchases': len(purchases),
        'total_consumption': len(consumption)
    }

    return render_template('reports/index.html', **stats)

@reports_bp.route('/consumption')
@login_required
def consumption_report():
    """Consumption report with filters"""
    from flask import request, session

    # Get filter parameters
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    department_id = request.args.get('department_id')
    patient_id = request.args.get('patient_id')
    medicine_id = request.args.get('medicine_id')

    # Get all data
    consumption = get_consumption()
    medicines = get_medicines()
    patients = get_patients()
    departments = get_departments()

    # Apply filters
    filtered_consumption = consumption

    # Filter by user role
    if session.get('role') != 'admin':
        user_department_id = session.get('department_id')
        filtered_consumption = [c for c in filtered_consumption if c.get('department_id') == user_department_id]

    # Apply date filters
    if date_from:
        filtered_consumption = [c for c in filtered_consumption if c.get('date', '') >= date_from]
    if date_to:
        filtered_consumption = [c for c in filtered_consumption if c.get('date', '') <= date_to]

    # Apply other filters
    if department_id:
        filtered_consumption = [c for c in filtered_consumption if c.get('department_id') == department_id]
    if patient_id:
        filtered_consumption = [c for c in filtered_consumption if c.get('patient_id') == patient_id]
    if medicine_id:
        filtered_consumption = [c for c in filtered_consumption
                              if any(m.get('medicine_id') == medicine_id for m in c.get('medicines', []))]

    # Calculate statistics
    total_quantity = 0
    unique_patients = set()
    unique_medicines = set()

    for record in filtered_consumption:
        unique_patients.add(record.get('patient_id'))
        for medicine_item in record.get('medicines', []):
            total_quantity += medicine_item.get('quantity', 0)
            unique_medicines.add(medicine_item.get('medicine_id'))

    return render_template('reports/consumption.html',
                         consumption_data=filtered_consumption,
                         medicines=medicines,
                         patients=patients,
                         departments=departments,
                         total_quantity=total_quantity,
                         unique_patients=len(unique_patients),
                         unique_medicines=len(unique_medicines))

@reports_bp.route('/supplier')
@login_required
def supplier_report():
    """Supplier report with filters"""
    suppliers = get_suppliers()
    purchases = get_purchases()

    # Calculate supplier statistics
    supplier_stats = {}
    total_purchases = 0

    for purchase in purchases:
        supplier_id = purchase.get('supplier_id')
        total_purchases += 1

        if supplier_id not in supplier_stats:
            supplier_stats[supplier_id] = {
                'purchase_count': 0
            }

        supplier_stats[supplier_id]['purchase_count'] += 1

    # Enrich supplier data with statistics
    for supplier in suppliers:
        supplier_id = supplier['id']
        stats = supplier_stats.get(supplier_id, {'purchase_count': 0})
        supplier['purchase_count'] = stats['purchase_count']

    # Count active suppliers
    active_suppliers_count = len([s for s in suppliers if s.get('status', 'active') == 'active'])

    return render_template('reports/supplier.html',
                         suppliers=suppliers,
                         active_suppliers_count=active_suppliers_count,
                         total_purchases=total_purchases)

@reports_bp.route('/purchase')
@login_required
def purchase_report():
    """Purchase report with filters"""
    purchases = get_purchases()
    suppliers = get_suppliers()
    medicines = get_medicines()

    # Monthly purchases (current month)
    current_month = datetime.now().strftime('%Y-%m')
    monthly_purchases = len([p for p in purchases if p.get('purchase_date', '').startswith(current_month)])

    # Create lookup dictionaries
    supplier_dict = {s['id']: s['name'] for s in suppliers}
    medicine_dict = {m['id']: m['name'] for m in medicines}

    # Enrich purchase data with supplier names, medicine names, and normalize field names
    for purchase in purchases:
        supplier_id = purchase.get('supplier_id')
        purchase['supplier_name'] = supplier_dict.get(supplier_id, 'Unknown Supplier')

        # Enrich medicine data with names
        for medicine_item in purchase.get('medicines', []):
            medicine_id = medicine_item.get('medicine_id')
            medicine_item['medicine_name'] = medicine_dict.get(medicine_id, f'Unknown Medicine (ID: {medicine_id})')

        # Normalize field names for template compatibility
        # Preserve existing 'date' field, fall back to 'purchase_date' if 'date' is missing
        if not purchase.get('date'):
            purchase['date'] = purchase.get('purchase_date', '')

    return render_template('reports/purchase.html',
                         purchases=purchases,
                         suppliers=suppliers,
                         medicines=medicines,
                         monthly_purchases=monthly_purchases)

@reports_bp.route('/inventory')
@login_required
def inventory_report():
    """Inventory report with filters"""
    from flask import session, request

    # Get all data
    medicines = get_medicines()
    stores = get_stores()
    suppliers = get_suppliers()

    # Filter stores based on user role
    if session.get('role') != 'admin':
        user_department_id = session.get('department_id')
        stores = [s for s in stores if s.get('department_id') == user_department_id]

    # Apply filters from request parameters
    store_filter = request.args.get('store_id', '')
    medicine_filter = request.args.get('medicine_id', '')
    stock_status_filter = request.args.get('stock_status', '')

    # Filter stores if store filter is applied
    filtered_stores = stores
    if store_filter:
        filtered_stores = [s for s in stores if s.get('id') == store_filter]

    # Filter medicines if medicine filter is applied
    filtered_medicines = medicines
    if medicine_filter:
        filtered_medicines = [m for m in medicines if m.get('id') == medicine_filter]

    # Calculate total stock for each medicine and add it to medicine data
    for medicine in filtered_medicines:
        total_stock = 0
        for store in filtered_stores:
            total_stock += store.get('inventory', {}).get(medicine['id'], 0)
        medicine['total_stock'] = total_stock

    # Apply stock status filter if specified
    if stock_status_filter:
        if stock_status_filter == 'low':
            filtered_medicines = [m for m in filtered_medicines if m['total_stock'] <= m.get('low_stock_limit', 0)]
        elif stock_status_filter == 'medium':
            filtered_medicines = [m for m in filtered_medicines if m.get('low_stock_limit', 0) < m['total_stock'] <= m.get('low_stock_limit', 0) * 1.5]
        elif stock_status_filter == 'good':
            filtered_medicines = [m for m in filtered_medicines if m['total_stock'] > m.get('low_stock_limit', 0) * 1.5]
        elif stock_status_filter == 'out':
            filtered_medicines = [m for m in filtered_medicines if m['total_stock'] == 0]

    # Calculate statistics based on filtered data
    total_medicines = len(filtered_medicines)
    total_stock_value = 0
    low_stock_count = 0
    out_of_stock_count = 0
    good_stock_count = 0
    medium_stock_count = 0

    for medicine in filtered_medicines:
        total_stock = medicine['total_stock']
        total_stock_value += total_stock

        if total_stock == 0:
            out_of_stock_count += 1
        elif total_stock <= medicine.get('low_stock_limit', 0):
            low_stock_count += 1
        elif total_stock <= medicine.get('low_stock_limit', 0) * 1.5:
            medium_stock_count += 1
        else:
            good_stock_count += 1

    return render_template('reports/inventory.html',
                         medicines=filtered_medicines,
                         stores=filtered_stores,
                         suppliers=suppliers,
                         total_medicines=total_medicines,
                         total_stock_value=total_stock_value,
                         low_stock_count=low_stock_count,
                         out_of_stock_count=out_of_stock_count,
                         good_stock_count=good_stock_count,
                         medium_stock_count=medium_stock_count)

@reports_bp.route('/low-stock')
@login_required
def low_stock_report():
    """Low stock report"""
    from flask import session, request

    # Get department filter from request
    department_filter = request.args.get('department')

    # Get low stock items based on user role and filter
    if session.get('role') == 'admin':
        if department_filter:
            # Admin viewing specific department
            low_stock_items = get_low_stock_medicines(department_filter)
            # Set department_id for each item
            for item in low_stock_items:
                item['department_id'] = department_filter
        else:
            # Admin viewing all departments - get low stock items for each department
            low_stock_items = []
            stores = get_stores()
            medicines = get_medicines()

            for store in stores:
                department_id = store.get('department_id')
                if department_id:
                    for medicine in medicines:
                        stock = store.get('inventory', {}).get(medicine['id'], 0)
                        low_limit = medicine.get('low_stock_limit', 0)
                        if stock <= low_limit:
                            low_stock_items.append({
                                'medicine': medicine,
                                'current_stock': stock,
                                'low_stock_limit': low_limit,
                                'department_id': department_id
                            })
    else:
        # Department user - only their department
        user_department_id = session.get('department_id')
        low_stock_items = get_low_stock_medicines(user_department_id)
        for item in low_stock_items:
            item['department_id'] = user_department_id

    departments = get_departments()
    suppliers = get_suppliers()

    return render_template('reports/low_stock.html',
                         low_stock_items=low_stock_items,
                         departments=departments,
                         suppliers=suppliers,
                         department_filter=department_filter)

@reports_bp.route('/suggested-purchase')
@login_required
def suggested_purchase_report():
    """Suggested purchase report based on consumption patterns"""
    from flask import session
    from datetime import datetime, timedelta

    # Get data for analysis
    medicines = get_medicines()
    consumption = get_consumption()
    stores = get_stores()
    suppliers = get_suppliers()

    # Filter by user role
    if session.get('role') != 'admin':
        user_department_id = session.get('department_id')
        consumption = [c for c in consumption if c.get('department_id') == user_department_id]
        stores = [s for s in stores if s.get('department_id') == user_department_id]

    # Calculate consumption patterns (last 30 days)
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    recent_consumption = [c for c in consumption if c.get('date', '') >= thirty_days_ago]

    # Analyze consumption patterns
    medicine_consumption = {}
    for record in recent_consumption:
        for medicine_item in record.get('medicines', []):
            medicine_id = medicine_item.get('medicine_id')
            quantity = medicine_item.get('quantity', 0)

            if medicine_id not in medicine_consumption:
                medicine_consumption[medicine_id] = 0
            medicine_consumption[medicine_id] += quantity

    # Generate suggestions
    suggestions = []
    for medicine in medicines:
        medicine_id = medicine['id']

        # Get current stock using the proper function
        if session.get('role') == 'admin':
            current_stock = get_medicine_stock(medicine_id)  # Total across all stores
        else:
            user_department_id = session.get('department_id')
            current_stock = get_medicine_stock(medicine_id, user_department_id)  # Department-specific

        # Get consumption rate
        consumption_rate = medicine_consumption.get(medicine_id, 0)
        monthly_consumption = consumption_rate

        # Calculate suggested order quantity
        low_limit = medicine.get('low_stock_limit', 0)

        # Simple AI logic: if current stock is low and there's consumption, suggest reorder
        if current_stock <= low_limit and monthly_consumption > 0:
            # Suggest 2 months worth of consumption or minimum order quantity
            suggested_quantity = max(monthly_consumption * 2, low_limit * 2)

            supplier = next((s for s in suppliers if s['id'] == medicine.get('supplier_id')), None)

            suggestions.append({
                'medicine': medicine,
                'current_stock': current_stock,
                'monthly_consumption': monthly_consumption,
                'suggested_quantity': suggested_quantity,
                'supplier': supplier,
                'urgency': 'High' if current_stock == 0 else 'Medium' if current_stock <= low_limit else 'Low'
            })

    # Sort by urgency and consumption rate
    suggestions.sort(key=lambda x: (x['urgency'] == 'High', x['monthly_consumption']), reverse=True)

    return render_template('reports/suggested_purchase.html',
                         suggestions=suggestions,
                         total_suggestions=len(suggestions))
