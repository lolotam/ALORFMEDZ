"""
Store Repository Module
Store management functions
"""

from datetime import datetime
from typing import List, Dict, Optional

from .base import load_data, save_data, generate_id, renumber_ids, cascade_update_store_references


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
                from .transfers import get_transfers
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
    from .departments import get_departments
    from .users import delete_department_users
    from .activity import log_activity

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


def update_main_store_inventory(medicines: list, operation: str):
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


__all__ = [
    'get_stores', 'get_store_by_id', 'update_store',
    'create_store_for_department', 'delete_store', 'delete_department_and_store',
    'update_main_store_inventory',
]
