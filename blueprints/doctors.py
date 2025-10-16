"""
Doctors Management Blueprint
Handles doctor registration, management, and operations
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from utils.database import load_data, save_data, log_activity, generate_id, get_departments
from utils.helpers import login_required
from datetime import datetime
import json
import csv
import io
import os

doctors_bp = Blueprint('doctors', __name__)

# Dropdown options
SPECIALIST_OPTIONS = [
    ('surgery', 'Surgery'),
    ('gynecologist', 'Gynecologist'),
    ('dermatologist', 'Dermatologist'),
    ('gp', 'General Practitioner (G.P)'),
    ('pediatrician', 'Pediatrician'),
    ('cardiology', 'Cardiology'),
    ('neurology', 'Neurology'),
    ('orthopedics', 'Orthopedics'),
    ('psychiatry', 'Psychiatry'),
    ('radiology', 'Radiology'),
    ('anesthesiology', 'Anesthesiology'),
    ('emergency', 'Emergency Medicine'),
    ('internal_medicine', 'Internal Medicine'),
    ('ophthalmology', 'Ophthalmology'),
    ('ent', 'ENT (Ear, Nose, Throat)')
]

POSITION_OPTIONS = [
    ('specialist', 'Specialist'),
    ('consultant', 'Consultant'),
    ('professor', 'Professor'),
    ('senior_consultant', 'Senior Consultant'),
    ('chief', 'Chief of Department'),
    ('resident', 'Resident'),
    ('intern', 'Intern')
]

TYPE_OPTIONS = [
    ('employee', 'Employee'),
    ('visitor', 'Visitor')
]

GENDER_OPTIONS = [
    ('male', 'Male'),
    ('female', 'Female')
]

@doctors_bp.route('/')
@login_required
def index():
    """Display all doctors with filtering and sorting"""
    # Get filter parameters
    specialist_filter = request.args.get('specialist', '')
    position_filter = request.args.get('position', '')
    type_filter = request.args.get('type', '')
    gender_filter = request.args.get('gender', '')
    search = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'dr_name')
    sort_order = request.args.get('sort_order', 'asc')

    # Load doctors data
    doctors = load_data('doctors')

    # Apply filters
    if specialist_filter:
        doctors = [d for d in doctors if d.get('specialist') == specialist_filter]
    if position_filter:
        doctors = [d for d in doctors if d.get('position') == position_filter]
    if type_filter:
        doctors = [d for d in doctors if d.get('type') == type_filter]
    if gender_filter:
        doctors = [d for d in doctors if d.get('gender') == gender_filter]
    if search:
        search_lower = search.lower()
        doctors = [d for d in doctors if
                  search_lower in d.get('dr_name', '').lower() or
                  search_lower in d.get('email', '').lower() or
                  search_lower in d.get('mobile_no', '').lower() or
                  search_lower in d.get('nationality', '').lower()]

    # Apply sorting
    reverse = sort_order == 'desc'
    if sort_by in ['dr_name', 'specialist', 'position', 'type', 'gender', 'nationality']:
        doctors.sort(key=lambda x: x.get(sort_by, '').lower(), reverse=reverse)

    # Load departments
    departments = get_departments()

    # Log activity
    log_activity('VIEW', 'doctors_list', None, {
        'total_doctors': len(doctors),
        'filters_applied': bool(specialist_filter or position_filter or type_filter or gender_filter or search)
    })

    return render_template('doctors/index.html',
                         doctors=doctors,
                         departments=departments,
                         specialist_options=SPECIALIST_OPTIONS,
                         position_options=POSITION_OPTIONS,
                         type_options=TYPE_OPTIONS,
                         gender_options=GENDER_OPTIONS,
                         current_filters={
                             'specialist': specialist_filter,
                             'position': position_filter,
                             'type': type_filter,
                             'gender': gender_filter,
                             'search': search,
                             'sort_by': sort_by,
                             'sort_order': sort_order
                         })

@doctors_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new doctor"""
    if request.method == 'POST':
        # Get form data
        doctor_data = {
            'id': generate_id('doctors'),
            'dr_name': request.form.get('dr_name', '').strip(),
            'gender': request.form.get('gender', ''),
            'nationality': request.form.get('nationality', '').strip(),
            'department_id': request.form.get('department_id', '').strip(),
            'specialist': request.form.get('specialist', ''),
            'position': request.form.get('position', ''),
            'type': request.form.get('type', ''),
            'mobile_no': request.form.get('mobile_no', '').strip(),
            'email': request.form.get('email', '').strip(),
            'note': request.form.get('note', '').strip(),
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }

        # Validate required fields
        if not doctor_data['dr_name']:
            flash('Doctor name is required.', 'error')
            return redirect(url_for('doctors.add'))

        if not doctor_data['gender']:
            flash('Gender is required.', 'error')
            return redirect(url_for('doctors.add'))

        # Validate email format if provided
        if doctor_data['email'] and '@' not in doctor_data['email']:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('doctors.add'))

        try:
            # Load existing doctors
            doctors = load_data('doctors')

            # Check for duplicate email
            if doctor_data['email']:
                existing_email = next((d for d in doctors if d.get('email', '').lower() == doctor_data['email'].lower()), None)
                if existing_email:
                    flash('A doctor with this email already exists.', 'error')
                    return redirect(url_for('doctors.add'))

            # Add new doctor
            doctors.append(doctor_data)
            save_data('doctors', doctors)

            # Log activity
            log_activity('CREATE', 'doctor', doctor_data['id'], {
                'doctor_name': doctor_data['dr_name'],
                'specialist': doctor_data['specialist'],
                'type': doctor_data['type']
            })

            flash(f'Doctor {doctor_data["dr_name"]} added successfully!', 'success')
            return redirect(url_for('doctors.index'))

        except Exception as e:
            flash(f'Error adding doctor: {str(e)}', 'error')
            return redirect(url_for('doctors.add'))

    # Load departments for the dropdown
    departments = get_departments()

    return render_template('doctors/add.html',
                         specialist_options=SPECIALIST_OPTIONS,
                         position_options=POSITION_OPTIONS,
                         type_options=TYPE_OPTIONS,
                         gender_options=GENDER_OPTIONS,
                         departments=departments)

