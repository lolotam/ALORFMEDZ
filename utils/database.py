"""
JSON Database Utilities
Handles all database operations using JSON files
"""

import json
import os
import secrets
import string
from datetime import datetime
from typing import List, Dict, Any, Optional
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash

# Database file paths
DATA_DIR = 'data'
DB_FILES = {
    'users': os.path.join(DATA_DIR, 'users.json'),
    'medicines': os.path.join(DATA_DIR, 'medicines.json'),
    'patients': os.path.join(DATA_DIR, 'patients.json'),
    'doctors': os.path.join(DATA_DIR, 'doctors.json'),
    'suppliers': os.path.join(DATA_DIR, 'suppliers.json'),
    'departments': os.path.join(DATA_DIR, 'departments.json'),
    'stores': os.path.join(DATA_DIR, 'stores.json'),
    'purchases': os.path.join(DATA_DIR, 'purchases.json'),
    'consumption': os.path.join(DATA_DIR, 'consumption.json'),
    'history': os.path.join(DATA_DIR, 'history.json'),
    'transfers': os.path.join(DATA_DIR, 'transfers.json'),
    'forms': os.path.join(DATA_DIR, 'forms.json')
}

def ensure_main_entities():
    """Ensure main department and main store always exist"""
    # Check and create main department if missing
    departments = load_data('departments')
    main_dept_exists = any(dept.get('id') == '01' for dept in departments)

    if not main_dept_exists:
        main_department = {
            'id': '01',
            'name': 'Main Pharmacy',
            'description': 'Main hospital pharmacy department',
            'responsible_person': 'Madam Tina',
            'telephone': '+1234567890',
            'notes': 'Main hospital pharmacy department - System Protected',
            'created_at': datetime.now().isoformat()
        }
        departments.append(main_department)
        save_data('departments', departments)
        print("Main department recreated")

    # Check and create main store if missing
    stores = load_data('stores')
    main_store_exists = any(store.get('id') == '01' for store in stores)

    if not main_store_exists:
        main_store = {
            'id': '01',
            'name': 'Main Pharmacy Store',
            'department_id': '01',
            'location': 'Main Building, Ground Floor',
            'description': 'Main pharmacy store - System Protected',
            'inventory': {},
            'created_at': datetime.now().isoformat()
        }
        stores.append(main_store)
        save_data('stores', stores)
        print("Main store recreated")

def init_database():
    """Initialize database with default data"""
    # Create data directory if it doesn't exist
    os.makedirs(DATA_DIR, exist_ok=True)

    # Initialize each database file with default data
    default_data = {
        'users': [
            {
                'id': '01',
                'username': 'admin',
                'password': '@Xx123456789xX@',  # In production, use hashed passwords
                'role': 'admin',
                'name': 'Administrator',
                'email': 'admin@hospital.com',
                'department_id': None,
                'created_at': datetime.now().isoformat()
            },
            {
                'id': '02',
                'username': 'pharmacy',
                'password': 'pharmacy123',
                'role': 'department_user',
                'name': 'Pharmacy User',
                'email': 'pharmacy@hospital.com',
                'department_id': '01',
                'created_at': datetime.now().isoformat()
            }
        ],
        'medicines': [],
        'patients': [],
        'doctors': [],
        'suppliers': [],
        'departments': [
            {
                'id': '01',
                'name': 'Main Pharmacy',
                'description': 'Main hospital pharmacy department',
                'responsible_person': 'Madam Tina',
                'telephone': '+1234567890',
                'notes': 'Main hospital pharmacy department - System Protected',
                'created_at': datetime.now().isoformat()
            }
        ],
        'stores': [
            {
                'id': '01',
                'name': 'Main Pharmacy Store',
                'department_id': '01',
                'location': 'Main Building, Ground Floor',
                'description': 'Main pharmacy store - System Protected',
                'inventory': {},  # {medicine_id: quantity}
                'created_at': datetime.now().isoformat()
            }
        ],
        'purchases': [],
        'consumption': [],
        'history': [],
        'transfers': [],
        'forms': []
    }
    
    # Create files if they don't exist
    for file_type, file_path in DB_FILES.items():
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump(default_data[file_type], f, indent=2)

    # Ensure main entities always exist
    ensure_main_entities()

