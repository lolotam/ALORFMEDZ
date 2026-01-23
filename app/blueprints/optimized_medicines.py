"""
Optimized Medicines Management Blueprint
Performance-enhanced CRUD operations with caching, pagination, and monitoring
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, session
import csv
import io
import re
from datetime import datetime, timedelta
from app.utils.decorators import login_required, admin_required
from app.utils.optimized_database import optimized_db, find_by_id_optimized
from app.utils.pagination_helpers import (
    get_request_pagination_params, create_pagination_response,
    SmartFilter, DataViewOptimizer, create_ajax_pagination_response
)
from app.utils.performance_monitor import performance_tracker, metrics
from app.utils.database import get_suppliers, log_activity

# Create optimized blueprint
medicines_bp = Blueprint('medicines_optimized', __name__)

@medicines_bp.route('/')
@login_required
@performance_tracker('endpoint')
def index():
    """Optimized medicines list page with pagination and filtering"""
    page, per_page = get_request_pagination_params()

    # Get filter parameters
    search_term = request.args.get('search', '').strip()
    supplier_filter = request.args.get('supplier_id', '').strip()
    category_filter = request.args.get('category', '').strip()

    # Check for AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        # Load medicines with caching
        medicines = optimized_db.load_data('medicines', use_cache=True)

        # Apply filters if provided
        if search_term or supplier_filter or category_filter:
            filter_obj = SmartFilter(medicines)
            filters = {}

            if search_term:
                filters['_search'] = search_term
                filters['_search_fields'] = ['name', 'form_dosage', 'notes']

            if supplier_filter:
                filters['supplier_id'] = supplier_filter

            if category_filter:
                filters['category'] = category_filter

            medicines = filter_obj.apply_filters(filters)

        # Optimize data for table view (only include visible fields)
        table_fields = ['id', 'name', 'form_dosage', 'supplier_id', 'low_stock_limit', 'notes']
        medicines = DataViewOptimizer.optimize_for_table_view(medicines, table_fields)

        # Create paginated response
        if is_ajax:
            response_data = create_ajax_pagination_response(medicines, page, per_page)
            return jsonify(response_data)
        else:
            paginated_data = create_pagination_response(
                medicines, page, per_page, 'medicines_optimized.index',
                search=search_term, supplier_id=supplier_filter, category=category_filter
            )

            # Load suppliers for filter dropdown (with caching)
            suppliers = optimized_db.load_data('suppliers', use_cache=True)
            supplier_options = DataViewOptimizer.prepare_select_options(
                suppliers, 'id', 'name'
            )

            return render_template(
                'medicines/optimized_index.html',
                medicines=paginated_data['data'],
                pagination=paginated_data['pagination'],
                suppliers=supplier_options,
                search_term=search_term,
                supplier_filter=supplier_filter,
                category_filter=category_filter
            )

    except Exception as e:
        metrics.record_error('MedicinesIndexError', str(e), 'medicines.index')
        flash('Error loading medicines data. Please try again.', 'error')

        if is_ajax:
            return jsonify({'success': False, 'error': str(e)}), 500
        else:
            return render_template('medicines/optimized_index.html', medicines=[], pagination=None)

@medicines_bp.route('/api/search')
@login_required
@performance_tracker('api')
def api_search():
    """High-performance medicine search API"""
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 10)), 50)  # Cap at 50 results

    if len(query) < 2:
        return jsonify({'results': []})

    try:
        # Use cached data for search
        medicines = optimized_db.load_data('medicines', use_cache=True)

        # Fast text search
        filter_obj = SmartFilter(medicines)
        results = filter_obj.filter_by_text_search(query, ['name', 'form_dosage'])

        # Limit results and optimize for API response
        limited_results = results[:limit]
        api_fields = ['id', 'name', 'form_dosage', 'supplier_id']
        optimized_results = DataViewOptimizer.optimize_for_table_view(
            limited_results, api_fields
        )

        return jsonify({
            'results': optimized_results,
            'total': len(results),
            'limited': len(results) > limit,
            'query': query
        })

    except Exception as e:
        metrics.record_error('MedicineSearchError', str(e), 'medicines.api_search')
        return jsonify({'error': 'Search failed'}), 500

@medicines_bp.route('/add', methods=['GET', 'POST'])
@admin_required
@performance_tracker('endpoint')
def add():
    """Optimized add medicine with validation"""
    if request.method == 'POST':
        try:
            # Extract and validate form data
            medicine_data = {
                'name': request.form.get('name', '').strip(),
                'form_dosage': request.form.get('form_dosage', '').strip(),
                'supplier_id': request.form.get('supplier_id', '').strip(),
                'low_stock_limit': int(request.form.get('low_stock_limit', 0)),
                'notes': request.form.get('notes', '').strip(),
                'created_at': datetime.now().isoformat()
            }

            # Validation
            if not medicine_data['name']:
                raise ValueError("Medicine name is required")

            if not medicine_data['supplier_id']:
                raise ValueError("Supplier selection is required")

            # Verify supplier exists (with caching)
            supplier = find_by_id_optimized('suppliers', medicine_data['supplier_id'])
            if not supplier:
                raise ValueError("Selected supplier does not exist")

            # Save medicine
            medicines = optimized_db.load_data('medicines')
            medicine_id = optimized_db.generate_id('medicines')
            medicine_data['id'] = medicine_id

            medicines.append(medicine_data)
            success = optimized_db.save_data('medicines', medicines)

            if success:
                # Log activity
                log_activity('CREATE', 'medicine', medicine_id, {
                    'name': medicine_data['name'],
                    'supplier_id': medicine_data['supplier_id']
                })

                flash(f'Medicine "{medicine_data["name"]}" added successfully!', 'success')
                return redirect(url_for('medicines_optimized.index'))
            else:
                raise Exception("Failed to save medicine data")

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            metrics.record_error('MedicineAddError', str(e), 'medicines.add')
            flash('Error adding medicine. Please try again.', 'error')

    # Load suppliers for form
    suppliers = optimized_db.load_data('suppliers', use_cache=True)
    return render_template('medicines/optimized_add.html', suppliers=suppliers)

@medicines_bp.route('/edit/<medicine_id>', methods=['GET', 'POST'])
@admin_required
@performance_tracker('endpoint')
def edit(medicine_id):
    """Optimized edit medicine"""
    # Fast medicine lookup using indexing
    medicine = find_by_id_optimized('medicines', medicine_id)

    if not medicine:
        flash('Medicine not found!', 'error')
        return redirect(url_for('medicines_optimized.index'))

    if request.method == 'POST':
        try:
            # Update medicine data
            updated_data = {
                'name': request.form.get('name', '').strip(),
                'form_dosage': request.form.get('form_dosage', '').strip(),
                'supplier_id': request.form.get('supplier_id', '').strip(),
                'low_stock_limit': int(request.form.get('low_stock_limit', 0)),
                'notes': request.form.get('notes', '').strip(),
                'updated_at': datetime.now().isoformat()
            }

            # Validation
            if not updated_data['name']:
                raise ValueError("Medicine name is required")

            if not updated_data['supplier_id']:
                raise ValueError("Supplier selection is required")

            # Verify supplier exists
            supplier = find_by_id_optimized('suppliers', updated_data['supplier_id'])
            if not supplier:
                raise ValueError("Selected supplier does not exist")

            # Update using bulk update for efficiency
            updated_data['id'] = medicine_id
            success = optimized_db.bulk_update('medicines', [updated_data])

            if success:
                # Log activity
                log_activity('UPDATE', 'medicine', medicine_id, {
                    'name': updated_data['name'],
                    'supplier_id': updated_data['supplier_id']
                })

                flash(f'Medicine "{updated_data["name"]}" updated successfully!', 'success')
                return redirect(url_for('medicines_optimized.index'))
            else:
                raise Exception("Failed to update medicine data")

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            metrics.record_error('MedicineEditError', str(e), 'medicines.edit')
            flash('Error updating medicine. Please try again.', 'error')

    # Load suppliers for form
    suppliers = optimized_db.load_data('suppliers', use_cache=True)
    return render_template('medicines/optimized_edit.html', medicine=medicine, suppliers=suppliers)

@medicines_bp.route('/delete/<medicine_id>', methods=['POST'])
@admin_required
@performance_tracker('endpoint')
def delete(medicine_id):
    """Optimized delete medicine"""
    try:
        # Get medicine info before deletion
        medicine = find_by_id_optimized('medicines', medicine_id)
        if not medicine:
            flash('Medicine not found!', 'error')
            return redirect(url_for('medicines_optimized.index'))

        # Use bulk delete for efficiency
        success = optimized_db.bulk_delete('medicines', [medicine_id])

        if success:
            # Log activity
            log_activity('DELETE', 'medicine', medicine_id, {
                'name': medicine.get('name', 'Unknown')
            })

            flash(f'Medicine "{medicine.get("name", "Unknown")}" deleted successfully!', 'success')
        else:
            raise Exception("Failed to delete medicine")

    except Exception as e:
        metrics.record_error('MedicineDeleteError', str(e), 'medicines.delete')
        flash('Error deleting medicine. Please try again.', 'error')

    return redirect(url_for('medicines_optimized.index'))

@medicines_bp.route('/bulk-delete', methods=['POST'])
@admin_required
@performance_tracker('endpoint')
def bulk_delete():
    """Optimized bulk delete medicines"""
    try:
        data = request.get_json()
        medicine_ids = data.get('ids', [])

        if not medicine_ids:
            return jsonify({'error': 'No medicines selected'}), 400

        # Get medicine names for logging
        medicine_names = []
        for medicine_id in medicine_ids:
            medicine = find_by_id_optimized('medicines', medicine_id)
            if medicine:
                medicine_names.append(medicine.get('name', 'Unknown'))

        # Bulk delete operation
        success = optimized_db.bulk_delete('medicines', medicine_ids)

        if success:
            # Log bulk activity
            log_activity('BULK_DELETE', 'medicines', None, {
                'count': len(medicine_ids),
                'medicine_names': medicine_names
            })

            return jsonify({
                'success': True,
                'message': f'Successfully deleted {len(medicine_ids)} medicines',
                'deleted_count': len(medicine_ids)
            })
        else:
            raise Exception("Bulk delete operation failed")

    except Exception as e:
        metrics.record_error('MedicineBulkDeleteError', str(e), 'medicines.bulk_delete')
        return jsonify({'error': 'Bulk delete failed'}), 500

@medicines_bp.route('/export/csv')
@admin_required
@performance_tracker('export')
def export_csv():
    """Optimized CSV export with streaming"""
    try:
        medicines = optimized_db.load_data('medicines', use_cache=True)
        suppliers = optimized_db.load_data('suppliers', use_cache=True)

        # Create supplier lookup for performance
        supplier_lookup = {s['id']: s['name'] for s in suppliers}

        def generate_csv():
            """Generator for streaming CSV response"""
            yield 'ID,Name,Form & Dosage,Supplier,Low Stock Limit,Notes,Created At\n'

            for medicine in medicines:
                supplier_name = supplier_lookup.get(medicine.get('supplier_id', ''), 'Unknown')

                row = [
                    medicine.get('id', ''),
                    medicine.get('name', ''),
                    medicine.get('form_dosage', ''),
                    supplier_name,
                    str(medicine.get('low_stock_limit', 0)),
                    medicine.get('notes', ''),
                    medicine.get('created_at', '')
                ]

                # Escape CSV values
                escaped_row = [f'"{field.replace('"', '""')}"' for field in row]
                yield ','.join(escaped_row) + '\n'

        # Create streaming response
        filename = f"medicines_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return Response(
            generate_csv(),
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        metrics.record_error('MedicineExportError', str(e), 'medicines.export_csv')
        flash('Error exporting medicines data.', 'error')
        return redirect(url_for('medicines_optimized.index'))

@medicines_bp.route('/import/csv', methods=['POST'])
@admin_required
@performance_tracker('import')
def import_csv():
    """Optimized CSV import with batch processing"""
    if 'csv_file' not in request.files:
        flash('No file selected!', 'error')
        return redirect(url_for('medicines_optimized.index'))

    file = request.files['csv_file']
    if file.filename == '' or not file.filename.lower().endswith('.csv'):
        flash('Please upload a valid CSV file!', 'error')
        return redirect(url_for('medicines_optimized.index'))

    try:
        # Read and process CSV in chunks for large files
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)

        medicines = optimized_db.load_data('medicines')
        suppliers = optimized_db.load_data('suppliers', use_cache=True)
        supplier_lookup = {s['name']: s['id'] for s in suppliers}

        imported_count = 0
        errors = []
        batch_size = 100  # Process in batches

        new_medicines = []

        for row_num, row in enumerate(csv_reader, start=2):
            try:
                # Skip empty rows or comments
                if not row.get('name', '').strip() or row.get('name', '').startswith('#'):
                    continue

                # Map supplier name to ID
                supplier_name = row.get('supplier', '').strip()
                supplier_id = supplier_lookup.get(supplier_name)

                if not supplier_id:
                    errors.append(f"Row {row_num}: Supplier '{supplier_name}' not found")
                    continue

                medicine_data = {
                    'id': optimized_db.generate_id('medicines'),
                    'name': row.get('name', '').strip(),
                    'form_dosage': row.get('form_dosage', '').strip(),
                    'supplier_id': supplier_id,
                    'low_stock_limit': int(row.get('low_stock_limit', 0)),
                    'notes': row.get('notes', '').strip(),
                    'created_at': datetime.now().isoformat()
                }

                new_medicines.append(medicine_data)
                imported_count += 1

                # Process in batches
                if len(new_medicines) >= batch_size:
                    medicines.extend(new_medicines)
                    new_medicines = []

            except (ValueError, KeyError) as e:
                errors.append(f"Row {row_num}: {str(e)}")

        # Process remaining medicines
        if new_medicines:
            medicines.extend(new_medicines)

        # Save all at once for efficiency
        if imported_count > 0:
            success = optimized_db.save_data('medicines', medicines)
            if success:
                flash(f'Successfully imported {imported_count} medicines!', 'success')
            else:
                flash('Error saving imported data.', 'error')

        # Report errors
        if errors:
            error_summary = f"{len(errors)} errors occurred during import"
            flash(error_summary, 'warning')

    except Exception as e:
        metrics.record_error('MedicineImportError', str(e), 'medicines.import_csv')
        flash('Error processing CSV file.', 'error')

    return redirect(url_for('medicines_optimized.index'))

@medicines_bp.route('/performance-stats')
@admin_required
def performance_stats():
    """Performance statistics for medicines module"""
    try:
        stats = metrics.get_summary_stats(time_window=3600)  # Last hour
        slow_endpoints = metrics.get_slow_endpoints(threshold=0.5, limit=5)

        return jsonify({
            'success': True,
            'stats': stats,
            'slow_endpoints': slow_endpoints,
            'cache_performance': optimized_db.get_cache_stats()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500