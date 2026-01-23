"""
Department Repository Module
Department management functions
"""

from datetime import datetime
from typing import List, Dict

from .base import load_data, save_data, generate_id, renumber_ids, cascade_update_department_references
from .activity import log_activity
from .stores import create_store_for_department
from .users import create_department_user


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


__all__ = [
    'get_departments', 'save_department', 'save_department_with_user',
    'update_department', 'delete_department',
]
