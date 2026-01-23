"""
Medicine Repository Module
Medicine management functions
"""

from datetime import datetime
from typing import List, Dict

from .base import load_data, save_data, generate_id, renumber_ids, cascade_update_medicine_references


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


__all__ = [
    'get_medicines', 'save_medicine', 'update_medicine', 'delete_medicine',
    'migrate_medicine_fields',
]