@doctors_bp.route('/edit/<doctor_id>', methods=['GET', 'POST'])
@login_required
def edit(doctor_id):
    """Edit existing doctor"""
    doctors = load_data('doctors')
    doctor = next((d for d in doctors if d['id'] == doctor_id), None)

    if not doctor:
        flash('Doctor not found.', 'error')
        return redirect(url_for('doctors.index'))

    # Transform old data format to new format for backward compatibility
    if 'name' in doctor and 'dr_name' not in doctor:
        doctor['dr_name'] = doctor['name']
    if 'specialization' in doctor and 'specialist' not in doctor:
        doctor['specialist'] = doctor['specialization']
    # Add default values for missing fields
    doctor.setdefault('gender', '')
    doctor.setdefault('nationality', '')
    doctor.setdefault('position', '')
    doctor.setdefault('type', '')
    doctor.setdefault('mobile_no', doctor.get('phone', ''))
    doctor.setdefault('email', '')
    doctor.setdefault('note', doctor.get('notes', ''))

    if request.method == 'POST':
        # Get form data
        updated_data = {
            'dr_name': request.form.get('dr_name', '').strip(),
            'gender': request.form.get('gender', ''),
            'nationality': request.form.get('nationality', '').strip(),
            'department_id': request.form.get('department_id', '').strip(),
            'specialist': request.form.get('specialist', ''),
            'position': request.form.get('position', ''),
            'type': request.form.get('type', ''),
            'mobile_no': request.form.get('mobile_no', '').strip(),
            'email': request.form.get('email', '').strip(),
            'note': request.form.get('note', '').strip(),
            'updated_at': datetime.now().isoformat()
        }

        # Validate required fields
        if not updated_data['dr_name']:
            flash('Doctor name is required.', 'error')
            return redirect(url_for('doctors.edit', doctor_id=doctor_id))

        if not updated_data['gender']:
            flash('Gender is required.', 'error')
            return redirect(url_for('doctors.edit', doctor_id=doctor_id))

        # Validate email format if provided
        if updated_data['email'] and '@' not in updated_data['email']:
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('doctors.edit', doctor_id=doctor_id))

        try:
            # Check for duplicate email (excluding current doctor)
            if updated_data['email']:
                existing_email = next((d for d in doctors if d['id'] != doctor_id and d.get('email', '').lower() == updated_data['email'].lower()), None)
                if existing_email:
                    flash('A doctor with this email already exists.', 'error')
                    return redirect(url_for('doctors.edit', doctor_id=doctor_id))

            # Update doctor data
            for i, d in enumerate(doctors):
                if d['id'] == doctor_id:
                    doctors[i].update(updated_data)
                    break

            save_data('doctors', doctors)

            # Log activity
            log_activity('UPDATE', 'doctor', doctor_id, {
                'doctor_name': updated_data['dr_name'],
                'specialist': updated_data['specialist'],
                'type': updated_data['type']
            })

            flash(f'Doctor {updated_data["dr_name"]} updated successfully!', 'success')
            return redirect(url_for('doctors.index'))

        except Exception as e:
            flash(f'Error updating doctor: {str(e)}', 'error')
            return redirect(url_for('doctors.edit', doctor_id=doctor_id))

    # Load departments for the dropdown
    departments = get_departments()

    return render_template('doctors/edit.html',
                         doctor=doctor,
                         specialist_options=SPECIALIST_OPTIONS,
                         position_options=POSITION_OPTIONS,
                         type_options=TYPE_OPTIONS,
                         gender_options=GENDER_OPTIONS,
                         departments=departments)

