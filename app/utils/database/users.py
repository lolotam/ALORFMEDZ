"""
User Repository Module
User management functions
"""

import secrets
import string
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

from .base import load_data, save_data, generate_id, renumber_ids, cascade_update_user_references
from .activity import log_activity


def get_users() -> List[Dict]:
    """Get all users"""
    return load_data('users')


def validate_user(username: str, password: str) -> Optional[Dict]:
    """Validate user credentials with enhanced security and audit logging"""
    users = get_users()

    # Log authentication attempt
    log_activity('AUTH_ATTEMPT', 'user', None, {
        'username': username,
        'timestamp': datetime.now().isoformat(),
        'ip_address': 'localhost'  # Could be enhanced with real IP
    })

    for user in users:
        if user.get('username') == username:
            # Check if account is locked
            if user.get('account_locked', False):
                log_activity('AUTH_FAILED', 'user', user.get('id'), {
                    'username': username,
                    'reason': 'account_locked',
                    'timestamp': datetime.now().isoformat()
                })
                return None

            # Check if password is hashed (new format) or plain text (legacy)
            stored_password = user.get('password', '')
            if stored_password.startswith('pbkdf2:sha256:'):
                # Hashed password - use secure check
                if check_password_hash(stored_password, password):
                    # Reset failed login attempts on successful login
                    if user.get('failed_login_attempts', 0) > 0:
                        update_user(user['id'], {
                            'failed_login_attempts': 0,
                            'last_successful_login': datetime.now().isoformat()
                        })

                    log_activity('AUTH_SUCCESS', 'user', user.get('id'), {
                        'username': username,
                        'timestamp': datetime.now().isoformat()
                    })
                    return user
                else:
                    # Handle failed login attempt
                    handle_failed_login(user)
                    return None
            else:
                # Plain text password - legacy support (should be migrated)
                if stored_password == password:
                    # Reset failed login attempts on successful login
                    if user.get('failed_login_attempts', 0) > 0:
                        update_user(user['id'], {
                            'failed_login_attempts': 0,
                            'last_successful_login': datetime.now().isoformat()
                        })

                    log_activity('AUTH_SUCCESS', 'user', user.get('id'), {
                        'username': username,
                        'timestamp': datetime.now().isoformat(),
                        'note': 'legacy_password_used'
                    })
                    return user
                else:
                    # Handle failed login attempt
                    handle_failed_login(user)
                    return None

    # User not found
    log_activity('AUTH_FAILED', 'user', None, {
        'username': username,
        'reason': 'user_not_found',
        'timestamp': datetime.now().isoformat()
    })
    return None


def handle_failed_login(user: Dict):
    """Handle failed login attempts with account locking"""
    user_id = user.get('id')
    failed_attempts = user.get('failed_login_attempts', 0) + 1
    max_attempts = 5  # Maximum failed attempts before locking

    update_data = {
        'failed_login_attempts': failed_attempts,
        'last_failed_login': datetime.now().isoformat()
    }

    # Lock account if max attempts reached
    if failed_attempts >= max_attempts:
        update_data['account_locked'] = True
        update_data['account_locked_at'] = datetime.now().isoformat()

        log_activity('ACCOUNT_LOCKED', 'user', user_id, {
            'username': user.get('username'),
            'failed_attempts': failed_attempts,
            'timestamp': datetime.now().isoformat()
        })
    else:
        log_activity('AUTH_FAILED', 'user', user_id, {
            'username': user.get('username'),
            'reason': 'invalid_password',
            'failed_attempts': failed_attempts,
            'timestamp': datetime.now().isoformat()
        })

    update_user(user_id, update_data)


def unlock_user_account(user_id: str):
    """Unlock a locked user account (admin only)"""
    update_user(user_id, {
        'account_locked': False,
        'failed_login_attempts': 0,
        'account_unlocked_at': datetime.now().isoformat()
    })

    user = get_user_by_id(user_id)
    log_activity('ACCOUNT_UNLOCKED', 'user', user_id, {
        'username': user.get('username') if user else 'unknown',
        'unlocked_by': session.get('username', 'system'),
        'timestamp': datetime.now().isoformat()
    })


