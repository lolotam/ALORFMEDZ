"""
Security Blueprint Routes

Security settings and audit routes extracted from settings blueprint.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from app.utils.decorators import admin_required
from app.utils.database import (
    get_history, save_data, load_data, log_activity, get_users,
    get_departments, get_stores, save_user, update_user, delete_user,
    get_user_by_id, DB_FILES, ensure_main_entities, init_database
)
from datetime import datetime
import csv
import io
import json
import os
import zipfile

security_bp = Blueprint('security', __name__)


@security_bp.route('/')
@admin_required
def index():
    """Security settings page"""
    # Get audit log stats
    audit_logs = get_history(limit=1000)

    stats = {
        'total_audit_logs': len(audit_logs),
        'recent_activities': len([log for log in audit_logs if
            (datetime.now() - datetime.fromisoformat(log.get('timestamp', '1970-01-01T00:00:00'))).days <= 7])
    }

    return render_template('security/index.html', **stats)


@security_bp.route('/audit-logs')
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

    return render_template('security/audit_logs.html',
                          logs=logs,
                          current_page=page,
                          total_pages=total_pages,
                          total_logs=len(all_logs))


@security_bp.route('/audit-logs/export')
@admin_required
def export_audit_logs():
    """Export audit logs as CSV"""
    try:
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
        return redirect(url_for('security.audit_logs'))


@security_bp.route('/erase-all-data', methods=['POST'])
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


@security_bp.route('/backup', methods=['POST'])
@admin_required
def create_backup():
    """Create a comprehensive backup of all data with CSV exports"""
    try:
        import tempfile
        from app.blueprints.backup.handlers import export_all_data_to_csv

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
