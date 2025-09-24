"""
Authentication Blueprint
Handles user login, logout, and session management
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from utils.database import get_users, validate_user, log_activity, get_user_activity_summary, get_departments, update_user, get_user_by_id, unlock_user_account
from werkzeug.security import generate_password_hash
from utils.helpers import login_required
from utils.upload import save_uploaded_photo, delete_photo, get_photo_info

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = validate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            session['department_id'] = user.get('department_id')

            # Log login activity
            log_activity('LOGIN', 'user', user['id'], {
                'username': user['username'],
                'role': user['role']
            })

            flash('Login successful!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    """User logout"""
    # Log logout activity before clearing session
    log_activity('LOGOUT', 'user', session.get('user_id'), {
        'username': session.get('username')
    })

    session.clear()
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile page"""
    if request.method == 'POST':
        # Restrict profile editing for department users
        if session.get('role') == 'department_user':
            flash('Department users cannot edit their profile information. Contact administrator if changes are needed.', 'error')
            return redirect(url_for('auth.profile'))

        # Only admin users can update profile
        if session.get('role') == 'admin':
            user_id = session.get('user_id')
            profile_data = {
                'name': request.form.get('name', '').strip(),
                'email': request.form.get('email', '').strip()
            }

            # Validate required fields
            if not profile_data['name']:
                flash('Full name is required.', 'error')
                return redirect(url_for('auth.profile'))

            try:
                update_user(user_id, profile_data)
                log_activity('UPDATE', 'user_profile', user_id, {
                    'action': 'profile_update'
                })
                flash('Profile updated successfully!', 'success')
            except Exception as e:
                flash(f'Error updating profile: {str(e)}', 'error')

        return redirect(url_for('auth.profile'))

    # GET request - display profile
    # Get user activity summary
    user_stats = get_user_activity_summary(session.get('user_id'))

    # Get user department info
    departments = get_departments()
    user_department = None
    if session.get('department_id'):
        user_department = next((d for d in departments if d['id'] == session.get('department_id')), None)

    # Get current user info for form population
    user_info = get_user_by_id(session.get('user_id')) or {}

    # Log profile view
    log_activity('VIEW', 'profile', session.get('user_id'))

    return render_template('auth/profile.html',
                         user_stats=user_stats,
                         user_department=user_department,
                         user_info=user_info)

@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Change user password"""
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Validate inputs
    if not all([current_password, new_password, confirm_password]):
        flash('All password fields are required.', 'error')
        return redirect(url_for('auth.profile'))

    if new_password != confirm_password:
        flash('New passwords do not match.', 'error')
        return redirect(url_for('auth.profile'))

    if len(new_password) < 6:
        flash('New password must be at least 6 characters long.', 'error')
        return redirect(url_for('auth.profile'))

    # Verify current password (simplified - in production use proper hashing)
    users = get_users()
    current_user = next((u for u in users if u['id'] == session.get('user_id')), None)

    if not current_user or current_user['password'] != current_password:
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.profile'))

    # Validate current password
    user_id = session.get('user_id')
    users = get_users()
    user = next((u for u in users if u['id'] == user_id), None)

    if not user or not validate_user(user.get('username'), current_password):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.profile'))

    # Update password with hashing
    try:
        update_user(user_id, {'password': new_password})
        log_activity('UPDATE', 'user_password', user_id, {
            'action': 'password_change'
        })
        flash('Password changed successfully!', 'success')
    except Exception as e:
        flash(f'Error changing password: {str(e)}', 'error')

    return redirect(url_for('auth.profile'))

@auth_bp.route('/migrate_passwords')
def migrate_passwords():
    """One-time migration to hash existing plain text passwords (admin only)"""
    if session.get('role') != 'admin':
        flash('Access denied!', 'error')
        return redirect(url_for('main.dashboard'))

    try:
        users = get_users()
        migrated_count = 0

        for user in users:
            password = user.get('password', '')
            # Check if password is already hashed
            if password and not password.startswith('pbkdf2:sha256:'):
                # Hash the plain text password
                hashed_password = generate_password_hash(password)
                update_user(user['id'], {'password': hashed_password})
                migrated_count += 1

        if migrated_count > 0:
            flash(f'Successfully migrated {migrated_count} user passwords to secure hashing!', 'success')
        else:
            flash('All user passwords are already using secure hashing.', 'info')

    except Exception as e:
        flash(f'Error during password migration: {str(e)}', 'error')

    return redirect(url_for('settings.users'))

@auth_bp.route('/unlock_account/<user_id>', methods=['POST'])
@login_required
def unlock_account(user_id):
    """Unlock a locked user account (admin only)"""
    if session.get('role') != 'admin':
        flash('Access denied! Admin privileges required.', 'error')
        return redirect(url_for('settings.users'))

    try:
        user = get_user_by_id(user_id)
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('settings.users'))

        if not user.get('account_locked', False):
            flash(f'User {user.get("username", "Unknown")} is not locked.', 'info')
            return redirect(url_for('settings.users'))

        unlock_user_account(user_id)
        flash(f'Successfully unlocked account for user {user.get("username", "Unknown")}.', 'success')

    except Exception as e:
        flash(f'Error unlocking account: {str(e)}', 'error')

    return redirect(url_for('settings.users'))

@auth_bp.route('/upload-profile-photo', methods=['POST'])
@login_required
def upload_profile_photo():
    """Upload profile photo for current user"""
    try:
        # Check if file was uploaded
        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': 'No photo file provided'}), 400

        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400

        # Use user ID as entity ID for profile photos
        user_id = session.get('user_id')

        # Delete existing profile photo if it exists
        existing_photos = []
        import os
        from utils.upload import UPLOAD_FOLDER
        profile_folder = os.path.join(UPLOAD_FOLDER, 'profiles')
        if os.path.exists(profile_folder):
            for filename in os.listdir(profile_folder):
                if filename.startswith(f"{user_id}_"):
                    photo_info = get_photo_info(filename, 'profiles')
                    if photo_info:
                        delete_photo(photo_info)

        # Save new profile photo
        photo_info = save_uploaded_photo(file, 'profiles', user_id)

        if photo_info:
            # Update user record with photo filename
            update_user(user_id, {'profile_photo': photo_info['filename']})

            # Log activity
            log_activity('UPDATE', 'user_profile_photo', user_id, {
                'action': 'profile_photo_upload',
                'filename': photo_info['filename']
            })

            return jsonify({
                'success': True,
                'message': 'Profile photo uploaded successfully',
                'photo_url': photo_info['url'],
                'thumbnail_url': photo_info.get('thumbnail_url')
            }), 200
        else:
            return jsonify({'success': False, 'message': 'Failed to upload photo'}), 400

    except ValueError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': f'Upload error: {str(e)}'}), 500