@doctors_bp.route('/preview/<doctor_id>')
@login_required
def preview(doctor_id):
    """Preview doctor details"""
    doctors = load_data('doctors')
    doctor = next((d for d in doctors if d['id'] == doctor_id), None)

    if not doctor:
        flash('Doctor not found.', 'error')
        return redirect(url_for('doctors.index'))

    # Load departments
    departments = get_departments()

    # Log activity
    log_activity('VIEW', 'doctor_preview', doctor_id, {
        'doctor_name': doctor.get('dr_name')
    })

    return render_template('doctors/preview.html', doctor=doctor, departments=departments)

@doctors_bp.route('/delete/<doctor_id>', methods=['POST'])
@login_required
def delete(doctor_id):
    """Delete doctor"""
    try:
        doctors = load_data('doctors')
        doctor = next((d for d in doctors if d['id'] == doctor_id), None)

        if not doctor:
            flash('Doctor not found.', 'error')
            return redirect(url_for('doctors.index'))

        # Remove doctor
        doctors = [d for d in doctors if d['id'] != doctor_id]
        save_data('doctors', doctors)

        # Log activity
        log_activity('DELETE', 'doctor', doctor_id, {
            'doctor_name': doctor.get('dr_name'),
            'specialist': doctor.get('specialist')
        })

        flash(f'Doctor {doctor.get("dr_name")} deleted successfully!', 'success')

    except Exception as e:
        flash(f'Error deleting doctor: {str(e)}', 'error')

    return redirect(url_for('doctors.index'))

@doctors_bp.route('/bulk-delete', methods=['POST'])
@login_required
def bulk_delete():
    """Bulk delete doctors"""
    try:
        data = request.get_json()
        doctor_ids = data.get('ids', [])

        if not doctor_ids:
            return jsonify({'success': False, 'message': 'No doctors selected'})

        doctors = load_data('doctors')
        deleted_doctors = []

        # Get doctors to be deleted for logging
        for doctor_id in doctor_ids:
            doctor = next((d for d in doctors if d['id'] == doctor_id), None)
            if doctor:
                deleted_doctors.append(doctor.get('dr_name', f'ID: {doctor_id}'))

        # Remove selected doctors
        doctors = [d for d in doctors if d['id'] not in doctor_ids]
        save_data('doctors', doctors)

        # Log activity
        log_activity('BULK_DELETE', 'doctors', None, {
            'deleted_count': len(doctor_ids),
            'deleted_doctors': deleted_doctors
        })

        return jsonify({
            'success': True,
            'message': f'Successfully deleted {len(doctor_ids)} doctor(s)'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})

