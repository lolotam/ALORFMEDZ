"""
Consumption Management Blueprint (Stock Out)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify, session
from app.utils.decorators import login_required, admin_required
from app.utils.database import get_consumption, save_consumption, update_consumption, delete_consumption, log_activity, get_patients, get_departments, get_medicines, get_stores, load_data

consumption_bp = Blueprint('consumption', __name__)

@consumption_bp.route('/')
@login_required
def index():
    """Consumption list page"""
    consumption = get_consumption()
    patients = get_patients()
    departments = get_departments()
    medicines = get_medicines()

    # Filter by department if not admin
    if session.get('role') != 'admin':
        user_department_id = session.get('department_id')
        consumption = [c for c in consumption if c.get('department_id') == user_department_id]

    # Calculate total quantity for each consumption record
    for consumption_record in consumption:
        total_qty = 0
        for medicine_item in consumption_record.get('medicines', []):
            total_qty += medicine_item.get('quantity', 0)
        consumption_record['total_quantity'] = total_qty

    return render_template('consumption/index.html',
                         consumption=consumption,
                         patients=patients,
                         departments=departments,
                         medicines=medicines)

@consumption_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new consumption (Point-of-Sale style)"""
    if request.method == 'POST':
        # Handle multiple medicines in consumption
        medicines_data = []
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')
        
        for i, medicine_id in enumerate(medicine_ids):
            if medicine_id and i < len(quantities):
                medicines_data.append({
                    'medicine_id': medicine_id,
                    'quantity': int(quantities[i])
                })
        
        consumption_data = {
            'date': request.form.get('date'),
            'patient_id': request.form.get('patient_id'),
            'medicines': medicines_data,
            'prescribed_by': request.form.get('prescribed_by', ''),
            'notes': request.form.get('notes', ''),
            'department_id': request.form.get('department_id') or session.get('department_id', '01')
        }
        
        consumption_id = save_consumption(consumption_data)
        flash(f'Consumption recorded successfully with ID: {consumption_id}', 'success')
        return redirect(url_for('consumption.index'))

    patients = get_patients()
    medicines = get_medicines()
    stores = get_stores()
    departments = get_departments()
    doctors = load_data('doctors')
    # Filter to only show active doctors
    doctors = [doctor for doctor in doctors if doctor.get('is_active', True)]

    # Filter stores by department if not admin
    if session.get('role') != 'admin':
        user_department_id = session.get('department_id')
        stores = [s for s in stores if s.get('department_id') == user_department_id]
        departments = [d for d in departments if d.get('id') == user_department_id]

    return render_template('consumption/add.html', patients=patients, medicines=medicines, stores=stores, departments=departments, doctors=doctors)

@consumption_bp.route('/edit/<consumption_id>', methods=['GET', 'POST'])
@login_required
def edit(consumption_id):
    """Edit consumption"""
    from app.utils.database import get_consumption, save_consumption, update_consumption, delete_consumption, log_activity

    consumption_records = get_consumption()
    consumption = next((c for c in consumption_records if c['id'] == consumption_id), None)

    if not consumption:
        flash('Consumption record not found!', 'error')
        return redirect(url_for('consumption.index'))

    if request.method == 'POST':
        # Handle multiple medicines in consumption
        medicines_data = []
        medicine_ids = request.form.getlist('medicine_id[]')
        quantities = request.form.getlist('quantity[]')

        for i, medicine_id in enumerate(medicine_ids):
            if medicine_id and i < len(quantities):
                medicines_data.append({
                    'medicine_id': medicine_id,
                    'quantity': int(quantities[i])
                })

        consumption_data = {
            'patient_id': request.form.get('patient_id'),
            'date': request.form.get('date'),
            'medicines': medicines_data,
            'prescribed_by': request.form.get('prescribed_by'),
            'notes': request.form.get('notes', ''),
            'department_id': request.form.get('department_id') or session.get('department_id', '01')
        }

        update_consumption(consumption_id, consumption_data)
        flash('Consumption updated successfully!', 'success')
        return redirect(url_for('consumption.index'))

    patients = get_patients()
    medicines = get_medicines()
    stores = get_stores()
    departments = get_departments()
    doctors = load_data('doctors')
    # Filter to only show active doctors
    doctors = [doctor for doctor in doctors if doctor.get('is_active', True)]

    # Filter stores by department if not admin
    if session.get('role') != 'admin':
        user_department_id = session.get('department_id')
        stores = [s for s in stores if s.get('department_id') == user_department_id]
        departments = [d for d in departments if d.get('id') == user_department_id]

    return render_template('consumption/edit.html',
                         consumption=consumption,
                         patients=patients,
                         medicines=medicines,
                         stores=stores,
                         departments=departments,
                         doctors=doctors)

@consumption_bp.route('/delete/<consumption_id>')
@login_required
def delete(consumption_id):
    """Delete consumption"""
    consumption_records = get_consumption()
    consumption = next((c for c in consumption_records if c['id'] == consumption_id), None)

    if not consumption:
        flash('Consumption record not found!', 'error')
        return redirect(url_for('consumption.index'))

    delete_consumption(consumption_id)
    flash('Consumption record deleted successfully!', 'success')
    return redirect(url_for('consumption.index'))

@consumption_bp.route('/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete():
    """Bulk delete consumption records"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'No items selected for deletion'}), 400

        # Delete each item
        deleted_count = 0
        failed_items = []

        for consumption_id in ids:
            try:
                delete_consumption(consumption_id)
                deleted_count += 1
            except Exception as e:
                failed_items.append(f"Consumption ID {consumption_id}: {str(e)}")

        # Log the bulk delete activity
        log_activity(
            action='bulk_delete',
            entity_type='consumption',
            details={'message': f'Bulk deleted {deleted_count} consumption records', 'count': deleted_count}
        )

        # Prepare response message
        if deleted_count == len(ids):
            message = f'Successfully deleted {deleted_count} consumption records'
            return jsonify({'success': True, 'message': message}), 200
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(ids)} consumption records. Failed: {", ".join(failed_items)}'
            return jsonify({'success': True, 'message': message, 'warnings': failed_items}), 200
        else:
            message = f'Failed to delete any consumption records. Errors: {", ".join(failed_items)}'
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk delete: {str(e)}'}), 500
