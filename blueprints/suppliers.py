"""
Suppliers Management Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify, session
import csv
import io
from utils.helpers import login_required, admin_required
from utils.database import get_suppliers, save_supplier, update_supplier, delete_supplier, get_medicines, log_activity

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Suppliers list page"""
    if request.method == 'POST':
        # Handle CSV import
        if 'csv_file' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('suppliers.index'))

        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('suppliers.index'))

        if not file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file!', 'error')
            return redirect(url_for('suppliers.index'))

        try:
            # Read CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.DictReader(stream)

            imported_count = 0
            errors = []

            for row_num, row in enumerate(csv_input, start=2):
                # Skip comment lines
                if any(value.startswith('#') for value in row.values()):
                    continue

                # Validate required fields
                if not row.get('name', '').strip():
                    errors.append(f"Row {row_num}: Name is required")
                    continue

                # Create supplier data
                supplier_data = {
                    'name': row.get('name', '').strip(),
                    'type': row.get('type', 'Medicine').strip(),
                    'contact_person': row.get('contact_person', '').strip(),
                    'phone': row.get('phone', '').strip(),
                    'email': row.get('email', '').strip(),
                    'address': row.get('address', '').strip(),
                    'notes': row.get('notes', '').strip()
                }

                # Save supplier
                save_supplier(supplier_data)
                imported_count += 1

            if errors:
                flash(f'Import completed with {imported_count} suppliers imported. Errors: {"; ".join(errors)}', 'warning')
            else:
                flash(f'Successfully imported {imported_count} suppliers!', 'success')

        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'error')

        return redirect(url_for('suppliers.index'))

    suppliers = get_suppliers()
    return render_template('suppliers/index.html', suppliers=suppliers)

@suppliers_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new supplier"""
    if request.method == 'POST':
        supplier_data = {
            'name': request.form.get('name'),
            'type': request.form.get('type'),
            'contact_person': request.form.get('contact_person'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'notes': request.form.get('notes', '')
        }

        supplier_id = save_supplier(supplier_data)
        flash(f'Supplier added successfully with ID: {supplier_id}', 'success')
        return redirect(url_for('suppliers.index'))

    return render_template('suppliers/add.html')

@suppliers_bp.route('/edit/<supplier_id>', methods=['GET', 'POST'])
@login_required
def edit(supplier_id):
    """Edit supplier"""
    suppliers = get_suppliers()
    supplier = next((s for s in suppliers if s['id'] == supplier_id), None)
    
    if not supplier:
        flash('Supplier not found!', 'error')
        return redirect(url_for('suppliers.index'))
    
    if request.method == 'POST':
        supplier_data = {
            'name': request.form.get('name'),
            'type': request.form.get('type'),
            'contact_person': request.form.get('contact_person'),
            'phone': request.form.get('phone'),
            'email': request.form.get('email'),
            'address': request.form.get('address'),
            'notes': request.form.get('notes', '')
        }

        update_supplier(supplier_id, supplier_data)
        flash('Supplier updated successfully!', 'success')
        return redirect(url_for('suppliers.index'))
    
    return render_template('suppliers/edit.html', supplier=supplier)

@suppliers_bp.route('/delete/<supplier_id>')
@login_required
def delete(supplier_id):
    """Delete supplier"""
    delete_supplier(supplier_id)
    flash('Supplier deleted successfully!', 'success')
    return redirect(url_for('suppliers.index'))

@suppliers_bp.route('/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete():
    """Bulk delete suppliers"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'No items selected for deletion'}), 400

        # Delete each item
        deleted_count = 0
        failed_items = []

        for supplier_id in ids:
            try:
                # Check if supplier has medicines
                medicines = get_medicines()
                has_medicines = any(
                    medicine.get('supplier_id') == supplier_id
                    for medicine in medicines
                )

                if has_medicines:
                    failed_items.append(f"Supplier ID {supplier_id} has associated medicines")
                    continue

                delete_supplier(supplier_id)
                deleted_count += 1

            except Exception as e:
                failed_items.append(f"Supplier ID {supplier_id}: {str(e)}")

        # Log the bulk delete activity
        log_activity(
            user_id=session.get('user_id'),
            action='bulk_delete',
            details=f'Bulk deleted {deleted_count} suppliers'
        )

        # Prepare response message
        if deleted_count == len(ids):
            message = f'Successfully deleted {deleted_count} suppliers'
            return jsonify({'success': True, 'message': message}), 200
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(ids)} suppliers. Failed: {", ".join(failed_items)}'
            return jsonify({'success': True, 'message': message, 'warnings': failed_items}), 200
        else:
            message = f'Failed to delete any suppliers. Errors: {", ".join(failed_items)}'
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk delete: {str(e)}'}), 500

@suppliers_bp.route('/template/download')
@login_required
def download_template():
    """Download CSV template for suppliers import"""
    template_headers = [
        'name',
        'type',
        'contact_person',
        'phone',
        'email',
        'address',
        'notes'
    ]

    csv_content = ','.join(template_headers) + '\n'
    csv_content += '# Example: ABC Pharmaceuticals,Medicine,John Smith,123-456-7890,john@abc.com,123 Business St,Reliable supplier\n'

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=suppliers_template.csv'}
    )