def load_data(file_type: str) -> List[Dict]:
    """Load data from JSON file"""
    file_path = DB_FILES.get(file_type)
    if not file_path or not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def save_data(file_type: str, data: List[Dict]):
    """Save data to JSON file"""
    file_path = DB_FILES.get(file_type)
    if not file_path:
        return False
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

def generate_id(file_type: str) -> str:
    """Generate auto-increment ID"""
    data = load_data(file_type)
    if not data:
        return '01'
    
    # Find the highest ID and increment
    max_id = 0
    for item in data:
        try:
            current_id = int(item.get('id', '0'))
            max_id = max(max_id, current_id)
        except ValueError:
            continue
    
    return f"{max_id + 1:02d}"

def renumber_ids(file_type: str, protect_ids: List[str] = None) -> Dict[str, str]:
    """
    Renumber IDs sequentially after deletion to maintain 1, 2, 3, 4... sequence.

    Args:
        file_type: Type of data file (e.g., 'medicines', 'patients')
        protect_ids: List of IDs that should not be renumbered (e.g., ['01'] for main entities)

    Returns:
        Dictionary mapping old_id -> new_id for cascade updates
    """
    if protect_ids is None:
        protect_ids = []

    data = load_data(file_type)
    if not data:
        return {}

    # Create mapping of old IDs to new IDs
    id_mapping = {}
    new_id_counter = 1

    # Sort data by existing ID to maintain some order
    sorted_data = sorted(data, key=lambda x: int(x.get('id', '0')))

    for item in sorted_data:
        old_id = item.get('id')

        # Skip protected IDs - they keep their original ID
        if old_id in protect_ids:
            id_mapping[old_id] = old_id
            continue

        # Assign new sequential ID
        new_id = f"{new_id_counter:02d}"

        # Skip if new_id is protected (e.g., we're at 01 but 01 is protected)
        while new_id in protect_ids:
            new_id_counter += 1
            new_id = f"{new_id_counter:02d}"

        id_mapping[old_id] = new_id
        item['id'] = new_id
        new_id_counter += 1

    # Save renumbered data
    save_data(file_type, data)

    return id_mapping

def cascade_update_supplier_references(id_mapping: Dict[str, str]):
    """Update supplier_id references in medicines after supplier ID renumbering"""
    if not id_mapping:
        return

    medicines = get_medicines()
    updated = False

    for medicine in medicines:
        old_supplier_id = medicine.get('supplier_id')
        if old_supplier_id and old_supplier_id in id_mapping:
            medicine['supplier_id'] = id_mapping[old_supplier_id]
            updated = True

    if updated:
        save_data('medicines', medicines)

def cascade_update_department_references(id_mapping: Dict[str, str]):
    """Update department_id references after department ID renumbering"""
    if not id_mapping:
        return

    # Update users
    users = get_users()
    for user in users:
        old_dept_id = user.get('department_id')
        if old_dept_id and old_dept_id in id_mapping:
            user['department_id'] = id_mapping[old_dept_id]
    save_data('users', users)

    # Update stores
    stores = get_stores()
    for store in stores:
        old_dept_id = store.get('department_id')
        if old_dept_id and old_dept_id in id_mapping:
            store['department_id'] = id_mapping[old_dept_id]
    save_data('stores', stores)

    # Update patients
    patients = get_patients()
    for patient in patients:
        old_dept_id = patient.get('department_id')
        if old_dept_id and old_dept_id in id_mapping:
            patient['department_id'] = id_mapping[old_dept_id]
    save_data('patients', patients)

    # Update consumption records
    consumption = get_consumption()
    for record in consumption:
        old_dept_id = record.get('department_id')
        if old_dept_id and old_dept_id in id_mapping:
            record['department_id'] = id_mapping[old_dept_id]
    save_data('consumption', consumption)

