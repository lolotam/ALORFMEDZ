"""
Medicines Management Blueprint
CRUD operations for medicines
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, session
import csv
import io
import re
from datetime import datetime, timedelta
from utils.helpers import login_required, admin_required
from utils.database import get_medicines, save_medicine, update_medicine, delete_medicine, get_suppliers, get_stores, log_activity, migrate_medicine_fields


def convert_date_format(date_str):
    """Convert date from dd-mm-yyyy or dd/mm/yyyy to yyyy-mm-dd format"""
    if not date_str or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    # If already in yyyy-mm-dd format, return as is
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        return date_str
    
    # Convert dd-mm-yyyy or dd/mm/yyyy to yyyy-mm-dd
    if re.match(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}', date_str):
        parts = re.split(r'[-/]', date_str)
        if len(parts) == 3:
            day, month, year = parts
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    
    return date_str

def format_date_display(date_str):
    """Convert date from yyyy-mm-dd to dd-mm-yyyy for display"""
    if not date_str:
        return ""
    
    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
        year, month, day = date_str.split('-')
        return f"{day}-{month}-{year}"
    
    return date_str

medicines_bp = Blueprint('medicines', __name__)


# Register template filter
@medicines_bp.app_template_filter('format_date_display')
def format_date_display_filter(date_str):
    return format_date_display(date_str)

@medicines_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Medicines list page"""
    # Ensure medicine data consistency
    migrate_medicine_fields()

    if request.method == 'POST':
        # Handle CSV import
        if 'csv_file' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('medicines.index'))

        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('medicines.index'))

        if not file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file!', 'error')
            return redirect(url_for('medicines.index'))

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

                # Handle supplier mapping (accept both supplier_id and supplier_name)
                supplier_id = row.get('supplier_id', '').strip()
                supplier_name = row.get('supplier_name', '').strip()

                # If supplier_id is provided, use it directly
                if supplier_id:
                    final_supplier_id = supplier_id
                # If supplier_name is provided, map it to supplier_id
                elif supplier_name:
                    suppliers_list = get_suppliers()
                    supplier_match = next((s for s in suppliers_list if s['name'].lower() == supplier_name.lower()), None)
                    if supplier_match:
                        final_supplier_id = supplier_match['id']
                    else:
                        errors.append(f'Row {row_num}: Supplier "{supplier_name}" not found')
                        continue
                # Default to first supplier if neither is provided
                else:
                    final_supplier_id = '01'

                # Validate and convert expiry date if provided
                expiry_date = row.get('expiry_date', '').strip()
                if expiry_date:
                    converted_date = convert_date_format(expiry_date)
                    if converted_date:
                        try:
                            datetime.strptime(converted_date, '%Y-%m-%d')
                            expiry_date = converted_date
                        except ValueError:
                            errors.append(f'Row {row_num}: Invalid expiry date format. Use DD-MM-YYYY or YYYY-MM-DD')
                            continue
                    else:
                        errors.append(f'Row {row_num}: Invalid expiry date format. Use DD-MM-YYYY or YYYY-MM-DD')
                        continue

                # Create medicine data
                medicine_data = {
                    'name': row.get('name', '').strip(),
                    'supplier_id': final_supplier_id,
                    'form_dosage': row.get('form_dosage', '').strip(),
                    'low_stock_limit': int(row.get('low_stock_limit', 10)),
                    'notes': row.get('notes', '').strip(),
                    'expiry_date': expiry_date if expiry_date else None,
                    'batch_number': row.get('batch_number', '').strip() or None,
                    'barcode_number': row.get('barcode_number', '').strip() or None
                }

                # Save medicine
                save_medicine(medicine_data)
                imported_count += 1

            if errors:
                flash(f'Import completed with {imported_count} medicines imported. Errors: {"; ".join(errors)}', 'warning')
            else:
                flash(f'Successfully imported {imported_count} medicines!', 'success')

        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'error')

        return redirect(url_for('medicines.index'))

    medicines = get_medicines()
    suppliers = get_suppliers()
    stores = get_stores()

    # Calculate current stock for each medicine based on user role
    for medicine in medicines:
        current_stock = 0

        # Admin users see Main Pharmacy stock only (department_id = "01")
        # Department users see their assigned store stock only
        if session.get('role') == 'admin':
            # Admin sees Main Pharmacy stock only
            main_pharmacy_store = next((s for s in stores if s.get('department_id') == '01'), None)
            if main_pharmacy_store:
                inventory = main_pharmacy_store.get('inventory', {})
                current_stock = inventory.get(medicine['id'], 0)
        else:
            # Department users see their assigned store stock only
            user_department_id = session.get('department_id')
            if user_department_id:
                user_store = next((s for s in stores if s.get('department_id') == user_department_id), None)
                if user_store:
                    inventory = user_store.get('inventory', {})
                    current_stock = inventory.get(medicine['id'], 0)

        medicine['current_stock'] = current_stock

        # Calculate stock status based on department-specific stock
        if current_stock <= medicine.get('low_stock_limit', 0):
            medicine['stock_status'] = 'low'
        elif current_stock <= medicine.get('low_stock_limit', 0) * 1.5:
            medicine['stock_status'] = 'medium'
        else:
            medicine['stock_status'] = 'good'

    # Calculate dates for expiry status checking
    current_date = datetime.now().strftime('%Y-%m-%d')
    warning_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')

    return render_template('medicines/index.html',
                         medicines=medicines,
                         suppliers=suppliers,
                         stores=stores,
                         current_date=current_date,
                         warning_date=warning_date)

