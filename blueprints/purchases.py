"""
Purchases Management Blueprint (Admin Only)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify, session
from utils.helpers import login_required, admin_required
from utils.database import get_purchases, save_purchase, update_purchase, delete_purchase, log_activity, get_suppliers, get_medicines, update_main_store_inventory
from datetime import datetime

purchases_bp = Blueprint('purchases', __name__)

@purchases_bp.route('/')
@admin_required
def index():
    """Purchases list page"""
    purchases = get_purchases()
    suppliers = get_suppliers()
    medicines = get_medicines()



    return render_template('purchases/index.html', purchases=purchases, suppliers=suppliers, medicines=medicines)

@purchases_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    """Add new purchase"""
    if request.method == 'POST':
        # Handle multiple medicines in purchase
        medicines_data = []
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')
        
        for i, medicine_id in enumerate(medicine_ids):
            if medicine_id and i < len(quantities):
                medicines_data.append({
                    'medicine_id': medicine_id,
                    'quantity': int(quantities[i])
                })
        
        purchase_data = {
            'date': request.form.get('date'),
            'invoice_number': request.form.get('invoice_number'),
            'supplier_id': request.form.get('supplier_id'),
            'medicines': medicines_data,
            'purchaser_name': request.form.get('purchaser_name'),
            'notes': request.form.get('notes', ''),
            'status': request.form.get('status', 'complete')
        }

        # Add delivery fields only if status is 'delivered'
        if purchase_data['status'] == 'delivered':
            purchase_data['delivery_date'] = request.form.get('delivery_date')
            purchase_data['received_by'] = request.form.get('received_by')

            # Update inventory for delivered purchases
            from utils.database import get_purchases, save_purchase, update_purchase, delete_purchase, log_activity
            update_main_store_inventory(medicines_data, 'add')

        purchase_id = save_purchase(purchase_data)
        flash(f'Purchase added successfully with ID: {purchase_id}', 'success')
        return redirect(url_for('purchases.index'))
    
    suppliers = get_suppliers()
    medicines = get_medicines()
    return render_template('purchases/add.html', suppliers=suppliers, medicines=medicines)

@purchases_bp.route('/edit/<purchase_id>', methods=['GET', 'POST'])
@admin_required
def edit(purchase_id):
    """Edit purchase"""
    purchases = get_purchases()
    purchase = next((p for p in purchases if p['id'] == purchase_id), None)

    if not purchase:
        flash('Purchase not found!', 'error')
        return redirect(url_for('purchases.index'))

    if request.method == 'POST':
        # Handle multiple medicines in purchase
        medicines_data = []
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')

        for i, medicine_id in enumerate(medicine_ids):
            if medicine_id and i < len(quantities):
                medicines_data.append({
                    'medicine_id': medicine_id,
                    'quantity': int(quantities[i])
                })

        # Validate that at least one medicine is provided
        if not medicines_data:
            flash('At least one medicine must be added to the purchase.', 'error')
            suppliers = get_suppliers()
            medicines = get_medicines()
            return render_template('purchases/edit.html', purchase=purchase, suppliers=suppliers, medicines=medicines)

        # Get current purchase to check for status changes
        current_status = purchase.get('status', 'complete')
        new_status = request.form.get('status', 'complete')

        purchase_data = {
            'date': request.form.get('date'),
            'invoice_number': request.form.get('invoice_number'),
            'supplier_id': request.form.get('supplier_id'),
            'medicines': medicines_data,
            'purchaser_name': request.form.get('purchaser_name'),
            'notes': request.form.get('notes', ''),
            'status': new_status
        }

        # Add delivery fields only if status is 'delivered'
        if new_status == 'delivered':
            purchase_data['delivery_date'] = request.form.get('delivery_date')
            purchase_data['received_by'] = request.form.get('received_by')

        # Handle stock updates based on status changes
        if current_status != new_status:
            from utils.database import get_purchases, save_purchase, update_purchase, delete_purchase, log_activity

            # If changing FROM delivered TO complete/pending: subtract stock
            if current_status == 'delivered' and new_status in ['complete', 'pending']:
                update_main_store_inventory(medicines_data, 'subtract')

            # If changing FROM complete/pending TO delivered: add stock
            elif current_status in ['complete', 'pending'] and new_status == 'delivered':
                update_main_store_inventory(medicines_data, 'add')

        update_purchase(purchase_id, purchase_data)
        flash('Purchase updated successfully!', 'success')
        return redirect(url_for('purchases.index'))

    suppliers = get_suppliers()
    medicines = get_medicines()
    return render_template('purchases/edit.html', purchase=purchase, suppliers=suppliers, medicines=medicines)

@purchases_bp.route('/delete/<purchase_id>')
@admin_required
def delete(purchase_id):
    """Delete purchase"""
    purchases = get_purchases()
    purchase = next((p for p in purchases if p['id'] == purchase_id), None)

    if not purchase:
        flash('Purchase not found!', 'error')
        return redirect(url_for('purchases.index'))

    # Handle inventory adjustment if purchase was delivered
    if purchase.get('status') == 'delivered':
        medicines_data = purchase.get('medicines', [])
        try:
            update_main_store_inventory(medicines_data, 'subtract')
        except Exception as e:
            flash(f'Warning: Could not adjust inventory: {str(e)}', 'warning')

    try:
        delete_purchase(purchase_id)
        flash('Purchase deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting purchase: {str(e)}', 'error')

    return redirect(url_for('purchases.index'))

@purchases_bp.route('/bulk-delete', methods=['POST'])
@admin_required
def bulk_delete():
    """Bulk delete purchases"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'No items selected for deletion'}), 400

        # Get all purchases to check inventory adjustments
        purchases = get_purchases()

        # Delete each item
        deleted_count = 0
        failed_items = []

        for purchase_id in ids:
            try:
                # Find the purchase to check if inventory adjustment is needed
                purchase = next((p for p in purchases if p['id'] == purchase_id), None)

                if purchase:
                    # Handle inventory adjustment if purchase was delivered
                    if purchase.get('status') == 'delivered':
                        medicines_data = purchase.get('medicines', [])
                        try:
                            update_main_store_inventory(medicines_data, 'subtract')
                        except Exception as inv_e:
                            failed_items.append(f"Purchase ID {purchase_id}: Inventory adjustment failed - {str(inv_e)}")
                            continue

                delete_purchase(purchase_id)
                deleted_count += 1

            except Exception as e:
                failed_items.append(f"Purchase ID {purchase_id}: {str(e)}")

        # Log the bulk delete activity
        log_activity(
            action='bulk_delete',
            entity_type='purchases',
            details={'message': f'Bulk deleted {deleted_count} purchases', 'count': deleted_count}
        )

        # Prepare response message
        if deleted_count == len(ids):
            message = f'Successfully deleted {deleted_count} purchases'
            return jsonify({'success': True, 'message': message}), 200
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(ids)} purchases. Failed: {", ".join(failed_items)}'
            return jsonify({'success': True, 'message': message, 'warnings': failed_items}), 200
        else:
            message = f'Failed to delete any purchases. Errors: {", ".join(failed_items)}'
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk delete: {str(e)}'}), 500

@purchases_bp.route('/print/<purchase_id>')
@admin_required
def print_purchase(purchase_id):
    """Print purchase details"""
    purchases = get_purchases()
    purchase = next((p for p in purchases if p['id'] == purchase_id), None)

    if not purchase:
        flash('Purchase not found!', 'error')
        return redirect(url_for('purchases.index'))

    suppliers = get_suppliers()
    medicines = get_medicines()
    current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return render_template('purchases/print.html', purchase=purchase, suppliers=suppliers, medicines=medicines, current_datetime=current_datetime)