def cascade_update_medicine_references(id_mapping: Dict[str, str]):
    """Update medicine_id references after medicine ID renumbering"""
    if not id_mapping:
        return

    # Update store inventories (keys are medicine IDs)
    stores = get_stores()
    for store in stores:
        if 'inventory' in store and store['inventory']:
            new_inventory = {}
            for old_med_id, quantity in store['inventory'].items():
                new_med_id = id_mapping.get(old_med_id, old_med_id)
                new_inventory[new_med_id] = quantity
            store['inventory'] = new_inventory
    save_data('stores', stores)

    # Update purchases
    purchases = get_purchases()
    for purchase in purchases:
        if 'medicines' in purchase:
            for medicine_item in purchase['medicines']:
                old_med_id = medicine_item.get('medicine_id')
                if old_med_id and old_med_id in id_mapping:
                    medicine_item['medicine_id'] = id_mapping[old_med_id]
    save_data('purchases', purchases)

    # Update consumption
    consumption = get_consumption()
    for record in consumption:
        if 'medicines' in record:
            for medicine_item in record['medicines']:
                old_med_id = medicine_item.get('medicine_id')
                if old_med_id and old_med_id in id_mapping:
                    medicine_item['medicine_id'] = id_mapping[old_med_id]
    save_data('consumption', consumption)

    # Update transfers
    transfers = get_transfers()
    for transfer in transfers:
        if 'medicines' in transfer:
            for medicine_item in transfer['medicines']:
                old_med_id = medicine_item.get('medicine_id')
                if old_med_id and old_med_id in id_mapping:
                    medicine_item['medicine_id'] = id_mapping[old_med_id]
    save_data('transfers', transfers)

def cascade_update_patient_references(id_mapping: Dict[str, str]):
    """Update patient_id references after patient ID renumbering"""
    if not id_mapping:
        return

    consumption = get_consumption()
    updated = False

    for record in consumption:
        old_patient_id = record.get('patient_id')
        if old_patient_id and old_patient_id in id_mapping:
            record['patient_id'] = id_mapping[old_patient_id]
            updated = True

    if updated:
        save_data('consumption', consumption)

def cascade_update_store_references(id_mapping: Dict[str, str]):
    """Update store_id references after store ID renumbering"""
    if not id_mapping:
        return

    transfers = get_transfers()
    updated = False

    for transfer in transfers:
        old_source_id = transfer.get('source_store_id')
        if old_source_id and old_source_id in id_mapping:
            transfer['source_store_id'] = id_mapping[old_source_id]
            updated = True

        old_dest_id = transfer.get('destination_store_id')
        if old_dest_id and old_dest_id in id_mapping:
            transfer['destination_store_id'] = id_mapping[old_dest_id]
            updated = True

    if updated:
        save_data('transfers', transfers)

def cascade_update_user_references(id_mapping: Dict[str, str]):
    """Update user_id references in history after user ID renumbering"""
    if not id_mapping:
        return

    history = load_data('history')
    updated = False

    for entry in history:
        old_user_id = entry.get('user_id')
        if old_user_id and old_user_id in id_mapping:
            entry['user_id'] = id_mapping[old_user_id]
            updated = True

        # Also update entity_id if it references a user
        if entry.get('entity_type') == 'user':
            old_entity_id = entry.get('entity_id')
            if old_entity_id and old_entity_id in id_mapping:
                entry['entity_id'] = id_mapping[old_entity_id]
                updated = True

    if updated:
        save_data('history', history)

def log_history(action: str, table: str, record_id: str, user_id: str, details: str = ''):
    """Log action to history"""
    history = load_data('history')
    history.append({
        'id': generate_id('history'),
        'action': action,
        'table': table,
        'record_id': record_id,
        'user_id': user_id,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })
    save_data('history', history)

# User Management Functions
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

# Medicine functions
def get_medicines() -> List[Dict]:
    """Get all medicines"""
    return load_data('medicines')

def save_medicine(medicine_data: Dict) -> str:
    """Save new medicine"""
    medicines = get_medicines()
    medicine_id = generate_id('medicines')
    medicine_data['id'] = medicine_id
    medicine_data['created_at'] = datetime.now().isoformat()
    medicines.append(medicine_data)
    save_data('medicines', medicines)
    return medicine_id

def update_medicine(medicine_id: str, medicine_data: Dict):
    """Update existing medicine"""
    medicines = get_medicines()
    for i, medicine in enumerate(medicines):
        if medicine['id'] == medicine_id:
            medicine_data['id'] = medicine_id
            medicine_data['updated_at'] = datetime.now().isoformat()
            medicines[i] = {**medicine, **medicine_data}
            break
    save_data('medicines', medicines)

