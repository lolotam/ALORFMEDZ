"""
Inventory Transfer Management Blueprint
Handles inventory transfers between stores
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.utils.database import (get_transfers, save_transfer, process_inventory_transfer, 
                           get_stores, get_medicines, log_activity)
from app.utils.decorators import login_required, admin_required

transfers_bp = Blueprint('transfers', __name__)

@transfers_bp.route('/')
@login_required
def index():
    """Inventory transfers list"""
    transfers = get_transfers()
    stores = get_stores()
    medicines = get_medicines()
    
    # Enrich transfer data with store and medicine names
    for transfer in transfers:
        # Add store names
        source_store = next((s for s in stores if s['id'] == transfer.get('source_store_id')), None)
        dest_store = next((s for s in stores if s['id'] == transfer.get('destination_store_id')), None)
        transfer['source_store_name'] = source_store['name'] if source_store else 'Unknown'
        transfer['destination_store_name'] = dest_store['name'] if dest_store else 'Unknown'
        
        # Add medicine names to transfer items
        for item in transfer.get('medicines', []):
            medicine = next((m for m in medicines if m['id'] == item.get('medicine_id')), None)
            item['medicine_name'] = medicine['name'] if medicine else 'Unknown'
    
    return render_template('transfers/index.html', transfers=transfers)

@transfers_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create new inventory transfer"""
    if request.method == 'POST':
        # Get form data
        source_store_id = request.form.get('source_store_id', '').strip()
        destination_store_id = request.form.get('destination_store_id', '').strip()
        requested_by = request.form.get('requested_by', '').strip()
        approved_by = request.form.get('approved_by', '').strip()
        notes = request.form.get('notes', '').strip()
        
        # Get medicines data
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')
        
        # Validate required fields
        if not all([source_store_id, destination_store_id, requested_by, approved_by]):
            flash('Source store, destination store, requested by, and approved by fields are required.', 'error')
            return redirect(url_for('transfers.create'))
        
        if source_store_id == destination_store_id:
            flash('Source and destination stores must be different.', 'error')
            return redirect(url_for('transfers.create'))
        
        if not medicine_ids or not quantities:
            flash('At least one medicine must be selected for transfer.', 'error')
            return redirect(url_for('transfers.create'))
        
        # Prepare medicines data
        medicines_data = []
        for i, medicine_id in enumerate(medicine_ids):
            if medicine_id and i < len(quantities):
                try:
                    quantity = int(quantities[i])
                    if quantity > 0:
                        medicines_data.append({
                            'medicine_id': medicine_id,
                            'quantity': quantity
                        })
                except ValueError:
                    flash(f'Invalid quantity for medicine {i+1}.', 'error')
                    return redirect(url_for('transfers.create'))
        
        if not medicines_data:
            flash('At least one valid medicine with quantity must be specified.', 'error')
            return redirect(url_for('transfers.create'))
        
        # Process the transfer
        success, message = process_inventory_transfer(source_store_id, destination_store_id, medicines_data)
        
        if success:
            # Save transfer record
            transfer_data = {
                'source_store_id': source_store_id,
                'destination_store_id': destination_store_id,
                'medicines': medicines_data,
                'notes': notes,
                'status': 'completed',
                'requested_by': requested_by,
                'approved_by': approved_by
            }
            
            transfer_id = save_transfer(transfer_data)
            
            # Log activity
            log_activity('CREATE', 'transfer', transfer_id, {
                'source_store_id': source_store_id,
                'destination_store_id': destination_store_id,
                'medicines_count': len(medicines_data),
                'requested_by': requested_by,
                'approved_by': approved_by
            })
            
            flash(f'Transfer completed successfully! Transfer ID: {transfer_id}', 'success')
            return redirect(url_for('transfers.index'))
        else:
            flash(f'Transfer failed: {message}', 'error')
            return redirect(url_for('transfers.create'))
    
    # GET request - show form
    stores = get_stores()
    medicines = get_medicines()
    return render_template('transfers/create.html', stores=stores, medicines=medicines)

@transfers_bp.route('/view/<transfer_id>')
@login_required
def view(transfer_id):
    """View transfer details"""
    transfers = get_transfers()
    transfer = next((t for t in transfers if t['id'] == transfer_id), None)
    
    if not transfer:
        flash('Transfer not found.', 'error')
        return redirect(url_for('transfers.index'))
    
    # Enrich with additional data
    stores = get_stores()
    medicines = get_medicines()
    
    source_store = next((s for s in stores if s['id'] == transfer.get('source_store_id')), None)
    dest_store = next((s for s in stores if s['id'] == transfer.get('destination_store_id')), None)
    
    transfer['source_store_name'] = source_store['name'] if source_store else 'Unknown'
    transfer['destination_store_name'] = dest_store['name'] if dest_store else 'Unknown'
    
    # Add medicine names
    for item in transfer.get('medicines', []):
        medicine = next((m for m in medicines if m['id'] == item.get('medicine_id')), None)
        item['medicine_name'] = medicine['name'] if medicine else 'Unknown'
    
    # Log view activity
    log_activity('VIEW', 'transfer', transfer_id)
    
    return render_template('transfers/view.html', transfer=transfer)

@transfers_bp.route('/api/store-inventory/<store_id>')
@login_required
def get_store_inventory(store_id):
    """API endpoint to get store inventory for AJAX calls"""
    stores = get_stores()
    medicines = get_medicines()
    
    store = next((s for s in stores if s['id'] == store_id), None)
    if not store:
        return jsonify({'error': 'Store not found'}), 404
    
    inventory = store.get('inventory', {})
    result = []
    
    for medicine in medicines:
        stock = inventory.get(medicine['id'], 0)
        if stock > 0:  # Only return medicines with stock
            result.append({
                'id': medicine['id'],
                'name': medicine['name'],
                'stock': stock,
                'form_dosage': medicine.get('form_dosage', '')
            })
    
    return jsonify(result)