def validate_password_strength(password: str) -> Dict[str, Any]:
    """Validate password strength and return detailed feedback"""
    result = {
        'is_valid': True,
        'score': 0,
        'feedback': [],
        'requirements_met': {
            'length': False,
            'uppercase': False,
            'lowercase': False,
            'digit': False,
            'special': False
        }
    }

    # Check length
    if len(password) >= 8:
        result['requirements_met']['length'] = True
        result['score'] += 20
    else:
        result['is_valid'] = False
        result['feedback'].append('Password must be at least 8 characters long')

    # Check for uppercase letter
    if any(c.isupper() for c in password):
        result['requirements_met']['uppercase'] = True
        result['score'] += 20
    else:
        result['is_valid'] = False
        result['feedback'].append('Password must contain at least one uppercase letter')

    # Check for lowercase letter
    if any(c.islower() for c in password):
        result['requirements_met']['lowercase'] = True
        result['score'] += 20
    else:
        result['is_valid'] = False
        result['feedback'].append('Password must contain at least one lowercase letter')

    # Check for digit
    if any(c.isdigit() for c in password):
        result['requirements_met']['digit'] = True
        result['score'] += 20
    else:
        result['is_valid'] = False
        result['feedback'].append('Password must contain at least one digit')

    # Check for special character
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        result['requirements_met']['special'] = True
        result['score'] += 20
    else:
        result['is_valid'] = False
        result['feedback'].append('Password must contain at least one special character')

    # Additional strength checks
    if len(password) >= 12:
        result['score'] += 10
    if len(set(password)) >= len(password) * 0.7:  # Character diversity
        result['score'] += 10

    return result


def generate_username(department_name: str) -> str:
    """Generate username for department user"""
    # Clean department name and create base username
    base_username = department_name.lower().replace(' ', '_').replace('-', '_')
    base_username = ''.join(c for c in base_username if c.isalnum() or c == '_')

    # Ensure it's not too long
    if len(base_username) > 15:
        base_username = base_username[:15]

    # Check if username exists and add number if needed
    users = get_users()
    existing_usernames = [u.get('username', '') for u in users]

    username = f"{base_username}_user"
    counter = 1
    while username in existing_usernames:
        username = f"{base_username}_user{counter}"
        counter += 1

    return username


def generate_secure_password(length: int = 12) -> str:
    """Generate a secure random password"""
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = "!@#$%^&*"

    # Ensure at least one character from each set
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]

    # Fill the rest with random characters from all sets
    all_chars = lowercase + uppercase + digits + special
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))

    # Shuffle the password list
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)


def save_user(user_data: Dict) -> str:
    """Save new user with enhanced security validation and password hashing"""
    users = get_users()

    # Validate required fields
    required_fields = ['username', 'password']
    for field in required_fields:
        if not user_data.get(field):
            raise ValueError(f"Field '{field}' is required")

    # Check for duplicate username
    existing_usernames = [u.get('username', '') for u in users]
    if user_data.get('username') in existing_usernames:
        raise ValueError(f"Username '{user_data.get('username')}' already exists")

    # Validate username format
    username = user_data.get('username', '')
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters long")
    if not username.replace('_', '').replace('-', '').isalnum():
        raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")

    # Validate password strength
    password = user_data.get('password', '')
    password_validation = validate_password_strength(password)
    if not password_validation['is_valid']:
        raise ValueError(f"Password validation failed: {'; '.join(password_validation['feedback'])}")

    # Generate user ID
    user_id = generate_id('users')
    user_data['id'] = user_id
    user_data['created_at'] = datetime.now().isoformat()

    # Hash password if it's not already hashed
    if 'password' in user_data and not user_data['password'].startswith('pbkdf2:sha256:'):
        user_data['password'] = generate_password_hash(user_data['password'])

    # Set default security values
    user_data.setdefault('role', 'department_user')
    user_data.setdefault('name', user_data.get('username', '').title())
    user_data.setdefault('email', f"{user_data.get('username', '')}@hospital.com")
    user_data.setdefault('failed_login_attempts', 0)
    user_data.setdefault('account_locked', False)
    user_data.setdefault('password_changed_at', datetime.now().isoformat())
    user_data.setdefault('must_change_password', False)

    users.append(user_data)
    save_data('users', users)

    # Log activity with enhanced details
    log_activity('CREATE', 'user', user_id, {
        'username': user_data.get('username'),
        'role': user_data.get('role'),
        'department_id': user_data.get('department_id'),
        'created_by': session.get('username', 'system'),
        'password_strength_score': password_validation['score']
    })

    return user_id