def migrate_medicine_fields():
    """Migrate medicine records to ensure consistent field structure"""
    medicines = get_medicines()
    updated = False

    for i, medicine in enumerate(medicines):
        # Check if medicine has old field structure
        if 'description' in medicine and 'notes' not in medicine:
            medicine['notes'] = medicine.pop('description')
            updated = True

        # Ensure notes field exists
        if 'notes' not in medicine:
            medicine['notes'] = 'No notes available'
            updated = True

        # Convert old category/dosage/form structure to new format
        if 'category' in medicine and 'supplier_id' not in medicine:
            # Try to map category to a supplier_id (default to '01' if not found)
            medicine['supplier_id'] = '01'  # Default supplier
            medicine.pop('category', None)
            updated = True

        if 'dosage' in medicine and 'form' in medicine and 'form_dosage' not in medicine:
            medicine['form_dosage'] = f"{medicine.get('form', 'Tablet')} {medicine.get('dosage', '1 unit')}"
            medicine.pop('dosage', None)
            medicine.pop('form', None)
            updated = True

        if 'photos' not in medicine:
            medicine['photos'] = []
            updated = True

    if updated:
        save_data('medicines', medicines)
        return True
    return False

def delete_medicine(medicine_id: str, skip_renumber: bool = False):
    """Delete medicine and optionally renumber remaining records"""
    medicines = get_medicines()
    medicines = [m for m in medicines if m['id'] != medicine_id]
    save_data('medicines', medicines)

    # Renumber medicines and cascade update all references (unless skipped for bulk operations)
    if not skip_renumber:
        id_mapping = renumber_ids('medicines', protect_ids=[])
        cascade_update_medicine_references(id_mapping)

# Patient functions
def get_patients() -> List[Dict]:
    """Get all patients"""
    return load_data('patients')

def save_patient(patient_data: Dict) -> str:
    """Save new patient"""
    patients = get_patients()
    patient_id = generate_id('patients')
    patient_data['id'] = patient_id
    patient_data['created_at'] = datetime.now().isoformat()
    patients.append(patient_data)
    save_data('patients', patients)
    return patient_id

def update_patient(patient_id: str, patient_data: Dict):
    """Update existing patient"""
    patients = get_patients()
    for i, patient in enumerate(patients):
        if patient['id'] == patient_id:
            patient_data['id'] = patient_id
            patient_data['updated_at'] = datetime.now().isoformat()
            patients[i] = {**patient, **patient_data}
            break
    save_data('patients', patients)

def delete_patient(patient_id: str, skip_renumber: bool = False, cascade_delete: bool = True):
    """Delete patient and optionally renumber remaining records

    Args:
        patient_id: ID of the patient to delete
        skip_renumber: If True, skip renumbering (used in bulk operations)
        cascade_delete: If True, delete associated consumption records first (default: True)
    """
    # Step 1: Delete associated consumption records if cascade_delete is enabled
    if cascade_delete:
        consumption_records = get_consumption()
        # Filter out consumption records for this patient
        updated_consumption = [
            record for record in consumption_records
            if record.get('patient_id') != patient_id
        ]
        # Save updated consumption data
        if len(updated_consumption) < len(consumption_records):
            save_data('consumption', updated_consumption)

    # Step 2: Delete the patient record
    patients = get_patients()
    patients = [p for p in patients if p['id'] != patient_id]
    save_data('patients', patients)

    # Step 3: Renumber patients and cascade update all references (unless skipped for bulk operations)
    if not skip_renumber:
        id_mapping = renumber_ids('patients', protect_ids=[])
        cascade_update_patient_references(id_mapping)

# Supplier functions
def get_suppliers() -> List[Dict]:
    """Get all suppliers"""
    return load_data('suppliers')

def save_supplier(supplier_data: Dict) -> str:
    """Save new supplier"""
    suppliers = get_suppliers()
    supplier_id = generate_id('suppliers')
    supplier_data['id'] = supplier_id
    supplier_data['created_at'] = datetime.now().isoformat()
    suppliers.append(supplier_data)
    save_data('suppliers', suppliers)
    return supplier_id

def update_supplier(supplier_id: str, supplier_data: Dict):
    """Update existing supplier"""
    suppliers = get_suppliers()
    for i, supplier in enumerate(suppliers):
        if supplier['id'] == supplier_id:
            supplier_data['id'] = supplier_id
            supplier_data['updated_at'] = datetime.now().isoformat()
            suppliers[i] = {**supplier, **supplier_data}
            break
    save_data('suppliers', suppliers)

