"""
Base Repository Module
Core database utilities and functions
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

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
    # Import here to avoid circular dependencies
    from .departments import get_departments
    from .stores import get_stores
    from . import save_data

    # Check and create main department if missing
    departments = get_departments()
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
    stores = get_stores()
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

    from .medicines import get_medicines
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

    from .users import get_users
    from .stores import get_stores
    from .patients import get_patients
    from .consumption import get_consumption

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

    from .stores import get_stores
    from .purchases import get_purchases
    from .consumption import get_consumption
    from .transfers import get_transfers

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

    from .consumption import get_consumption
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

    from .transfers import get_transfers
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


def get_forms() -> List[Dict]:
    """Get all forms"""
    return load_data('forms')


__all__ = [
    'load_data', 'save_data', 'generate_id', 'renumber_ids',
    'ensure_main_entities', 'init_database',
    'cascade_update_medicine_references', 'cascade_update_patient_references',
    'cascade_update_supplier_references', 'cascade_update_department_references',
    'cascade_update_store_references', 'cascade_update_user_references',
    'log_history', 'get_forms',
]