@medicines_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new medicine"""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name', '').strip()
        supplier_id = request.form.get('supplier_id', '').strip()
        low_stock_limit = request.form.get('low_stock_limit', '0')
        form_dosage = request.form.get('form_dosage', '').strip()
        notes = request.form.get('notes', '').strip()
        expiry_date = request.form.get('expiry_date', '').strip()
        batch_number = request.form.get('batch_number', '').strip()
        barcode_number = request.form.get('barcode_number', '').strip()

        # Validate required fields
        if not all([name, supplier_id]):
            flash('Name and supplier are required fields.', 'error')
            suppliers = get_suppliers()
            return render_template('medicines/add.html', suppliers=suppliers)

        # Validate data types and ranges
        try:
            low_stock_limit = int(low_stock_limit)
            if low_stock_limit < 0:
                flash('Low stock limit must be a positive number.', 'error')
                suppliers = get_suppliers()
                return render_template('medicines/add.html', suppliers=suppliers)
        except ValueError:
            flash('Low stock limit must be a valid number.', 'error')
            suppliers = get_suppliers()
            return render_template('medicines/add.html', suppliers=suppliers)

        # Validate supplier exists
        suppliers_list = get_suppliers()
        if not any(s['id'] == supplier_id for s in suppliers_list):
            flash('Selected supplier does not exist.', 'error')
            return render_template('medicines/add.html', suppliers=suppliers_list)

        # Validate expiry date format if provided
        if expiry_date:
            try:
                datetime.strptime(expiry_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid expiry date format. Please use YYYY-MM-DD format.', 'error')
                suppliers = get_suppliers()
                return render_template('medicines/add.html', suppliers=suppliers)

        medicine_data = {
            'name': name,
            'supplier_id': supplier_id,
            'low_stock_limit': low_stock_limit,
            'form_dosage': form_dosage,
            'notes': notes,
            'expiry_date': expiry_date if expiry_date else None,
            'batch_number': batch_number if batch_number else None,
            'barcode_number': barcode_number if barcode_number else None
        }
        
        medicine_id = save_medicine(medicine_data)

        # Log activity
        log_activity('CREATE', 'medicine', medicine_id, {
            'name': medicine_data['name'],
            'supplier_id': medicine_data['supplier_id']
        })

        flash(f'Medicine added successfully with ID: {medicine_id}', 'success')
        return redirect(url_for('medicines.index'))
    
    suppliers = get_suppliers()
    return render_template('medicines/add.html', suppliers=suppliers)

@medicines_bp.route('/edit/<medicine_id>', methods=['GET', 'POST'])
@login_required
def edit(medicine_id):
    """Edit medicine"""
    medicines = get_medicines()
    medicine = next((m for m in medicines if m['id'] == medicine_id), None)
    
    if not medicine:
        flash('Medicine not found!', 'error')
        return redirect(url_for('medicines.index'))
    
    if request.method == 'POST':
        # Get form data including new fields
        expiry_date = request.form.get('expiry_date', '').strip()

        # Validate expiry date format if provided
        if expiry_date:
            try:
                datetime.strptime(expiry_date, '%Y-%m-%d')
            except ValueError:
                flash('Invalid expiry date format. Please use YYYY-MM-DD format.', 'error')
                suppliers = get_suppliers()
                return render_template('medicines/edit.html', medicine=medicine, suppliers=suppliers)

        medicine_data = {
            'name': request.form.get('name'),
            'supplier_id': request.form.get('supplier_id'),
            'low_stock_limit': int(request.form.get('low_stock_limit', 0)),
            'form_dosage': request.form.get('form_dosage'),
            'notes': request.form.get('notes', ''),
            'expiry_date': expiry_date if expiry_date else None,
            'batch_number': request.form.get('batch_number', '').strip() or None,
            'barcode_number': request.form.get('barcode_number', '').strip() or None
        }

        update_medicine(medicine_id, medicine_data)
        flash('Medicine updated successfully!', 'success')
        return redirect(url_for('medicines.index'))
    
    suppliers = get_suppliers()
    return render_template('medicines/edit.html', medicine=medicine, suppliers=suppliers)

@medicines_bp.route('/delete/<medicine_id>')
@login_required
def delete(medicine_id):
    """Delete medicine"""
    delete_medicine(medicine_id)
    flash('Medicine deleted successfully!', 'success')
    return redirect(url_for('medicines.index'))

@medicines_bp.route('/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete():
    """Bulk delete medicines"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'No items selected for deletion'}), 400

        # Delete each medicine
        deleted_count = 0
        failed_items = []

        for medicine_id in ids:
            try:
                # Check if medicine exists in any stores
                stores = get_stores()
                has_stock = any(
                    store.get('medicine_id') == medicine_id and store.get('quantity', 0) > 0
                    for store in stores
                )

                if has_stock:
                    failed_items.append(f"Medicine ID {medicine_id} has stock in stores")
                    continue

                delete_medicine(medicine_id)
                deleted_count += 1

            except Exception as e:
                failed_items.append(f"Medicine ID {medicine_id}: {str(e)}")

        # Log the bulk delete activity
        log_activity(
            user_id=session.get('user_id'),
            action='bulk_delete',
            details=f'Bulk deleted {deleted_count} medicines'
        )

        # Prepare response message
        if deleted_count == len(ids):
            message = f'Successfully deleted {deleted_count} medicines'
            return jsonify({'success': True, 'message': message}), 200
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(ids)} medicines. Failed: {", ".join(failed_items)}'
            return jsonify({'success': True, 'message': message, 'warnings': failed_items}), 200
        else:
            message = f'Failed to delete any medicines. Errors: {", ".join(failed_items)}'
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk delete: {str(e)}'}), 500