def delete_supplier(supplier_id: str, skip_renumber: bool = False):
    """Delete supplier and optionally renumber remaining records"""
    suppliers = get_suppliers()
    suppliers = [s for s in suppliers if s['id'] != supplier_id]
    save_data('suppliers', suppliers)

    # Renumber suppliers and cascade update all references (unless skipped for bulk operations)
    if not skip_renumber:
        id_mapping = renumber_ids('suppliers', protect_ids=[])
        cascade_update_supplier_references(id_mapping)

# Department functions
def get_departments() -> List[Dict]:
    """Get all departments"""
    return load_data('departments')

def save_department(department_data: Dict) -> str:
    """Save new department with automatic user creation"""
    departments = get_departments()
    department_id = generate_id('departments')
    department_data['id'] = department_id
    department_data['created_at'] = datetime.now().isoformat()
    departments.append(department_data)
    save_data('departments', departments)

    # Log department creation
    log_activity('CREATE', 'department', department_id, {
        'name': department_data.get('name'),
        'responsible_person': department_data.get('responsible_person')
    })

    return department_id

def save_department_with_user(department_data: Dict) -> Dict:
    """Save new department and automatically create department user"""
    # Save department first
    department_id = save_department(department_data)

    # Create store for department
    create_store_for_department(department_id, department_data['name'])

    # Create department user
    user_info = create_department_user(department_id, department_data['name'])

    return {
        'department_id': department_id,
        'user_info': user_info,
        'department_data': department_data
    }

def update_department(department_id: str, department_data: Dict):
    """Update existing department"""
    departments = get_departments()
    for i, department in enumerate(departments):
        if department['id'] == department_id:
            department_data['id'] = department_id
            department_data['updated_at'] = datetime.now().isoformat()
            departments[i] = {**department, **department_data}
            break
    save_data('departments', departments)

def delete_department(department_id: str, skip_renumber: bool = False):
    """Delete department and optionally renumber remaining records"""
    departments = get_departments()
    departments = [d for d in departments if d['id'] != department_id]
    save_data('departments', departments)

    # Renumber departments and cascade update all references (protect Main Pharmacy) (unless skipped for bulk operations)
    if not skip_renumber:
        id_mapping = renumber_ids('departments', protect_ids=['01'])
        cascade_update_department_references(id_mapping)

# Store functions
def get_stores() -> List[Dict]:
    """Get all stores"""
    return load_data('stores')

def get_store_by_id(store_id: str) -> Optional[Dict]:
    """Get store by ID"""
    stores = get_stores()
    return next((s for s in stores if s['id'] == store_id), None)

def update_store(store_id: str, store_data: Dict):
    """Update existing store"""
    stores = get_stores()
    for i, store in enumerate(stores):
        if store['id'] == store_id:
            store_data['id'] = store_id
            store_data['updated_at'] = datetime.now().isoformat()
            stores[i] = {**store, **store_data}
            break
    save_data('stores', stores)

def create_store_for_department(department_id: str, department_name: str) -> str:
    """Create store for department"""
    stores = get_stores()
    store_id = generate_id('stores')
    store_data = {
        'id': store_id,
        'name': f"{department_name} Store",
        'department_id': department_id,
        'inventory': {},
        'created_at': datetime.now().isoformat()
    }
    stores.append(store_data)
    save_data('stores', stores)
    return store_id

def delete_store(store_id: str):
    """Delete store and transfer inventory to main store"""
    stores = get_stores()
    store_to_delete = next((s for s in stores if s['id'] == store_id), None)

    if not store_to_delete:
        return False, "Store not found"

    # Prevent deletion of main store
    if store_id == '01':
        return False, "Cannot delete main store"

    # Transfer inventory to main store if any exists
    if store_to_delete.get('inventory'):
        main_store = next((s for s in stores if s['id'] == '01'), None)
        if main_store:
            # Create transfer record for audit trail
            transfer_data = {
                'source_store_id': store_id,
                'destination_store_id': '01',
                'medicines': [],
                'notes': f'Automatic transfer due to store deletion: {store_to_delete["name"]}',
                'status': 'completed',
                'created_at': datetime.now().isoformat()
            }

            # Transfer each medicine
            for medicine_id, quantity in store_to_delete['inventory'].items():
                if quantity > 0:
                    transfer_data['medicines'].append({
                        'medicine_id': medicine_id,
                        'quantity': quantity
                    })

                    # Add to main store inventory
                    current_stock = main_store['inventory'].get(medicine_id, 0)
                    main_store['inventory'][medicine_id] = current_stock + quantity

            # Save transfer record if there were medicines to transfer
            if transfer_data['medicines']:
                transfers = get_transfers()
                transfer_id = generate_id('transfers')
                transfer_data['id'] = transfer_id
                transfers.append(transfer_data)
                save_data('transfers', transfers)

    # Remove store from stores list
    stores = [s for s in stores if s['id'] != store_id]
    save_data('stores', stores)

    # Renumber stores and cascade update all references (protect Main Store)
    id_mapping = renumber_ids('stores', protect_ids=['01'])
    cascade_update_store_references(id_mapping)

    return True, "Store deleted successfully and inventory transferred to main store"

