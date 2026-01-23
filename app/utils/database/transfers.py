"""
Transfer Repository Module
Transfer management functions
"""

from datetime import datetime
from typing import List, Dict

from .base import load_data, save_data, generate_id, renumber_ids
from .medicines import get_medicines


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
    from .stores import get_stores
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


def delete_transfer(transfer_id: str):
    """Delete transfer and renumber remaining records"""
    transfers = get_transfers()
    transfers = [t for t in transfers if t['id'] != transfer_id]
    save_data('transfers', transfers)

    # Renumber transfers (no cascade needed)
    renumber_ids('transfers', protect_ids=[])


def update_transfer(transfer_id: str, transfer_data: Dict):
    """Update existing transfer"""
    transfers = get_transfers()
    for i, transfer in enumerate(transfers):
        if transfer['id'] == transfer_id:
            transfer_data['id'] = transfer_id
            transfer_data['updated_at'] = datetime.now().isoformat()
            transfers[i] = {**transfer, **transfer_data}
            break
    save_data('transfers', transfers)


__all__ = [
    'get_transfers', 'save_transfer', 'process_inventory_transfer',
    'get_medicine_name', 'delete_transfer', 'update_transfer',
]
