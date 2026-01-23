"""
Patients Management Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response, jsonify, session
import csv
import io
from app.utils.decorators import login_required, admin_required
from app.utils.database import get_patients, save_patient, update_patient, delete_patient, get_departments, log_activity

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    """Patients list page"""
    if request.method == 'POST':
        # Handle CSV import
        if 'csv_file' not in request.files:
            flash('No file selected!', 'error')
            return redirect(url_for('patients.index'))

        file = request.files['csv_file']
        if file.filename == '':
            flash('No file selected!', 'error')
            return redirect(url_for('patients.index'))

        if not file.filename.lower().endswith('.csv'):
            flash('Please upload a CSV file!', 'error')
            return redirect(url_for('patients.index'))

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

                if not row.get('gender', '').strip():
                    errors.append(f"Row {row_num}: Gender is required")
                    continue

                # Create patient data
                patient_data = {
                    'name': row.get('name', '').strip(),
                    'file_no': row.get('file_no', '').strip(),
                    'gender': row.get('gender', '').strip(),
                    'date_of_entry': row.get('date_of_entry', '').strip(),
                    'department_id': row.get('department_id', '').strip(),
                    'medical_history': row.get('medical_history', '').strip(),
                    'notes': row.get('notes', '').strip()
                }

                # Save patient
                save_patient(patient_data)
                imported_count += 1

            if errors:
                flash(f'Import completed with {imported_count} patients imported. Errors: {"; ".join(errors)}', 'warning')
            else:
                flash(f'Successfully imported {imported_count} patients!', 'success')

        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'error')

        return redirect(url_for('patients.index'))

    patients = get_patients()
    departments = get_departments()
    return render_template('patients/index.html', patients=patients, departments=departments)

@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new patient"""
    if request.method == 'POST':
        # Validation
        name = request.form.get('name', '').strip()
        gender = request.form.get('gender', '').strip()
        date_of_entry = request.form.get('date_of_entry', '').strip()
        department_id = request.form.get('department_id', '').strip()

        if not name:
            flash('Patient name is required!', 'error')
            departments = get_departments()
            return render_template('patients/add.html', departments=departments)

        if not gender:
            flash('Gender is required!', 'error')
            departments = get_departments()
            return render_template('patients/add.html', departments=departments)

        if not date_of_entry:
            flash('Date of entry is required!', 'error')
            departments = get_departments()
            return render_template('patients/add.html', departments=departments)

        if not department_id:
            flash('Department is required!', 'error')
            departments = get_departments()
            return render_template('patients/add.html', departments=departments)

        patient_data = {
            'name': name,
            'file_no': request.form.get('file_no', ''),
            'gender': gender,
            'date_of_entry': date_of_entry,
            'medical_history': request.form.get('medical_history', ''),
            'notes': request.form.get('notes', ''),
            'department_id': department_id
        }

        patient_id = save_patient(patient_data)
        flash(f'Patient added successfully with ID: {patient_id}', 'success')
        return redirect(url_for('patients.index'))

    departments = get_departments()
    return render_template('patients/add.html', departments=departments)

@patients_bp.route('/edit/<patient_id>', methods=['GET', 'POST'])
@login_required
def edit(patient_id):
    """Edit patient"""
    patients = get_patients()
    patient = next((p for p in patients if p['id'] == patient_id), None)

    if not patient:
        flash('Patient not found!', 'error')
        return redirect(url_for('patients.index'))

    if request.method == 'POST':
        patient_data = {
            'name': request.form.get('name'),
            'file_no': request.form.get('file_no', ''),
            'gender': request.form.get('gender'),
            'date_of_entry': request.form.get('date_of_entry'),
            'medical_history': request.form.get('medical_history', ''),
            'notes': request.form.get('notes', ''),
            'department_id': request.form.get('department_id', '')
        }

        update_patient(patient_id, patient_data)
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('patients.index'))

    departments = get_departments()
    return render_template('patients/edit.html', patient=patient, departments=departments)

@patients_bp.route('/delete/<patient_id>')
@login_required
def delete(patient_id):
    """Delete patient"""
    delete_patient(patient_id)
    flash('Patient deleted successfully!', 'success')
    return redirect(url_for('patients.index'))

@patients_bp.route('/bulk-delete', methods=['POST'])
@login_required
@admin_required
def bulk_delete():
    """Bulk delete patients with cascading deletion of consumption records"""
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids:
            return jsonify({'success': False, 'message': 'No items selected for deletion'}), 400

        # Delete each patient with cascading deletion enabled
        deleted_count = 0
        failed_items = []
        deleted_consumption_count = 0

        # First, count how many consumption records will be deleted
        from app.utils.database import get_consumption
        consumption_records = get_consumption()
        for patient_id in ids:
            deleted_consumption_count += sum(
                1 for record in consumption_records
                if record.get('patient_id') == patient_id
            )

        for patient_id in ids:
            try:
                # Delete patient with cascading deletion (will delete consumption records automatically)
                # Skip renumbering during bulk delete (will renumber once at the end)
                delete_patient(patient_id, skip_renumber=True, cascade_delete=True)
                deleted_count += 1

            except Exception as e:
                failed_items.append(f"Patient ID {patient_id}: {str(e)}")

        # Renumber once after all deletions are complete
        if deleted_count > 0:
            from app.utils.database import renumber_ids, cascade_update_patient_references
            id_mapping = renumber_ids('patients', protect_ids=[])
            cascade_update_patient_references(id_mapping)

        # Log the bulk delete activity
        log_activity(
            action='bulk_delete',
            entity_type='patients',
            details={
                'message': f'Bulk deleted {deleted_count} patients and {deleted_consumption_count} consumption records',
                'patients_count': deleted_count,
                'consumption_count': deleted_consumption_count
            }
        )

        # Prepare response message
        if deleted_count == len(ids):
            if deleted_consumption_count > 0:
                message = f'Successfully deleted {deleted_count} patients and {deleted_consumption_count} associated consumption records'
            else:
                message = f'Successfully deleted {deleted_count} patients'
            return jsonify({'success': True, 'message': message}), 200
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(ids)} patients'
            if deleted_consumption_count > 0:
                message += f' and {deleted_consumption_count} associated consumption records'
            message += f'. Failed: {", ".join(failed_items)}'
            return jsonify({'success': True, 'message': message, 'warnings': failed_items}), 200
        else:
            message = f'Failed to delete any patients. Errors: {", ".join(failed_items)}'
            return jsonify({'success': False, 'message': message}), 400

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk delete: {str(e)}'}), 500

@patients_bp.route('/template/download')
@login_required
def download_template():
    """Download CSV template for patients import"""
    template_headers = [
        'name',
        'file_no',
        'gender',
        'date_of_entry',
        'department_id',
        'medical_history',
        'notes'
    ]

    csv_content = ','.join(template_headers) + '\n'
    csv_content += '# Example: John Doe,P001,Male,2025-07-25,01,Diabetes,Patient notes\n'

    return Response(
        csv_content,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=patients_template.csv'}
    )