def delete_department_and_store(department_id: str):
    """Delete department, its associated store, and department users"""
    # Get department info for logging
    departments = get_departments()
    department_to_delete = next((d for d in departments if d['id'] == department_id), None)
    department_name = department_to_delete.get('name', 'Unknown') if department_to_delete else 'Unknown'

    # First delete associated users
    deleted_users = delete_department_users(department_id)

    # Then delete the associated store
    stores = get_stores()
    store_to_delete = next((s for s in stores if s.get('department_id') == department_id), None)

    if store_to_delete:
        success, message = delete_store(store_to_delete['id'])
        if not success:
            return False, f"Failed to delete store: {message}"

    # Finally delete the department
    departments = [d for d in departments if d['id'] != department_id]
    save_data('departments', departments)

    # Log department deletion
    log_activity('DELETE', 'department', department_id, {
        'name': department_name,
        'deleted_users': deleted_users,
        'store_deleted': store_to_delete is not None
    })

    user_message = f" and {len(deleted_users)} user(s)" if deleted_users else ""
    return True, f"Department '{department_name}', associated store{user_message} deleted successfully"

# Purchase functions
def get_purchases() -> List[Dict]:
    """Get all purchases"""
    return load_data('purchases')

def save_purchase(purchase_data: Dict) -> str:
    """Save new purchase and update inventory"""
    purchases = get_purchases()
    purchase_id = generate_id('purchases')
    purchase_data['id'] = purchase_id
    purchase_data['created_at'] = datetime.now().isoformat()
    purchases.append(purchase_data)
    save_data('purchases', purchases)

    # Update main store inventory
    update_main_store_inventory(purchase_data['medicines'], 'add')

    return purchase_id

def update_purchase(purchase_id: str, purchase_data: Dict):
    """Update existing purchase"""
    purchases = get_purchases()
    for i, purchase in enumerate(purchases):
        if purchase['id'] == purchase_id:
            purchase_data['id'] = purchase_id
            purchase_data['updated_at'] = datetime.now().isoformat()
            purchases[i] = {**purchase, **purchase_data}
            break
    save_data('purchases', purchases)

def delete_purchase(purchase_id: str):
    """Delete purchase and renumber remaining records"""
    purchases = get_purchases()
    purchases = [p for p in purchases if p['id'] != purchase_id]
    save_data('purchases', purchases)

    # Renumber purchases (no cascade needed - purchases don't have foreign keys referencing them)
    renumber_ids('purchases', protect_ids=[])

# Consumption functions
def get_consumption() -> List[Dict]:
    """Get all consumption records"""
    return load_data('consumption')

def save_consumption(consumption_data: Dict) -> str:
    """Save new consumption and update inventory"""
    consumption = get_consumption()
    consumption_id = generate_id('consumption')
    consumption_data['id'] = consumption_id
    consumption_data['created_at'] = datetime.now().isoformat()
    consumption.append(consumption_data)
    save_data('consumption', consumption)

    # Update store inventory (deduct)
    department_id = consumption_data.get('department_id')
    update_store_inventory(department_id, consumption_data['medicines'], 'subtract')

    return consumption_id

def update_consumption(consumption_id: str, consumption_data: Dict):
    """Update existing consumption"""
    consumption = get_consumption()
    for i, record in enumerate(consumption):
        if record['id'] == consumption_id:
            consumption_data['id'] = consumption_id
            consumption_data['updated_at'] = datetime.now().isoformat()
            consumption[i] = {**record, **consumption_data}
            break
    save_data('consumption', consumption)

def delete_consumption(consumption_id: str):
    """Delete consumption and renumber remaining records"""
    consumption = get_consumption()
    consumption = [c for c in consumption if c['id'] != consumption_id]
    save_data('consumption', consumption)

    # Renumber consumption (no cascade needed - consumption doesn't have foreign keys referencing it)
    renumber_ids('consumption', protect_ids=[])

