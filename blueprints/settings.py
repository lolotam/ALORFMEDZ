"""
Settings Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from utils.helpers import login_required, admin_required
from utils.database import (
    get_medicines, get_patients, get_suppliers, get_departments, get_history,
    get_users, get_user_activity_summary, save_user, update_user, delete_user,
    get_user_by_id, generate_secure_password, create_department_user,
    get_stores, get_purchases, get_consumption, save_data, load_data, log_activity
)
import os
import zipfile
import json
from datetime import datetime
from werkzeug.utils import secure_filename

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@login_required
def index():
    """Settings dashboard"""
    return render_template('settings/index.html')



@settings_bp.route('/about')
@login_required
def about():
    """About page"""
    # Get system statistics
    medicines = get_medicines()
    patients = get_patients()
    suppliers = get_suppliers()
    departments = get_departments()

    stats = {
        'total_medicines': len(medicines),
        'total_patients': len(patients),
        'total_suppliers': len(suppliers),
        'total_departments': len(departments)
    }

    return render_template('settings/about.html', **stats)

@settings_bp.route('/history')
@login_required
def history():
    """Activity history page"""
    from flask import request, session

    # Get filter parameters
    user_id = request.args.get('user_id')
    action = request.args.get('action')
    entity_type = request.args.get('entity_type')

    # For non-admin users, only show their own history
    if session.get('role') != 'admin':
        user_id = session.get('user_id')

    # Get filtered history
    history_data = get_history(limit=200, user_id=user_id, entity_type=entity_type)

    # Apply action filter
    if action:
        history_data = [h for h in history_data if h.get('action') == action]

    # Get users for admin filter
    users = get_users() if session.get('role') == 'admin' else []

    return render_template('settings/history.html',
                         history=history_data,
                         users=users)

@settings_bp.route('/users')
@admin_required
def users():
    """User management page (admin only)"""
    users = get_users()
    departments = get_departments()

    # Get activity summary for each user
    user_activities = {}
    for user in users:
        user_activities[user['id']] = get_user_activity_summary(user['id'])

    return render_template('settings/users.html',
                         users=users,
                         departments=departments,
                         user_activities=user_activities)

@settings_bp.route('/users/add', methods=['POST'])
@admin_required
def add_user():
    """Add new user (admin only)"""
    try:
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'department_user')
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        department_id = request.form.get('department_id', '').strip()

        # Validation
        if not username:
            flash('Username is required!', 'error')
            return redirect(url_for('settings.users'))

        if not password:
            flash('Password is required!', 'error')
            return redirect(url_for('settings.users'))

        if role == 'department_user' and not department_id:
            flash('Department is required for department users!', 'error')
            return redirect(url_for('settings.users'))

        # Prepare user data
        user_data = {
            'username': username,
            'password': password,
            'role': role,
            'name': name or username.title(),
            'email': email or f"{username}@hospital.com"
        }

        # Add department_id for department users
        if role == 'department_user' and department_id:
            user_data['department_id'] = department_id

        # Save user
        user_id = save_user(user_data)
        flash(f'User "{username}" created successfully!', 'success')

    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error creating user: {str(e)}', 'error')

    return redirect(url_for('settings.users'))

@settings_bp.route('/users/edit/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user (admin only)"""
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('settings.users'))

    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', user.get('role', 'department_user'))
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            department_id = request.form.get('department_id', '').strip()

            # Validation
            if not username:
                flash('Username is required!', 'error')
                return redirect(url_for('settings.edit_user', user_id=user_id))

            if role == 'department_user' and not department_id:
                flash('Department is required for department users!', 'error')
                return redirect(url_for('settings.edit_user', user_id=user_id))

            # Prepare update data
            update_data = {
                'username': username,
                'role': role,
                'name': name or username.title(),
                'email': email or f"{username}@hospital.com"
            }

            # Add password if provided
            if password:
                update_data['password'] = password

            # Add department_id for department users
            if role == 'department_user' and department_id:
                update_data['department_id'] = department_id
            elif role == 'admin':
                update_data['department_id'] = None

            # Update user
            update_user(user_id, update_data)
            flash(f'User "{username}" updated successfully!', 'success')
            return redirect(url_for('settings.users'))

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'error')

    # GET request - show edit form
    departments = get_departments()
    return render_template('settings/edit_user.html', user=user, departments=departments)

