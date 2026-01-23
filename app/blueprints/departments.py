"""
Departments Management Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify, session
import csv
import io
from app.utils.decorators import login_required, admin_required
from app.utils.database import get_departments, save_department, update_department, delete_department, get_users, get_consumption, log_activity, save_department_with_user

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Departments list page"""
    if request.method == 'POST':
        # Handle CSV import (admin only)
        if session.get('role') != 'admin':
            flash('Only administrators can import departments!', 'error')
            return redirect(url_for('departments.index'))

        if 'csv_file' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('departments.index'))

        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('departments.index'))

        if not file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file!', 'error')
            return redirect(url_for('departments.index'))

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

                # Create department data (map CSV fields to department fields)
                department_data = {
                    'name': row.get('name', '').strip(),
                    'responsible_person': row.get('responsible_person', '').strip(),
                    'telephone': row.get('telephone', '').strip(),
                    'notes': row.get('notes', '').strip()
                }

                # Save department with automatic user creation
                result = save_department_with_user(department_data)
                imported_count += 1

            if errors:
                flash(f'Import completed with {imported_count} departments imported. Errors: {"; ".join(errors)}', 'warning')
            else:
                flash(f'Successfully imported {imported_count} departments!', 'success')

        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'error')

        return redirect(url_for('departments.index'))

    departments = get_departments()
    return render_template('departments/index.html', departments=departments)

@departments_bp.route('/add', methods=['GET', 'POST'])
@admin_required
def add():
    """Add new department with automatic user creation"""
    if request.method == 'POST':
        department_data = {
            'name': request.form.get('name'),
            'responsible_person': request.form.get('responsible_person'),
            'telephone': request.form.get('telephone'),
            'notes': request.form.get('notes', '')
        }

        try:
            # Save department with automatic store and user creation
            result = save_department_with_user(department_data)

            department_id = result['department_id']
            user_info = result['user_info']

            # Show success message with user credentials
            flash(f'Department "{department_data["name"]}" added successfully!', 'success')
            flash(f'Department User Created - Username: {user_info["username"]}, Password: {user_info["password"]}', 'info')
            flash('Please save these credentials and share them with the department staff.', 'warning')

        except Exception as e:
            flash(f'Error creating department: {str(e)}', 'error')

        return redirect(url_for('departments.index'))

    return render_template('departments/add.html')

@departments_bp.route('/edit/<department_id>', methods=['GET', 'POST'])
@admin_required
def edit(department_id):
    """Edit department"""
    departments = get_departments()
    department = next((d for d in departments if d['id'] == department_id), None)
    
    if not department:
        flash('Department not found!', 'error')
        return redirect(url_for('departments.index'))
    
    if request.method == 'POST':
        department_data = {
            'name': request.form.get('name'),
            'responsible_person': request.form.get('responsible_person'),
            'telephone': request.form.get('telephone'),
            'notes': request.form.get('notes', '')
        }
        
        update_department(department_id, department_data)
        flash('Department updated successfully!', 'success')
        return redirect(url_for('departments.index'))
    
    return render_template('departments/edit.html', department=department)

@departments_bp.route('/delete/<department_id>')
@admin_required
def delete(department_id):
    """Delete department and associated store"""
    # Prevent deletion of main department
    if department_id == '01':
        flash('Cannot delete main department!', 'error')
        return redirect(url_for('departments.index'))

    # Check for dependencies before deletion
    users = get_users()
    consumption_records = get_consumption()

    has_users = any(user.get('department_id') == department_id for user in users)
    has_consumption = any(record.get('department_id') == department_id for record in consumption_records)

    if has_users:
        flash('Cannot delete department with assigned users!', 'error')
        return redirect(url_for('departments.index'))

    if has_consumption:
        flash('Cannot delete department with consumption records!', 'error')
        return redirect(url_for('departments.index'))

    try:
        delete_department(department_id)
        flash('Department deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting department: {str(e)}', 'error')

    return redirect(url_for('departments.index'))

@departments_bp.route('/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete():
    """Bulk delete departments"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'No items selected for deletion'}), 400

        # Check for main department in selection
        if '01' in ids:
            return jsonify({'success': False, 'message': 'Cannot delete main department!'}), 400

        # Get dependencies data once
        users = get_users()
        consumption_records = get_consumption()

        # Delete each item
        deleted_count = 0
        failed_items = []

        for department_id in ids:
            try:
                # Check if department has users or consumption
                has_users = any(user.get('department_id') == department_id for user in users)
                has_consumption = any(record.get('department_id') == department_id for record in consumption_records)

                if has_users:
                    failed_items.append(f"Department ID {department_id} has assigned users")
                    continue
                if has_consumption:
                    failed_items.append(f"Department ID {department_id} has consumption records")
                    continue

                # Skip renumbering during bulk delete (will renumber once at the end)
                delete_department(department_id, skip_renumber=True)
                deleted_count += 1

            except Exception as e:
                failed_items.append(f"Department ID {department_id}: {str(e)}")

        # Renumber once after all deletions are complete
        if deleted_count > 0:
            from app.utils.database import renumber_ids, cascade_update_department_references
            id_mapping = renumber_ids('departments', protect_ids=['01'])
            cascade_update_department_references(id_mapping)

        # Log the bulk delete activity
        log_activity(
            action='bulk_delete',
            entity_type='departments',
            details={'message': f'Bulk deleted {deleted_count} departments', 'count': deleted_count}
        )

        # Prepare response message
        if deleted_count == len(ids):
            message = f'Successfully deleted {deleted_count} departments'
            return jsonify({'success': True, 'message': message}), 200
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(ids)} departments. Failed: {", ".join(failed_items)}'
            return jsonify({'success': True, 'message': message, 'warnings': failed_items}), 200
        else:
            message = f'Failed to delete any departments. Errors: {", ".join(failed_items)}'
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk delete: {str(e)}'}), 500

@departments_bp.route('/template/download')
@admin_required
def download_template():
    """Download CSV template for departments import"""
    template_headers = [
        'name',
        'responsible_person',
        'telephone',
        'notes'
    ]

    csv_content = ','.join(template_headers) + '\n'
    csv_content += '# Example: Cardiology,Dr. Smith,+1-555-0123,Heart and cardiovascular care department\n'

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=departments_template.csv'}
    )