def update_main_store_inventory(medicines: List[Dict], operation: str):
    """Update main store inventory (for purchases)"""
    stores = get_stores()
    main_store = next((s for s in stores if s['id'] == '01'), None)

    if main_store:
        for medicine in medicines:
            medicine_id = medicine['medicine_id']
            quantity = medicine['quantity']

            current_stock = main_store['inventory'].get(medicine_id, 0)

            if operation == 'add':
                main_store['inventory'][medicine_id] = current_stock + quantity
            elif operation == 'subtract':
                main_store['inventory'][medicine_id] = max(0, current_stock - quantity)

        save_data('stores', stores)

def update_store_inventory(department_id: str, medicines: List[Dict], operation: str):
    """Update specific store inventory"""
    stores = get_stores()
    store = next((s for s in stores if s['department_id'] == department_id), None)

    if store:
        for medicine in medicines:
            medicine_id = medicine['medicine_id']
            quantity = medicine['quantity']

            current_stock = store['inventory'].get(medicine_id, 0)

            if operation == 'add':
                store['inventory'][medicine_id] = current_stock + quantity
            elif operation == 'subtract':
                store['inventory'][medicine_id] = max(0, current_stock - quantity)

        save_data('stores', stores)

def get_medicine_stock(medicine_id: str, department_id: str = None) -> int:
    """Get current stock for a medicine in a specific store or all stores"""
    stores = get_stores()

    if department_id:
        # Get stock for specific department store
        store = next((s for s in stores if s.get('department_id') == department_id), None)
        if store:
            return store.get('inventory', {}).get(medicine_id, 0)
        return 0
    else:
        # Get total stock across all stores
        total_stock = 0
        for store in stores:
            total_stock += store.get('inventory', {}).get(medicine_id, 0)
        return total_stock

def get_low_stock_medicines(department_id: str = None) -> List[Dict]:
    """Get medicines that are at or below low stock limit"""
    medicines = get_medicines()
    stores = get_stores()
    low_stock_medicines = []

    for medicine in medicines:
        current_stock = get_medicine_stock(medicine['id'], department_id)
        if current_stock <= medicine.get('low_stock_limit', 0):
            low_stock_medicines.append({
                'medicine': medicine,
                'current_stock': current_stock,
                'low_stock_limit': medicine.get('low_stock_limit', 0)
            })

    return low_stock_medicines

def get_stock_status(medicine_id: str, department_id: str = None) -> Dict:
    """Get stock status for a medicine"""
    medicines = get_medicines()
    medicine = next((m for m in medicines if m['id'] == medicine_id), None)

    if not medicine:
        return {'status': 'unknown', 'color': 'secondary', 'message': 'Medicine not found'}

    current_stock = get_medicine_stock(medicine_id, department_id)
    low_limit = medicine.get('low_stock_limit', 0)

    if current_stock <= low_limit:
        return {'status': 'low', 'color': 'danger', 'message': 'Low Stock'}
    elif current_stock <= low_limit * 1.5:
        return {'status': 'medium', 'color': 'warning', 'message': 'Medium Stock'}
    else:
        return {'status': 'good', 'color': 'success', 'message': 'Good Stock'}

def validate_consumption_stock(medicines: List[Dict], department_id: str) -> Dict:
    """Validate if consumption is possible with current stock"""
    validation_result = {'valid': True, 'errors': []}

    for medicine_item in medicines:
        medicine_id = medicine_item['medicine_id']
        requested_qty = medicine_item['quantity']
        available_stock = get_medicine_stock(medicine_id, department_id)

        if requested_qty > available_stock:
            medicines_list = get_medicines()
            medicine = next((m for m in medicines_list if m['id'] == medicine_id), None)
            medicine_name = medicine['name'] if medicine else f'Medicine ID {medicine_id}'

            validation_result['valid'] = False
            validation_result['errors'].append(
                f'{medicine_name}: Requested {requested_qty}, but only {available_stock} available'
            )

    return validation_result