@doctors_bp.route('/export')
@login_required
def export():
    """Export doctors to CSV"""
    try:
        doctors = load_data('doctors')

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['ID', 'Doctor Name', 'Gender', 'Nationality', 'Department ID', 'Specialist',
                        'Position', 'Type', 'Mobile No', 'Email', 'Note', 'Created At', 'Updated At'])

        # Write data
        for doctor in doctors:
            writer.writerow([
                doctor.get('id', ''),
                doctor.get('dr_name', ''),
                doctor.get('gender', ''),
                doctor.get('nationality', ''),
                doctor.get('department_id', ''),
                doctor.get('specialist', ''),
                doctor.get('position', ''),
                doctor.get('type', ''),
                doctor.get('mobile_no', ''),
                doctor.get('email', ''),
                doctor.get('note', ''),
                doctor.get('created_at', ''),
                doctor.get('updated_at', '')
            ])

        # Create file-like object
        output.seek(0)
        output_bytes = io.BytesIO()
        output_bytes.write(output.getvalue().encode('utf-8'))
        output_bytes.seek(0)

        # Log activity
        log_activity('EXPORT', 'doctors', None, {
            'total_exported': len(doctors),
            'format': 'CSV'
        })

        return send_file(
            output_bytes,
            as_attachment=True,
            download_name=f'doctors_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
            mimetype='text/csv'
        )

    except Exception as e:
        flash(f'Error exporting doctors: {str(e)}', 'error')
        return redirect(url_for('doctors.index'))

@doctors_bp.route('/import', methods=['GET', 'POST'])
@login_required
def import_doctors():
    """Import doctors from CSV"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected.', 'error')
            return redirect(url_for('doctors.import_doctors'))

        file = request.files['file']
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('doctors.import_doctors'))

        if not file.filename.lower().endswith('.csv'):
            flash('Please select a CSV file.', 'error')
            return redirect(url_for('doctors.import_doctors'))

        try:
            # Read CSV file
            stream = io.StringIO(file.stream.read().decode('utf-8'))
            csv_reader = csv.DictReader(stream)

            doctors = load_data('doctors')
            imported_count = 0
            errors = []

            for row_num, row in enumerate(csv_reader, start=2):
                try:
                    # Clean and validate data
                    dr_name = row.get('Doctor Name', '').strip()
                    gender = row.get('Gender', '').strip().lower()
                    email = row.get('Email', '').strip()

                    if not dr_name:
                        errors.append(f'Row {row_num}: Doctor name is required')
                        continue

                    if gender not in ['male', 'female']:
                        errors.append(f'Row {row_num}: Gender must be "male" or "female"')
                        continue

                    # Check for duplicate email
                    if email and any(d.get('email', '').lower() == email.lower() for d in doctors):
                        errors.append(f'Row {row_num}: Email {email} already exists')
                        continue

                    # Create doctor record
                    doctor_data = {
                        'id': generate_id('doctors'),
                        'dr_name': dr_name,
                        'gender': gender,
                        'nationality': row.get('Nationality', '').strip(),
                        'department_id': row.get('Department ID', '').strip(),
                        'specialist': row.get('Specialist', '').strip().lower(),
                        'position': row.get('Position', '').strip().lower(),
                        'type': row.get('Type', '').strip().lower(),
                        'mobile_no': row.get('Mobile No', '').strip(),
                        'email': email,
                        'note': row.get('Note', '').strip(),
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }

                    doctors.append(doctor_data)
                    imported_count += 1

                except Exception as e:
                    errors.append(f'Row {row_num}: {str(e)}')

            # Save imported data
            if imported_count > 0:
                save_data('doctors', doctors)

            # Log activity
            log_activity('IMPORT', 'doctors', None, {
                'imported_count': imported_count,
                'error_count': len(errors),
                'total_rows': row_num - 1 if 'row_num' in locals() else 0
            })

            # Show results
            if imported_count > 0:
                flash(f'Successfully imported {imported_count} doctor(s).', 'success')
            if errors:
                flash(f'Import completed with {len(errors)} error(s). Check the details below.', 'warning')
                for error in errors[:10]:  # Show first 10 errors
                    flash(error, 'error')

        except Exception as e:
            flash(f'Error importing file: {str(e)}', 'error')

        return redirect(url_for('doctors.index'))

    return render_template('doctors/import.html')