def update_user(user_id: str, user_data: Dict):
    """Update existing user with enhanced security validation"""
    users = get_users()
    user_found = False
    original_user = None

    for i, user in enumerate(users):
        if user['id'] == user_id:
            original_user = user.copy()

            # Validate username if being updated
            if 'username' in user_data:
                username = user_data['username']
                if len(username) < 3:
                    raise ValueError("Username must be at least 3 characters long")
                if not username.replace('_', '').replace('-', '').isalnum():
                    raise ValueError("Username can only contain letters, numbers, hyphens, and underscores")

                # Check for duplicate username (excluding current user)
                existing_usernames = [u.get('username', '') for u in users if u['id'] != user_id]
                if username in existing_usernames:
                    raise ValueError(f"Username '{username}' already exists")

            # Validate and hash password if provided
            if 'password' in user_data and user_data['password']:
                if not user_data['password'].startswith('pbkdf2:sha256:'):
                    # Validate password strength
                    password_validation = validate_password_strength(user_data['password'])
                    if not password_validation['is_valid']:
                        raise ValueError(f"Password validation failed: {'; '.join(password_validation['feedback'])}")

                    # Hash the password
                    user_data['password'] = generate_password_hash(user_data['password'])
                    user_data['password_changed_at'] = datetime.now().isoformat()
                    user_data['must_change_password'] = False

            # Update user data
            user_data['id'] = user_id
            user_data['updated_at'] = datetime.now().isoformat()
            users[i] = {**user, **user_data}
            user_found = True
            break

    if not user_found:
        raise ValueError(f"User with ID '{user_id}' not found")

    save_data('users', users)

    # Log activity with detailed changes
    changed_fields = []
    for key, new_value in user_data.items():
        if key in ['password', 'updated_at', 'id']:
            continue  # Don't log sensitive or automatic fields
        old_value = original_user.get(key)
        if old_value != new_value:
            changed_fields.append(key)

    log_activity('UPDATE', 'user', user_id, {
        'updated_fields': changed_fields,
        'username': user_data.get('username', original_user.get('username')),
        'updated_by': session.get('username', 'system'),
        'password_changed': 'password' in user_data
    })


def delete_user(user_id: str):
    """Delete user and renumber remaining records"""
    users = get_users()
    user_to_delete = next((u for u in users if u['id'] == user_id), None)

    if not user_to_delete:
        raise ValueError(f"User with ID '{user_id}' not found")

    # Prevent deletion of admin users if it's the last admin
    if user_to_delete.get('role') == 'admin':
        admin_count = len([u for u in users if u.get('role') == 'admin'])
        if admin_count <= 1:
            raise ValueError("Cannot delete the last admin user")

    # Remove user
    users = [u for u in users if u['id'] != user_id]
    save_data('users', users)

    # Log activity
    log_activity('DELETE', 'user', user_id, {
        'username': user_to_delete.get('username'),
        'role': user_to_delete.get('role')
    })

    # Renumber users and cascade update all references (protect default admin users)
    id_mapping = renumber_ids('users', protect_ids=['01', '02'])
    cascade_update_user_references(id_mapping)


def get_user_by_id(user_id: str) -> Optional[Dict]:
    """Get user by ID"""
    users = get_users()
    return next((u for u in users if u['id'] == user_id), None)


def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    users = get_users()
    return next((u for u in users if u.get('username') == username), None)


def get_users_by_department(department_id: str) -> List[Dict]:
    """Get all users for a specific department"""
    users = get_users()
    return [u for u in users if u.get('department_id') == department_id]


def create_department_user(department_id: str, department_name: str) -> Dict:
    """Create a user account for a new department"""
    # Generate username and password
    username = generate_username(department_name)
    password = generate_secure_password()

    # Create user data
    user_data = {
        'username': username,
        'password': password,  # Will be hashed in save_user
        'role': 'department_user',
        'name': f"{department_name} User",
        'email': f"{username}@hospital.com",
        'department_id': department_id
    }

    # Save user
    user_id = save_user(user_data)

    # Return user info including plain text password for admin display
    return {
        'user_id': user_id,
        'username': username,
        'password': password,  # Plain text for display
        'role': 'department_user',
        'department_id': department_id
    }


def delete_department_users(department_id: str):
    """Delete all users associated with a department"""
    users = get_users()
    department_users = [u for u in users if u.get('department_id') == department_id]

    deleted_users = []
    for user in department_users:
        try:
            delete_user(user['id'])
            deleted_users.append(user['username'])
        except ValueError as e:
            # Log error but continue with other users
            print(f"Error deleting user {user['username']}: {e}")

    return deleted_users


__all__ = [
    'get_users', 'validate_user', 'save_user', 'update_user', 'delete_user',
    'get_user_by_id', 'get_user_by_username', 'get_users_by_department',
    'handle_failed_login', 'unlock_user_account', 'validate_password_strength',
    'generate_username', 'generate_secure_password', 'create_department_user',
    'delete_department_users',
]