def log_activity(action: str, entity_type: str, entity_id: str = None, details: Dict = None):
    """Log user activity for audit trail"""
    try:
        history = load_data('history')

        log_entry = {
            'id': generate_id('history'),
            'timestamp': datetime.now().isoformat(),
            'user_id': session.get('user_id', 'system'),
            'username': session.get('username', 'system'),
            'role': session.get('role', 'system'),
            'department_id': session.get('department_id'),
            'action': action,  # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, VIEW
            'entity_type': entity_type,  # medicine, patient, supplier, etc.
            'entity_id': entity_id,
            'details': details or {},
            'ip_address': 'localhost',  # Could be enhanced with real IP
            'user_agent': 'Flask App'   # Could be enhanced with real user agent
        }

        history.append(log_entry)
        save_data('history', history)

    except Exception as e:
        # Don't let logging errors break the main functionality
        print(f"Logging error: {e}")

def get_history(limit: int = 100, user_id: str = None, entity_type: str = None) -> List[Dict]:
    """Get activity history with optional filtering"""
    history = load_data('history')

    # Apply filters
    if user_id:
        history = [h for h in history if h.get('user_id') == user_id]

    if entity_type:
        history = [h for h in history if h.get('entity_type') == entity_type]

    # Sort by timestamp (newest first) and limit
    history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

    return history[:limit]

def get_user_activity_summary(user_id: str) -> Dict:
    """Get activity summary for a specific user"""
    history = load_data('history')
    user_history = [h for h in history if h.get('user_id') == user_id]

    if not user_history:
        return {
            'total_actions': 0,
            'last_login': None,
            'most_common_action': None,
            'entities_modified': 0
        }

    # Count actions
    action_counts = {}
    entities = set()
    last_login = None

    for entry in user_history:
        action = entry.get('action', 'UNKNOWN')
        action_counts[action] = action_counts.get(action, 0) + 1

        if entry.get('entity_id'):
            entities.add(f"{entry.get('entity_type', '')}:{entry.get('entity_id', '')}")

        if action == 'LOGIN':
            if not last_login or entry.get('timestamp', '') > last_login:
                last_login = entry.get('timestamp')

    most_common_action = max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else None

    return {
        'total_actions': len(user_history),
        'last_login': last_login,
        'most_common_action': most_common_action,
        'entities_modified': len(entities),
        'action_breakdown': action_counts
    }

# Transfer functions
def get_transfers():
    """Get all inventory transfers"""
    return load_data('transfers')

def save_transfer(transfer_data):
    """Save a new inventory transfer"""
    transfers = load_data('transfers')
    transfer_data['id'] = generate_id('transfers')
    transfer_data['created_at'] = datetime.now().isoformat()
    transfers.append(transfer_data)
    save_data('transfers', transfers)
    return transfer_data['id']

def process_inventory_transfer(source_store_id, destination_store_id, medicines_data):
    """Process inventory transfer between stores"""
    stores = get_stores()

    # Find source and destination stores
    source_store = next((s for s in stores if s['id'] == source_store_id), None)
    destination_store = next((s for s in stores if s['id'] == destination_store_id), None)

    if not source_store or not destination_store:
        return False, "Source or destination store not found"

    # Validate sufficient stock in source store
    for medicine_data in medicines_data:
        medicine_id = medicine_data['medicine_id']
        quantity = int(medicine_data['quantity'])

        current_stock = source_store.get('inventory', {}).get(medicine_id, 0)
        if current_stock < quantity:
            medicine_name = get_medicine_name(medicine_id)
            return False, f"Insufficient stock for {medicine_name}. Available: {current_stock}, Requested: {quantity}"

    # Process the transfer
    for medicine_data in medicines_data:
        medicine_id = medicine_data['medicine_id']
        quantity = int(medicine_data['quantity'])

        # Deduct from source store
        if 'inventory' not in source_store:
            source_store['inventory'] = {}
        source_store['inventory'][medicine_id] = source_store['inventory'].get(medicine_id, 0) - quantity

        # Add to destination store
        if 'inventory' not in destination_store:
            destination_store['inventory'] = {}
        destination_store['inventory'][medicine_id] = destination_store['inventory'].get(medicine_id, 0) + quantity

    # Save updated stores
    save_data('stores', stores)

    return True, "Transfer completed successfully"

def get_medicine_name(medicine_id):
    """Get medicine name by ID"""
    medicines = get_medicines()
    medicine = next((m for m in medicines if m['id'] == medicine_id), None)
    return medicine['name'] if medicine else 'Unknown Medicine'

def get_forms() -> List[Dict]:
    """Get all forms"""
    return load_data('forms')
