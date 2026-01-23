"""
Supplier Repository Module
Supplier management functions
"""

from datetime import datetime
from typing import List, Dict

from .base import load_data, save_data, generate_id, renumber_ids, cascade_update_supplier_references


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


__all__ = [
    'get_suppliers', 'save_supplier', 'update_supplier', 'delete_supplier',
]
