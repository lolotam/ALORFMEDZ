"""
Stores Management Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify, session
import csv
import io
from app.utils.decorators import login_required, admin_required, restrict_department_user_action
from app.utils.database import get_stores, update_store, delete_store, log_activity, get_medicines, get_departments, get_store_by_id, delete_department_and_store

stores_bp = Blueprint('stores', __name__)

@stores_bp.route('/')
@login_required
def index():
    """Stores overview page"""
    stores = get_stores()
    medicines = get_medicines()
    departments = get_departments()

    # Check if department parameter is provided (from department view store button)
    department_filter = request.args.get('department')

    # Filter stores based on department parameter or user role
    if department_filter:
        # Filter to show only the specific department's store
        stores = [s for s in stores if s.get('department_id') == department_filter]
    elif session.get('role') != 'admin':
        # Regular role-based filtering for non-admin users
        user_department_id = session.get('department_id')
        stores = [s for s in stores if s.get('department_id') == user_department_id]

    # Calculate total stock for each medicine (similar to medicines blueprint)
    for medicine in medicines:
        total_stock = 0
        for store in stores:
            inventory = store.get('inventory', {})
            stock = inventory.get(medicine['id'], 0)
            total_stock += stock
        medicine['total_stock'] = total_stock

        # Calculate stock status
        if total_stock == 0:
            medicine['stock_status'] = 'out'
        elif total_stock <= medicine.get('low_stock_limit', 0):
            medicine['stock_status'] = 'low'
        elif total_stock <= medicine.get('low_stock_limit', 0) * 1.5:
            medicine['stock_status'] = 'medium'
        else:
            medicine['stock_status'] = 'good'

    return render_template('stores/index.html', stores=stores, medicines=medicines, departments=departments, department_filter=department_filter)

@stores_bp.route('/edit/<store_id>', methods=['GET', 'POST'])
@login_required
def edit(store_id):
    """Edit store information (allowed for department users)"""
    store = get_store_by_id(store_id)
    if not store:
        flash('Store not found!', 'error')
        return redirect(url_for('stores.index'))

    # Department users can only edit their own store
    if session.get('role') == 'department_user':
        if store.get('department_id') != session.get('department_id'):
            flash('You can only edit your own department store.', 'error')
            return redirect(url_for('stores.index'))

    if request.method == 'POST':
        store_data = {
            'name': request.form.get('name', '').strip(),
            'location': request.form.get('location', '').strip(),
            'description': request.form.get('description', '').strip()
        }

        # Validate required fields
        if not store_data['name']:
            flash('Store name is required.', 'error')
            return render_template('stores/edit.html', store=store)

        try:
            update_store(store_id, store_data)
            flash('Store updated successfully!', 'success')
            return redirect(url_for('stores.index'))
        except Exception as e:
            flash(f'Error updating store: {str(e)}', 'error')

    return render_template('stores/edit.html', store=store)

@stores_bp.route('/export')
@login_required
def export_inventory():
    """Export inventory data to CSV (allowed for department users)"""
    stores = get_stores()
    medicines = get_medicines()
    departments = get_departments()

    # Filter stores based on user role
    if session.get('role') != 'admin':
        user_department_id = session.get('department_id')
        stores = [s for s in stores if s.get('department_id') == user_department_id]

    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)

    # Write headers
    writer.writerow(['Store Name', 'Department', 'Medicine Name', 'Form/Dosage', 'Current Stock', 'Low Stock Limit', 'Status'])

    # Write data
    for store in stores:
        department = next((d for d in departments if d['id'] == store.get('department_id')), None)
        department_name = department['name'] if department else 'Unknown'

        for medicine_id, stock in store.get('inventory', {}).items():
            medicine = next((m for m in medicines if m['id'] == medicine_id), None)
            if medicine:
                # Determine status
                if stock == 0:
                    status = 'Out of Stock'
                elif stock <= medicine.get('low_stock_limit', 0):
                    status = 'Low Stock'
                elif stock <= medicine.get('low_stock_limit', 0) * 1.5:
                    status = 'Medium Stock'
                else:
                    status = 'Good Stock'

                writer.writerow([
                    store['name'],
                    department_name,
                    medicine['name'],
                    medicine.get('form_dosage', ''),
                    stock,
                    medicine.get('low_stock_limit', 0),
                    status
                ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=inventory_export.csv'}
    )

@stores_bp.route('/delete/<store_id>')
@restrict_department_user_action('delete')
@admin_required
def delete(store_id):
    """Delete store with cascading delete of department and assigned users (admin only)"""
    # Get store info to find department
    stores = get_stores()
    store_to_delete = next((s for s in stores if s['id'] == store_id), None)

    if not store_to_delete:
        flash('Store not found!', 'error')
        return redirect(url_for('stores.index'))

    # Prevent deletion of main store
    if store_id == '01':
        flash('Cannot delete main store!', 'error')
        return redirect(url_for('stores.index'))

    department_id = store_to_delete.get('department_id')
    if not department_id:
        # If store has no department, just delete the store
        success, message = delete_store(store_id)
    else:
        # Use cascading delete that removes department and assigned users
        success, message = delete_department_and_store(department_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('stores.index'))

@stores_bp.route('/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete():
    """Bulk delete stores"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'No items selected for deletion'}), 400

        # Delete each item
        deleted_count = 0
        failed_items = []

        for store_id in ids:
            try:
                # Protect main store (id='01')
                if store_id == '01':
                    failed_items.append(f"Main Store (ID 01) cannot be deleted")
                    continue

                delete_store(store_id)
                deleted_count += 1

            except Exception as e:
                failed_items.append(f"Store ID {store_id}: {str(e)}")

        # Log the bulk delete activity
        log_activity(
            action='bulk_delete',
            entity_type='stores',
            details={'message': f'Bulk deleted {deleted_count} stores', 'count': deleted_count}
        )

        # Prepare response message
        if deleted_count == len(ids):
            message = f'Successfully deleted {deleted_count} stores'
            return jsonify({'success': True, 'message': message}), 200
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(ids)} stores. Failed: {", ".join(failed_items)}'
            return jsonify({'success': True, 'message': message, 'warnings': failed_items}), 200
        else:
            message = f'Failed to delete any stores. Errors: {", ".join(failed_items)}'
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk delete: {str(e)}'}), 500

@stores_bp.route('/delete_comprehensive/<store_id>')
@restrict_department_user_action('delete')
@admin_required
def delete_comprehensive(store_id):
    """Delete store and associated department comprehensively (admin only)"""
    # Get store info to find department
    stores = get_stores()
    store_to_delete = next((s for s in stores if s['id'] == store_id), None)

    if not store_to_delete:
        flash('Store not found!', 'error')
        return redirect(url_for('stores.index'))

    # Prevent deletion of main store
    if store_id == '01':
        flash('Cannot delete main store!', 'error')
        return redirect(url_for('stores.index'))

    department_id = store_to_delete.get('department_id')
    if not department_id:
        flash('Store has no associated department!', 'error')
        return redirect(url_for('stores.index'))

    # Use comprehensive deletion function
    success, message = delete_department_and_store(department_id)

    if success:
        flash(message, 'success')
    else:
        flash(message, 'error')

    return redirect(url_for('stores.index'))