@settings_bp.route('/users/delete/<user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    """Delete user (admin only)"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('settings.users'))

        username = user.get('username', 'Unknown')
        delete_user(user_id)
        flash(f'User "{username}" deleted successfully!', 'success')

    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')

    return redirect(url_for('settings.users'))

@settings_bp.route('/users/reset_password/<user_id>', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Reset user password (admin only)"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('settings.users'))

        # Generate new password
        new_password = generate_secure_password()

        # Update user password
        update_user(user_id, {'password': new_password})

        username = user.get('username', 'Unknown')
        flash(f'Password reset for "{username}". New password: {new_password}', 'success')
        flash('Please save this password and share it with the user.', 'warning')

    except Exception as e:
        flash(f'Error resetting password: {str(e)}', 'error')

    return redirect(url_for('settings.users'))

@settings_bp.route('/users/create_department_user/<department_id>', methods=['POST'])
@admin_required
def create_dept_user(department_id):
    """Create additional department user for existing department"""
    try:
        departments = get_departments()
        department = next((d for d in departments if d['id'] == department_id), None)

        if not department:
            flash('Department not found!', 'error')
            return redirect(url_for('settings.users'))

        # Create department user
        user_info = create_department_user(department_id, department['name'])

        flash(f'Department user created successfully!', 'success')
        flash(f'Username: {user_info["username"]}, Password: {user_info["password"]}', 'info')
        flash('Please save these credentials and share them with the department staff.', 'warning')

    except Exception as e:
        flash(f'Error creating department user: {str(e)}', 'error')

    return redirect(url_for('settings.users'))

@settings_bp.route('/backup/full')
@admin_required
def backup_full():
    """Create and download full system backup as CSV ZIP"""
    try:
        import tempfile
        from utils.database import load_data

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'pharmacy_csv_backup_{timestamp}.zip'
        backup_path = os.path.join('data', backup_filename)

        # Create temporary directory for CSV files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create ZIP file with CSV exports
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:

                # Export all data types to CSV
                csv_files = export_all_data_to_csv(temp_dir)
                for csv_file in csv_files:
                    if os.path.exists(csv_file):
                        zipf.write(csv_file, os.path.basename(csv_file))

                # Add backup metadata
                metadata = {
                    'backup_date': datetime.now().isoformat(),
                    'backup_type': 'full_system_csv',
                    'description': 'Complete system backup in CSV format',
                    'version': '2.0.0',
                    'format': 'CSV',
                    'files_included': [
                        'medicines', 'patients', 'suppliers', 'departments',
                        'doctors', 'stores', 'purchases', 'consumption',
                        'history', 'transfers', 'users'
                    ]
                }
                zipf.writestr('backup_metadata.json', json.dumps(metadata, indent=2))

        # Log the activity
        log_activity(
            'create_full_csv_backup',
            'system',
            session.get('user_id'),
            {'message': f'Created full CSV backup: {backup_filename}', 'backup_type': 'csv'}
        )

        return send_file(backup_path, as_attachment=True, download_name=backup_filename)

    except Exception as e:
        flash(f'CSV backup failed: {str(e)}', 'error')
        return redirect(url_for('settings.index'))

@settings_bp.route('/backup/file/<file_type>')
@admin_required
def backup_file(file_type):
    """Download individual data file as CSV"""
    try:
        import tempfile
        import csv
        from utils.database import load_data

        # Map file types to appropriate export functions
        export_functions = {
            'medicines': export_medicines_to_csv,
            'patients': export_patients_to_csv,
            'suppliers': export_suppliers_to_csv,
            'departments': export_departments_to_csv,
            'doctors': export_doctors_to_csv,
            'stores': export_stores_to_csv,
            'purchases': export_purchases_to_csv,
            'consumption': export_consumption_to_csv,
            'transfers': export_transfers_to_csv,
            'users': export_users_to_csv,
            'history': export_history_to_csv
        }

        if file_type not in export_functions:
            flash('Invalid file type.', 'error')
            return redirect(url_for('settings.index'))

        # Load data
        data = load_data(file_type)
        if not data:
            flash(f'No {file_type} data found.', 'warning')
            return redirect(url_for('settings.index'))

        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv', encoding='utf-8') as temp_file:
            export_function = export_functions[file_type]
            export_function(data, temp_file.name)
            temp_file_path = temp_file.name

        # Generate download filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        download_name = f'{file_type}_{timestamp}.csv'

        # Log the activity
        log_activity(
            'download_csv',
            file_type,
            session.get('user_id'),
            {'message': f'Downloaded {file_type} CSV backup', 'file_type': file_type}
        )

        return send_file(temp_file_path, as_attachment=True, download_name=download_name)

    except Exception as e:
        flash(f'CSV export failed: {str(e)}', 'error')
        return redirect(url_for('settings.index'))

@settings_bp.route('/restore', methods=['GET', 'POST'])
@admin_required
def restore():
    """Restore system from backup"""
    if request.method == 'POST':
        try:
            if 'backup_file' not in request.files:
                flash('No backup file selected.', 'error')
                return redirect(url_for('settings.restore'))

            file = request.files['backup_file']
            if file.filename == '':
                flash('No backup file selected.', 'error')
                return redirect(url_for('settings.restore'))

            if not file.filename.endswith('.zip'):
                flash('Please upload a ZIP backup file.', 'error')
                return redirect(url_for('settings.restore'))

            # Save uploaded file
            from utils.database import DATA_DIR
            filename = secure_filename(file.filename)
            upload_path = os.path.join(DATA_DIR, f'restore_{filename}')
            file.save(upload_path)

            # Extract and validate backup
            extracted_files = []
            with zipfile.ZipFile(upload_path, 'r') as zipf:
                # Check for metadata
                if 'backup_metadata.json' in zipf.namelist():
                    metadata_content = zipf.read('backup_metadata.json')
                    metadata = json.loads(metadata_content)
                    flash(f'Backup created on: {metadata.get("backup_date", "Unknown")}', 'info')

                # Extract data files
                from utils.database import DB_FILES
                for file_type in DB_FILES.keys():
                    json_filename = f'{file_type}.json'
                    if json_filename in zipf.namelist():
                        # Validate JSON content
                        content = zipf.read(json_filename)
                        try:
                            json.loads(content)  # Validate JSON
                            # Extract to data directory
                            zipf.extract(json_filename, DATA_DIR)
                            # Rename to proper filename
                            extracted_path = os.path.join(DATA_DIR, json_filename)
                            target_path = DB_FILES[file_type]
                            if os.path.exists(extracted_path):
                                os.replace(extracted_path, target_path)
                                extracted_files.append(file_type)
                        except json.JSONDecodeError:
                            flash(f'Invalid JSON in {json_filename}', 'warning')

            # Clean up
            os.remove(upload_path)

            if extracted_files:
                flash(f'Successfully restored {len(extracted_files)} data files: {", ".join(extracted_files)}', 'success')
            else:
                flash('No valid data files found in backup.', 'warning')

            return redirect(url_for('settings.index'))

        except Exception as e:
            flash(f'Restore failed: {str(e)}', 'error')
            return redirect(url_for('settings.restore'))

    return render_template('settings/restore.html')

@settings_bp.route('/generate-sample-data')
@admin_required
def generate_sample_data():
    """Generate comprehensive sample data"""
    try:
        from utils.enhanced_sample_data import generate_enhanced_sample_data
        data_collections, zip_path = generate_enhanced_sample_data()

        # Count total records
        total_records = sum(len(data) for data in data_collections.values())

        flash(f'Enhanced sample data generated successfully! Created {total_records} records across all sections. Backup ZIP: {os.path.basename(zip_path)}', 'success')
    except Exception as e:
        flash(f'Sample data generation failed: {str(e)}', 'error')

    return redirect(url_for('settings.index'))

# ========== SECURITY SETTINGS ==========

@settings_bp.route('/security')
@admin_required
def security():
    """Security settings page"""
    # Get audit log stats
    audit_logs = get_history(limit=1000)

    stats = {
        'total_audit_logs': len(audit_logs),
        'recent_activities': len([log for log in audit_logs if
            (datetime.now() - datetime.fromisoformat(log.get('timestamp', '1970-01-01T00:00:00'))).days <= 7])
    }

    return render_template('settings/security.html', **stats)

@settings_bp.route('/security/backup', methods=['POST'])
@admin_required
def create_backup():
    """Create a comprehensive backup of all data with CSV exports"""
    try:
        import tempfile
        import csv
        import io
        from utils.database import DB_FILES

        backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f'hospital_pharmacy_backup_{backup_time}.zip'
        backup_path = os.path.join('backups', backup_filename)

        # Ensure backups directory exists
        os.makedirs('backups', exist_ok=True)

        # Create temporary directory for CSV files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create backup ZIP file
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
                # Add JSON files
                for data_type, file_path in DB_FILES.items():
                    if os.path.exists(file_path):
                        backup_zip.write(file_path, f'json/{data_type}.json')

                # Generate and add CSV files
                csv_files = export_all_data_to_csv(temp_dir)
                for csv_file in csv_files:
                    backup_zip.write(csv_file, f'csv/{os.path.basename(csv_file)}')

                # Add backup metadata
                metadata = {
                    'backup_date': datetime.now().isoformat(),
                    'backup_type': 'security_comprehensive',
                    'description': 'Complete security backup with JSON and CSV formats',
                    'version': '2.0.0',
                    'files_included': list(DB_FILES.keys()),
                    'user_id': session.get('user_id'),
                    'username': session.get('username')
                }
                backup_zip.writestr('backup_metadata.json', json.dumps(metadata, indent=2))

        # Log the backup activity
        log_activity(
            'create_security_backup',
            'system',
            session.get('user_id'),
            {'message': f'Created comprehensive backup: {backup_filename}', 'backup_type': 'security'}
        )

        return send_file(backup_path, as_attachment=True, download_name=backup_filename)

    except Exception as e:
        return jsonify({'success': False, 'message': f'Backup failed: {str(e)}'}), 500

def export_all_data_to_csv(output_dir):
    """Export all data to CSV files and return list of created files"""
    csv_files = []

    try:
        # Export medicines
        medicines = get_medicines()
        if medicines:
            csv_path = os.path.join(output_dir, 'medicines.csv')
            export_medicines_to_csv(medicines, csv_path)
            csv_files.append(csv_path)

        # Export patients
        patients = get_patients()
        if patients:
            csv_path = os.path.join(output_dir, 'patients.csv')
            export_patients_to_csv(patients, csv_path)
            csv_files.append(csv_path)

        # Export suppliers
        suppliers = get_suppliers()
        if suppliers:
            csv_path = os.path.join(output_dir, 'suppliers.csv')
            export_suppliers_to_csv(suppliers, csv_path)
            csv_files.append(csv_path)

        # Export departments
        departments = get_departments()
        if departments:
            csv_path = os.path.join(output_dir, 'departments.csv')
            export_departments_to_csv(departments, csv_path)
            csv_files.append(csv_path)

        # Export doctors
        try:
            from utils.database import load_data
            doctors = load_data('doctors')
            if doctors:
                csv_path = os.path.join(output_dir, 'doctors.csv')
                export_doctors_to_csv(doctors, csv_path)
                csv_files.append(csv_path)
        except:
            pass  # Doctors might not exist yet

        # Export stores
        stores = get_stores()
        if stores:
            csv_path = os.path.join(output_dir, 'stores.csv')
            export_stores_to_csv(stores, csv_path)
            csv_files.append(csv_path)

        # Export purchases
        purchases = get_purchases()
        if purchases:
            csv_path = os.path.join(output_dir, 'purchases.csv')
            export_purchases_to_csv(purchases, csv_path)
            csv_files.append(csv_path)

        # Export consumption
        consumption = get_consumption()
        if consumption:
            csv_path = os.path.join(output_dir, 'consumption.csv')
            export_consumption_to_csv(consumption, csv_path)
            csv_files.append(csv_path)

        # Export transfers
        try:
            from utils.database import load_data
            transfers = load_data('transfers')
            if transfers:
                csv_path = os.path.join(output_dir, 'transfers.csv')
                export_transfers_to_csv(transfers, csv_path)
                csv_files.append(csv_path)
        except:
            pass

        # Export users (without passwords)
        users = get_users()
        if users:
            csv_path = os.path.join(output_dir, 'users.csv')
            export_users_to_csv(users, csv_path)
            csv_files.append(csv_path)

        # Export history
        history = get_history(limit=5000)
        if history:
            csv_path = os.path.join(output_dir, 'history.csv')
            export_history_to_csv(history, csv_path)
            csv_files.append(csv_path)

    except Exception as e:
        print(f"Error exporting CSV files: {str(e)}")

    return csv_files

@settings_bp.route('/security/audit-logs')
@admin_required
def audit_logs():
    """View audit logs"""
    page = request.args.get('page', 1, type=int)
    per_page = 50

    # Get audit logs
    all_logs = get_history(limit=2000)

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    logs = all_logs[start:end]

    # Total pages
    total_pages = (len(all_logs) + per_page - 1) // per_page

    return render_template('settings/audit_logs.html',
                          logs=logs,
                          current_page=page,
                          total_pages=total_pages,
                          total_logs=len(all_logs))

@settings_bp.route('/security/erase-all-data', methods=['POST'])
@admin_required
def erase_all_data():
    """Erase all data from the system (DANGEROUS)"""
    try:
        # Get confirmation from request
        data = request.get_json()
        confirm_text = data.get('confirm_text', '')

        if confirm_text != 'ERASE ALL DATA':
            return jsonify({'success': False, 'message': 'Confirmation text does not match'}), 400

        # Log the action before erasing
        log_activity(
            action='erase_all_data',
            entity_type='system',
            details={'message': 'CRITICAL: All system data erased by admin', 'user_id': session.get('user_id')}
        )

        # Initialize fresh data structures (keeping only admin user)
        from utils.database import init_database, DB_FILES, ensure_main_entities

        # Backup admin user before reset
        admin_user = None
        users = get_users()
        for user in users:
            if user.get('username') == 'admin':
                admin_user = user
                break

        # Backup main department before reset
        main_department = None
        departments = get_departments()
        for dept in departments:
            if dept.get('id') == '01':
                main_department = dept
                break

        # Backup main store before reset
        main_store = None
        stores = get_stores()
        for store in stores:
            if store.get('id') == '01':
                main_store = store
                break

        # Clear all data files (but preserve essential entities)
        for file_type, file_path in DB_FILES.items():
            if file_type == 'users':
                # Keep only admin user
                if admin_user:
                    save_data('users', [admin_user])
                else:
                    save_data('users', [])
            elif file_type == 'departments':
                # Keep main department or recreate if not found
                if main_department:
                    save_data('departments', [main_department])
                else:
                    # Recreate main department
                    default_main_dept = {
                        'id': '01',
                        'name': 'Main Pharmacy',
                        'description': 'Main hospital pharmacy department',
                        'responsible_person': 'Madam Tina',
                        'telephone': '+1234567890',
                        'notes': 'Main hospital pharmacy department - System Protected',
                        'created_at': datetime.now().isoformat()
                    }
                    save_data('departments', [default_main_dept])
            elif file_type == 'stores':
                # Keep main store or recreate if not found
                if main_store:
                    # Clear inventory but keep the store structure
                    main_store['inventory'] = {}
                    save_data('stores', [main_store])
                else:
                    # Recreate main store
                    default_main_store = {
                        'id': '01',
                        'name': 'Main Pharmacy Store',
                        'department_id': '01',
                        'location': 'Main Building, Ground Floor',
                        'description': 'Main pharmacy store - System Protected',
                        'inventory': {},
                        'created_at': datetime.now().isoformat()
                    }
                    save_data('stores', [default_main_store])
            else:
                # Clear other data files
                save_data(file_type, [])

        # Reinitialize with defaults (but preserve admin)
        if not admin_user:
            init_database()

        # Ensure main entities always exist after erase
        ensure_main_entities()

        return jsonify({'success': True, 'message': 'All data has been erased. Main department and store protected and preserved.'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Data erasure failed: {str(e)}'}), 500

@settings_bp.route('/security/audit-logs/export')
@admin_required
def export_audit_logs():
    """Export audit logs as CSV"""
    try:
        import csv
        import io

        # Get all audit logs
        logs = get_history(limit=5000)

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(['Timestamp', 'User ID', 'Action', 'Entity Type', 'Entity ID', 'Details'])

        # Write data
        for log in logs:
            writer.writerow([
                log.get('timestamp', ''),
                log.get('user_id', ''),
                log.get('action', ''),
                log.get('entity_type', ''),
                log.get('entity_id', ''),
                str(log.get('details', ''))
            ])

        # Create response
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        )

    except Exception as e:
        flash(f'Export failed: {str(e)}', 'error')
        return redirect(url_for('settings.audit_logs'))

@settings_bp.route('/history/clear', methods=['POST'])
@admin_required
def clear_history():
    """Clear all activity history"""
    try:
        # Log the action before clearing
        log_activity(
            user_id=session.get('user_id'),
            action='clear_history',
            entity_type='system',
            details={'message': 'Activity history cleared by admin'}
        )

        # Clear history
        save_data('history', [])
        flash('Activity history cleared successfully!', 'success')

    except Exception as e:
        flash(f'Error clearing history: {str(e)}', 'error')

    return redirect(url_for('settings.history'))

@settings_bp.route('/history/delete', methods=['POST'])
@admin_required
def delete_history_records():
    """Delete specific history records"""
    try:
        data = request.get_json()
        record_ids = data.get('record_ids', [])

        if not record_ids:
            return jsonify({'success': False, 'message': 'No records selected'}), 400

        # Load current history
        history = load_data('history')

        # Create a list to track which records are being deleted
        deleted_records = []

        # Filter out the records to delete (by timestamp as unique ID)
        filtered_history = []
        for record in history:
            if record.get('timestamp') in record_ids:
                deleted_records.append(record)
            else:
                filtered_history.append(record)

        # Save the filtered history
        save_data('history', filtered_history)

        # Log the deletion activity
        log_activity(
            user_id=session.get('user_id'),
            action='delete_history_records',
            entity_type='system',
            details={
                'message': f'Deleted {len(deleted_records)} history records',
                'deleted_count': len(deleted_records)
            }
        )

        return jsonify({
            'success': True,
            'message': f'Successfully deleted {len(deleted_records)} record(s)'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting records: {str(e)}'}), 500

# Manual Backup Management Routes
@settings_bp.route('/create-manual-backup', methods=['POST'])
@admin_required
def create_manual_backup():
    """Create a manual backup"""
    try:
        import os
        from datetime import datetime

        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'manual_backup_{timestamp}.zip'
        backup_path = os.path.join('backups', backup_filename)

        # Ensure backups directory exists
        os.makedirs('backups', exist_ok=True)

        # Create ZIP backup with both JSON and CSV files
        import zipfile
        with zipfile.ZipFile(backup_path, 'w') as backup_zip:
            # Add metadata
            metadata = {
                'backup_date': datetime.now().isoformat(),
                'type': 'manual',
                'version': '1.0',
                'description': 'Manual backup created by user',
                'user_id': session.get('user_id'),
                'username': session.get('username')
            }
            backup_zip.writestr('backup_metadata.json', json.dumps(metadata, indent=2))

            # Get all data and add both JSON and CSV files
            from utils.database import DB_FILES
            data_types = ['medicines', 'patients', 'suppliers', 'departments', 'doctors',
                         'stores', 'purchases', 'consumption', 'transfers', 'users', 'history']

            for data_type in data_types:
                try:
                    # Add JSON file (required for restore)
                    json_file_path = DB_FILES.get(data_type)
                    if json_file_path and os.path.exists(json_file_path):
                        backup_zip.write(json_file_path, f'{data_type}.json')

                    # Also add CSV file for easy viewing
                    data = load_data(data_type)
                    csv_filename = f'{data_type}.csv'
                    csv_path = f'{data_type}_temp.csv'

                    # Export to CSV
                    if data_type == 'medicines':
                        export_medicines_to_csv(data, csv_path)
                    elif data_type == 'patients':
                        export_patients_to_csv(data, csv_path)
                    elif data_type == 'suppliers':
                        export_suppliers_to_csv(data, csv_path)
                    elif data_type == 'departments':
                        export_departments_to_csv(data, csv_path)
                    elif data_type == 'doctors':
                        export_doctors_to_csv(data, csv_path)
                    elif data_type == 'stores':
                        export_stores_to_csv(data, csv_path)
                    elif data_type == 'purchases':
                        export_purchases_to_csv(data, csv_path)
                    elif data_type == 'consumption':
                        export_consumption_to_csv(data, csv_path)
                    elif data_type == 'transfers':
                        export_transfers_to_csv(data, csv_path)
                    elif data_type == 'users':
                        export_users_to_csv(data, csv_path)
                    elif data_type == 'history':
                        export_history_to_csv(data, csv_path)

                    # Add CSV to ZIP
                    if os.path.exists(csv_path):
                        backup_zip.write(csv_path, csv_filename)
                        # Clean up temp file
                        os.remove(csv_path)

                except Exception as e:
                    print(f"Warning: Could not backup {data_type}: {e}")

        # Log the backup creation
        log_activity(
            action='create_manual_backup',
            entity_type='system',
            details={'backup_file': backup_filename}
        )

        return jsonify({
            'success': True,
            'message': f'Manual backup created successfully: {backup_filename}'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error creating backup: {str(e)}'}), 500

@settings_bp.route('/backup-records')
@admin_required
def get_backup_records():
    """Get list of all backup records"""
    try:
        import os
        import zipfile
        from datetime import datetime

        backups = []
        backup_dir = 'backups'
        total_size = 0

        if os.path.exists(backup_dir):
            for filename in os.listdir(backup_dir):
                if filename.endswith('.zip'):
                    filepath = os.path.join(backup_dir, filename)
                    if os.path.isfile(filepath):
                        stat = os.stat(filepath)
                        total_size += stat.st_size

                        # Determine backup type from filename
                        backup_type = 'auto' if filename.startswith('pharmacy_data_backup_') else 'manual'

                        backups.append({
                            'filename': filename,
                            'type': backup_type,
                            'size': stat.st_size,
                            'created_date': datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })

        # Sort by creation date (newest first)
        backups.sort(key=lambda x: x['created_date'], reverse=True)

        stats = {
            'total': len(backups),
            'storage_used': total_size,
            'last_auto_backup': 'Never',  # TODO: Track last auto backup
            'next_scheduled': 'Not configured'  # TODO: Track scheduled backups
        }

        return jsonify({
            'success': True,
            'backups': backups,
            'stats': stats
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error loading backup records: {str(e)}'}), 500

@settings_bp.route('/auto-backup-settings', methods=['POST'])
@admin_required
def save_auto_backup_settings():
    """Save auto backup settings"""
    try:
        data = request.get_json()
        enabled = data.get('enabled', False)
        frequency = data.get('frequency', 'weekly')
        max_backups = data.get('max_backups', 10)

        # Save settings (you might want to store this in a config file or database)
        settings = {
            'auto_backup_enabled': enabled,
            'backup_frequency': frequency,
            'max_backups': max_backups,
            'updated_at': datetime.now().isoformat()
        }

        # For now, just log the activity
        log_activity(
            action='update_auto_backup_settings',
            entity_type='system',
            details=settings
        )

        return jsonify({
            'success': True,
            'message': 'Auto backup settings saved successfully'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error saving settings: {str(e)}'}), 500

@settings_bp.route('/download-backup/<filename>')
@admin_required
def download_backup(filename):
    """Download a backup file"""
    try:
        import os
        from flask import send_file

        backup_path = os.path.join('backups', filename)

        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Backup file not found'}), 404

        # Log the download
        log_activity(
            action='download_backup',
            entity_type='system',
            details={'filename': filename}
        )

        return send_file(backup_path, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error downloading backup: {str(e)}'}), 500

@settings_bp.route('/delete-backup/<filename>', methods=['DELETE'])
@admin_required
def delete_backup(filename):
    """Delete a single backup file"""
    try:
        import os

        backup_path = os.path.join('backups', filename)

        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Backup file not found'}), 404

        # Delete the file
        os.remove(backup_path)

        # Log the deletion
        log_activity(
            action='delete_backup',
            entity_type='system',
            details={'filename': filename}
        )

        return jsonify({
            'success': True,
            'message': f'Backup {filename} deleted successfully'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting backup: {str(e)}'}), 500

@settings_bp.route('/delete-backups-bulk', methods=['POST'])
@admin_required
def delete_backups_bulk():
    """Delete multiple backup files"""
    try:
        import os
        data = request.get_json()
        filenames = data.get('filenames', [])

        if not filenames:
            return jsonify({'success': False, 'message': 'No files selected for deletion'}), 400

        deleted_count = 0
        failed_files = []

        for filename in filenames:
            try:
                backup_path = os.path.join('backups', filename)
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                    deleted_count += 1
                else:
                    failed_files.append(f"{filename} (not found)")
            except Exception as e:
                failed_files.append(f"{filename} ({str(e)})")

        # Log the bulk deletion
        log_activity(
            action='delete_backups_bulk',
            entity_type='system',
            details={'deleted_count': deleted_count, 'total_requested': len(filenames)}
        )

        if deleted_count == len(filenames):
            message = f'Successfully deleted {deleted_count} backup file(s)'
        elif deleted_count > 0:
            message = f'Deleted {deleted_count} out of {len(filenames)} files. Failed: {", ".join(failed_files)}'
        else:
            message = f'Failed to delete any files: {", ".join(failed_files)}'

        return jsonify({
            'success': deleted_count > 0,
            'message': message
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error during bulk deletion: {str(e)}'}), 500

# CSV Export Functions
def export_medicines_to_csv(medicines, csv_path):
    """Export medicines to CSV"""
    import csv
    fieldnames = ['id', 'name', 'supplier_id', 'category', 'form_dosage', 'strength',
                 'low_stock_limit', 'unit_price', 'notes', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in medicines:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)

def export_patients_to_csv(patients, csv_path):
    """Export patients to CSV"""
    import csv
    fieldnames = ['id', 'name', 'age', 'gender', 'phone', 'address',
                 'medical_history', 'allergies', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in patients:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)

def export_suppliers_to_csv(suppliers, csv_path):
    """Export suppliers to CSV"""
    import csv
    fieldnames = ['id', 'name', 'contact_person', 'phone', 'email',
                 'address', 'city', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in suppliers:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)

def export_departments_to_csv(departments, csv_path):
    """Export departments to CSV"""
    import csv
    fieldnames = ['id', 'name', 'description', 'responsible_person',
                 'telephone', 'notes', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in departments:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)

def export_doctors_to_csv(doctors, csv_path):
    """Export doctors to CSV"""
    import csv
    fieldnames = ['id', 'dr_name', 'gender', 'nationality', 'department_id', 'specialist',
                 'position', 'type', 'mobile_no', 'email', 'license_number', 'note',
                 'created_at', 'updated_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in doctors:
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)

def export_stores_to_csv(stores, csv_path):
    """Export stores to CSV"""
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Store ID', 'Store Name', 'Department ID', 'Location',
                       'Description', 'Medicine ID', 'Medicine Stock', 'Created At'])

        for store in stores:
            inventory = store.get('inventory', {})
            if inventory:
                for med_id, stock in inventory.items():
                    writer.writerow([
                        store.get('id', ''),
                        store.get('name', ''),
                        store.get('department_id', ''),
                        store.get('location', ''),
                        store.get('description', ''),
                        med_id,
                        stock,
                        store.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    store.get('id', ''),
                    store.get('name', ''),
                    store.get('department_id', ''),
                    store.get('location', ''),
                    store.get('description', ''),
                    '', '',
                    store.get('created_at', '')
                ])

def export_purchases_to_csv(purchases, csv_path):
    """Export purchases to CSV"""
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Purchase ID', 'Supplier ID', 'Invoice Number', 'Purchase Date',
                       'Medicine ID', 'Quantity', 'Status', 'Notes', 'Created At'])

        for purchase in purchases:
            medicines = purchase.get('medicines', [])
            if medicines:
                for med in medicines:
                    writer.writerow([
                        purchase.get('id', ''),
                        purchase.get('supplier_id', ''),
                        purchase.get('invoice_number', ''),
                        purchase.get('date', ''),
                        med.get('medicine_id', ''),
                        med.get('quantity', ''),
                        purchase.get('status', ''),
                        purchase.get('notes', ''),
                        purchase.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    purchase.get('id', ''),
                    purchase.get('supplier_id', ''),
                    purchase.get('invoice_number', ''),
                    purchase.get('date', ''),
                    '', '',
                    purchase.get('status', ''),
                    purchase.get('notes', ''),
                    purchase.get('created_at', '')
                ])

def export_consumption_to_csv(consumption, csv_path):
    """Export consumption to CSV"""
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Consumption ID', 'Patient ID', 'Date', 'Medicine ID',
                       'Quantity', 'Prescribed By', 'Notes', 'Created At'])

        for consumption_record in consumption:
            medicines = consumption_record.get('medicines', [])
            if medicines:
                for med in medicines:
                    writer.writerow([
                        consumption_record.get('id', ''),
                        consumption_record.get('patient_id', ''),
                        consumption_record.get('date', ''),
                        med.get('medicine_id', ''),
                        med.get('quantity', ''),
                        consumption_record.get('prescribed_by', ''),
                        consumption_record.get('notes', ''),
                        consumption_record.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    consumption_record.get('id', ''),
                    consumption_record.get('patient_id', ''),
                    consumption_record.get('date', ''),
                    '', '',
                    consumption_record.get('prescribed_by', ''),
                    consumption_record.get('notes', ''),
                    consumption_record.get('created_at', '')
                ])

def export_transfers_to_csv(transfers, csv_path):
    """Export transfers to CSV"""
    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Transfer ID', 'Source Store ID', 'Destination Store ID',
                       'Medicine ID', 'Quantity', 'Transfer Date', 'Status',
                       'Notes', 'Created At'])

        for transfer in transfers:
            medicines = transfer.get('medicines', [])
            if medicines:
                for med in medicines:
                    writer.writerow([
                        transfer.get('id', ''),
                        transfer.get('source_store_id', ''),
                        transfer.get('destination_store_id', ''),
                        med.get('medicine_id', ''),
                        med.get('quantity', ''),
                        transfer.get('transfer_date', ''),
                        transfer.get('status', ''),
                        transfer.get('notes', ''),
                        transfer.get('created_at', '')
                    ])
            else:
                writer.writerow([
                    transfer.get('id', ''),
                    transfer.get('source_store_id', ''),
                    transfer.get('destination_store_id', ''),
                    '', '',
                    transfer.get('transfer_date', ''),
                    transfer.get('status', ''),
                    transfer.get('notes', ''),
                    transfer.get('created_at', '')
                ])

def export_users_to_csv(users, csv_path):
    """Export users to CSV (without passwords)"""
    import csv
    fieldnames = ['id', 'username', 'role', 'name', 'email',
                 'department_id', 'created_at']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in users:
            # Exclude password for security
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)

def export_history_to_csv(history, csv_path):
    """Export history to CSV"""
    import csv
    fieldnames = ['id', 'action', 'entity_type', 'entity_id', 'user_id',
                 'username', 'timestamp', 'details']

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for record in history:
            # Convert details dict to string if needed
            if 'details' in record and isinstance(record['details'], dict):
                record = record.copy()  # Don't modify original
                record['details'] = json.dumps(record['details'])
            filtered_record = {k: v for k, v in record.items() if k in fieldnames}
            writer.writerow(filtered_record)
