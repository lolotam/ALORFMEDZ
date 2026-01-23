"""
Users Blueprint Routes

User management routes extracted from settings blueprint.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import admin_required
from app.utils.database import (
    get_users, get_departments, get_user_activity_summary, save_user,
    update_user, delete_user, get_user_by_id, generate_secure_password,
    create_department_user
)

users_bp = Blueprint('users', __name__)


@users_bp.route('/')
@admin_required
def index():
    """User management page (admin only)"""
    users = get_users()
    departments = get_departments()

    # Get activity summary for each user
    user_activities = {}
    for user in users:
        user_activities[user['id']] = get_user_activity_summary(user['id'])

    return render_template('users/index.html',
                         users=users,
                         departments=departments,
                         user_activities=user_activities)


@users_bp.route('/add', methods=['POST'])
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
            return redirect(url_for('users.index'))

        if not password:
            flash('Password is required!', 'error')
            return redirect(url_for('users.index'))

        if role == 'department_user' and not department_id:
            flash('Department is required for department users!', 'error')
            return redirect(url_for('users.index'))

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

    return redirect(url_for('users.index'))


@users_bp.route('/edit/<user_id>', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    """Edit user (admin only)"""
    user = get_user_by_id(user_id)
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('users.index'))

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
                return redirect(url_for('users.edit_user', user_id=user_id))

            if role == 'department_user' and not department_id:
                flash('Department is required for department users!', 'error')
                return redirect(url_for('users.edit_user', user_id=user_id))

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
            return redirect(url_for('users.index'))

        except ValueError as e:
            flash(str(e), 'error')
        except Exception as e:
            flash(f'Error updating user: {str(e)}', 'error')

    # GET request - show edit form
    departments = get_departments()
    return render_template('users/edit.html', user=user, departments=departments)


@users_bp.route('/delete/<user_id>', methods=['POST'])
@admin_required
def delete_user_route(user_id):
    """Delete user (admin only)"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('users.index'))

        username = user.get('username', 'Unknown')
        delete_user(user_id)
        flash(f'User "{username}" deleted successfully!', 'success')

    except ValueError as e:
        flash(str(e), 'error')
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')

    return redirect(url_for('users.index'))


@users_bp.route('/reset_password/<user_id>', methods=['POST'])
@admin_required
def reset_password(user_id):
    """Reset user password (admin only)"""
    try:
        user = get_user_by_id(user_id)
        if not user:
            flash('User not found!', 'error')
            return redirect(url_for('users.index'))

        # Generate new password
        new_password = generate_secure_password()

        # Update user password
        update_user(user_id, {'password': new_password})

        username = user.get('username', 'Unknown')
        flash(f'Password reset for "{username}". New password: {new_password}', 'success')
        flash('Please save this password and share it with the user.', 'warning')

    except Exception as e:
        flash(f'Error resetting password: {str(e)}', 'error')

    return redirect(url_for('users.index'))


@users_bp.route('/create_department_user/<department_id>', methods=['POST'])
@admin_required
def create_department_user(department_id):
    """Create additional department user for existing department"""
    try:
        departments = get_departments()
        department = next((d for d in departments if d['id'] == department_id), None)

        if not department:
            flash('Department not found!', 'error')
            return redirect(url_for('users.index'))

        # Create department user
        user_info = create_department_user(department_id, department['name'])

        flash(f'Department user created successfully!', 'success')
        flash(f'Username: {user_info["username"]}, Password: {user_info["password"]}', 'info')
        flash('Please save these credentials and share them with the department staff.', 'warning')

    except Exception as e:
        flash(f'Error creating department user: {str(e)}', 'error')

    return redirect(url_for('users.index'))
