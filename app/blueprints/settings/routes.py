"""
Settings Blueprint Routes (Refactored)

Settings dashboard now contains only the main settings dashboard, about, and history pages.
User management, backup, and security functionality have been moved to their own blueprints.
"""

from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from app.utils.decorators import login_required, admin_required
from app.utils.database import (
    get_medicines, get_patients, get_suppliers, get_departments,
    get_history, get_users, save_data, load_data, log_activity,
    update_history_record
)
from flask import jsonify

settings_bp = Blueprint('settings', __name__)


@settings_bp.route('/')
@login_required
def index():
    """Settings dashboard"""
    return render_template('settings/index.html')


@settings_bp.route('/about')
@login_required
def about():
    """About page - System statistics"""
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



@settings_bp.route('/history/edit-note', methods=['POST'])
@admin_required
def edit_history_note():
    """Edit note/details for a history record"""
    try:
        data = request.get_json()
        record_id = data.get('record_id')
        note = data.get('note')
        
        if not record_id:
            return jsonify({'success': False, 'message': 'Record ID is required'}), 400
            
        success = update_history_record(record_id, {'note': note})
        
        if success:
            log_activity(
                user_id=session.get('user_id'),
                action='UPDATE',
                entity_type='history',
                entity_id=record_id,
                details={'message': 'Updated history note'}
            )
            return jsonify({'success': True, 'message': 'Note updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Record not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error updating note: {str(e)}'}), 500


@settings_bp.route('/generate-sample-data')
@admin_required
def generate_sample_data():
    """Generate comprehensive sample data"""
    try:
        from app.utils.enhanced_sample_data import generate_enhanced_sample_data
        import os
        data_collections, zip_path = generate_enhanced_sample_data()

        # Count total records
        total_records = sum(len(data) for data in data_collections.values())

        flash(f'Enhanced sample data generated successfully! Created {total_records} records across all sections. Backup ZIP: {os.path.basename(zip_path)}', 'success')
    except Exception as e:
        flash(f'Sample data generation failed: {str(e)}', 'error')

    return redirect(url_for('settings.index'))