@medicines_bp.route('/template/download')
@login_required
def download_template():
    """Download CSV template for medicines import"""
    template_headers = [
        'name',
        'supplier_id',
        'supplier_name',
        'form_dosage',
        'low_stock_limit',
        'notes',
        'expiry_date',
        'batch_number',
        'barcode_number'
    ]

    csv_content = ','.join(template_headers) + '\n'
    csv_content += '# You can use either supplier_id OR supplier_name (not both)\n'
    csv_content += '# Expiry date format: DD-MM-YYYY (optional)\n'
    csv_content += '# Example with supplier_id: Paracetamol,01,,Tablet 500mg,50,Pain relief medication,31-12-2025,BATCH001,1234567890123\n'
    csv_content += '# Example with supplier_name: Ibuprofen,,PharmaCorp International,Syrup 200ml,30,Anti-inflammatory,15-06-2026,BATCH002,9876543210987\n'

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=medicines_template.csv'}
    )

@medicines_bp.route('/api/<medicine_id>')
@login_required
def get_medicine_api(medicine_id):
    """Get medicine details for API consumption"""
    try:
        medicines = get_medicines()
        suppliers = get_suppliers()
        stores = get_stores()

        # Find the medicine
        medicine = next((m for m in medicines if m['id'] == medicine_id), None)
        if not medicine:
            return jsonify({'error': 'Medicine not found'}), 404

        # Get supplier name
        supplier = next((s for s in suppliers if s['id'] == medicine.get('supplier_id')), None)

        # Calculate current stock
        current_stock = 0
        stock_status = 'good'
        for store in stores:
            inventory = store.get('inventory', {})
            current_stock += inventory.get(medicine_id, 0)

        # Determine stock status
        low_stock_limit = int(medicine.get('low_stock_limit', 0))
        if current_stock <= low_stock_limit:
            stock_status = 'low'
        elif current_stock <= low_stock_limit * 2:
            stock_status = 'medium'
        else:
            stock_status = 'good'

        # Prepare response data
        response_data = {
            'id': medicine['id'],
            'name': medicine['name'],
            'supplier_id': medicine.get('supplier_id'),
            'supplier_name': supplier['name'] if supplier else 'N/A',
            'form_dosage': medicine.get('form_dosage'),
            'low_stock_limit': medicine.get('low_stock_limit'),
            'notes': medicine.get('notes') or medicine.get('description'),
            'expiry_date': medicine.get('expiry_date'),
            'batch_number': medicine.get('batch_number'),
            'barcode_number': medicine.get('barcode_number'),
            'current_stock': current_stock,
            'stock_status': stock_status
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({'error': f'Error fetching medicine: {str(e)}'}), 500
