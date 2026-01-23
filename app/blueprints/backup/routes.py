"""
Backup Blueprint Routes

Backup and restore routes extracted from settings blueprint.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, jsonify, session
from app.utils.decorators import admin_required
from app.utils.database import (
    load_data, save_data, DB_FILES, log_activity,
    get_medicines, get_patients, get_suppliers, get_departments,
    get_stores, get_purchases, get_consumption, get_history, get_users
)
from .handlers import export_all_data_to_csv
import os
import zipfile
import json
import tempfile
import csv
import io
from datetime import datetime
from werkzeug.utils import secure_filename

backup_bp = Blueprint('backup', __name__)


@backup_bp.route('/full')
@admin_required
def backup_full():
    """Create and download full system backup as CSV ZIP"""
    try:
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


@backup_bp.route('/file/<file_type>')
@admin_required
def backup_file(file_type):
    """Download individual data file as CSV"""
    try:
        from .handlers import (
            export_medicines_to_csv, export_patients_to_csv,
            export_suppliers_to_csv, export_departments_to_csv,
            export_doctors_to_csv, export_stores_to_csv,
            export_purchases_to_csv, export_consumption_to_csv,
            export_transfers_to_csv, export_users_to_csv,
            export_history_to_csv
        )

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


@backup_bp.route('/restore', methods=['GET', 'POST'])
@admin_required
def restore():
    """Restore system from backup"""
    if request.method == 'POST':
        try:
            if 'backup_file' not in request.files:
                flash('No backup file selected.', 'error')
                return redirect(url_for('backup.restore'))

            file = request.files['backup_file']
            if file.filename == '':
                flash('No backup file selected.', 'error')
                return redirect(url_for('backup.restore'))

            if not file.filename.endswith('.zip'):
                flash('Please upload a ZIP backup file.', 'error')
                return redirect(url_for('backup.restore'))

            # Save uploaded file
            from app.utils.database import DATA_DIR
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
            return redirect(url_for('backup.restore'))

    return render_template('backup/restore.html')


@backup_bp.route('/list')
@admin_required
def list_backups():
    """Get list of all backup records"""
    try:
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
            'last_auto_backup': 'Never',
            'next_scheduled': 'Not configured'
        }

        return jsonify({
            'success': True,
            'backups': backups,
            'stats': stats
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error loading backup records: {str(e)}'}), 500


@backup_bp.route('/delete/<filename>', methods=['DELETE'])
@admin_required
def delete_backup(filename):
    """Delete a single backup file"""
    try:
        backup_path = os.path.join('backups', filename)

        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Backup file not found'}), 404

        # Delete the file
        os.remove(backup_path)

        # Log the deletion
        log_activity(
            'delete_backup',
            'system',
            details={'filename': filename}
        )

        return jsonify({
            'success': True,
            'message': f'Backup {filename} deleted successfully'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting backup: {str(e)}'}), 500


@backup_bp.route('/bulk-delete', methods=['POST'])
@admin_required
def delete_backups_bulk():
    """Delete multiple backup files"""
    try:
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
            'delete_backups_bulk',
            'system',
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


@backup_bp.route('/download/<filename>')
@admin_required
def download_backup(filename):
    """Download a backup file"""
    try:
        backup_path = os.path.join('backups', filename)

        if not os.path.exists(backup_path):
            return jsonify({'success': False, 'message': 'Backup file not found'}), 404

        # Log the download
        log_activity(
            'download_backup',
            'system',
            details={'filename': filename}
        )

        return send_file(backup_path, as_attachment=True, download_name=filename)

    except Exception as e:
        return jsonify({'success': False, 'message': f'Error downloading backup: {str(e)}'}), 500
